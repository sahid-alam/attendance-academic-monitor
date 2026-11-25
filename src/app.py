"""Online Student Attendance & Academic Monitoring System, demo app.
Tables and names follow schema.sql (AAM-20), the ER diagram and the data dictionary"""
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

HERE = Path(__file__).parent
EDIT_WINDOW = timedelta(hours=48)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)  # no fallback key in the repo
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # blocks cross-site form posts riding the session (CSRF)
app.config["DATABASE"] = os.environ.get("DATABASE", str(HERE / "attendance.db"))


class Locked(Exception):
    """Attendance is older than the 48 hour edit window. Changes go through the HOD"""


def get_db():
    if "db" not in g:
        g.db = connect(app.config["DATABASE"])
    return g.db


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db):
    db.executescript((HERE / "schema.sql").read_text())
    db.executescript((HERE / "seed_synthetic.sql").read_text())


@app.cli.command("init-db")
def init_db_command():
    """Recreate the tables and load the synthetic seed data"""
    init_db(get_db())
    print("database ready")


def utcnow():
    # CURRENT_TIMESTAMP in the schema is UTC, so the app uses UTC too
    return datetime.now(timezone.utc).replace(tzinfo=None)


def ts(dt):
    return dt.isoformat(sep=" ", timespec="seconds")


def audit(db, user_id, table, record_id, old, new, now):
    db.execute(
        """INSERT INTO audit_log (user_id, table_name, record_id, action, old_value, new_value, changed_at)
           VALUES (?, ?, ?, 'UPDATE', ?, ?, ?)""",
        (user_id, table, record_id, json.dumps(old), json.dumps(new), ts(now)),
    )


# --- attendance (AAM-28, DFD process 2.0) -----------------------------------

def attendance_pct(db, student_id, course_id):
    """(P + L) / sessions x 100 from v_attendance_pct, None if nothing recorded yet"""
    row = db.execute("SELECT attendance_pct FROM v_attendance_pct WHERE student_id = ? AND course_id = ?",
                     (student_id, course_id)).fetchone()
    return row["attendance_pct"] if row else None


def is_locked(cs, now=None):
    return (now or utcnow()) - datetime.fromisoformat(cs["submitted_at"]) > EDIT_WINDOW


def submit_attendance(db, section_id, session_date, period, faculty_id, statuses, now=None):
    """New session + its P/A/L list in one go. Raises sqlite3.IntegrityError if that date and period
    is already recorded (sequence diagram flow b). Returns (session_id, risk status changes)"""
    now = now or utcnow()
    cur = db.execute(
        """INSERT INTO class_sessions (section_id, session_date, period, created_by, submitted_at)
           VALUES (?, ?, ?, ?, ?)""",
        (section_id, session_date, period, faculty_id, ts(now)),
    )
    db.executemany(
        "INSERT INTO attendance_records (session_id, student_id, status, marked_at) VALUES (?, ?, ?, ?)",
        [(cur.lastrowid, sid, st, ts(now)) for sid, st in statuses.items()],
    )
    db.commit()
    course_id = db.execute("SELECT course_id FROM sections WHERE section_id = ?", (section_id,)).fetchone()[0]
    return cur.lastrowid, evaluate(db, statuses, course_id, now)


def edit_attendance(db, session_id, statuses, user_id, now=None):
    """Change a recorded session within 48 hours. Every changed entry goes to audit_log.
    Returns the risk status changes"""
    now = now or utcnow()
    cs = db.execute("SELECT * FROM class_sessions WHERE session_id = ?", (session_id,)).fetchone()
    if is_locked(cs, now):
        raise Locked()
    old = {r["student_id"]: r for r in db.execute(
        "SELECT * FROM attendance_records WHERE session_id = ?", (session_id,))}
    for sid, st in statuses.items():
        if sid not in old:
            db.execute("INSERT INTO attendance_records (session_id, student_id, status, marked_at) VALUES (?, ?, ?, ?)",
                       (session_id, sid, st, ts(now)))
        elif old[sid]["status"] != st:
            db.execute("UPDATE attendance_records SET status = ?, updated_at = ? WHERE record_id = ?",
                       (st, ts(now), old[sid]["record_id"]))
            audit(db, user_id, "attendance_records", old[sid]["record_id"],
                  {"status": old[sid]["status"]}, {"status": st}, now)
    db.commit()
    course_id = db.execute("SELECT course_id FROM sections WHERE section_id = ?", (cs["section_id"],)).fetchone()[0]
    return evaluate(db, statuses, course_id, now)


# --- marks (AAM-29, DFD process 3.0) ----------------------------------------

def save_marks(db, assessment_id, marks, user_id, now=None):
    """Save marks_obtained per student. Raises ValueError if any is outside 0..max_marks.
    Changing a mark that was already entered goes to audit_log. Returns the risk status changes"""
    now = now or utcnow()
    a = db.execute("SELECT * FROM assessments WHERE assessment_id = ?", (assessment_id,)).fetchone()
    if any(not 0 <= m <= a["max_marks"] for m in marks.values()):
        raise ValueError(f"marks must be between 0 and {a['max_marks']:g}")
    old = {r["student_id"]: r for r in db.execute(
        "SELECT * FROM mark_entries WHERE assessment_id = ?", (assessment_id,))}
    for sid, m in marks.items():
        if sid not in old:
            db.execute("INSERT INTO mark_entries (assessment_id, student_id, marks_obtained, entered_at) VALUES (?, ?, ?, ?)",
                       (assessment_id, sid, m, ts(now)))
        elif old[sid]["marks_obtained"] != m:
            db.execute("UPDATE mark_entries SET marks_obtained = ?, updated_at = ? WHERE mark_id = ?",
                       (m, ts(now), old[sid]["mark_id"]))
            audit(db, user_id, "mark_entries", old[sid]["mark_id"],
                  {"marks_obtained": old[sid]["marks_obtained"]}, {"marks_obtained": m}, now)
    db.commit()
    course_id = db.execute("SELECT course_id FROM sections WHERE section_id = ?", (a["section_id"],)).fetchone()[0]
    return evaluate(db, marks, course_id, now)


# --- risk rules (AAM-30, DFD process 4.0, sub-processes 4.1 to 4.4) ---------
# thresholds live in risk_rules, nothing is hardcoded here

RANK = {"NORMAL": 0, "WARNING": 1, "AT_RISK": 2}


def fires(rule, value):
    t, hi = rule["threshold"], rule["threshold_high"]
    return {"<": value < t, "<=": value <= t, ">=": value >= t,
            "BETWEEN": hi is not None and t <= value <= hi}[rule["operator"]]


def worst(fired):
    return max((r["severity"] for r, _ in fired), key=RANK.get, default="NORMAL")


def course_check(db, rules, student_id, course_id):
    """4.1 + 4.2: fetch attendance % and test % for one course, apply the rules. Returns [(rule, value)]"""
    # ponytail: test rules use the lowest test %, fine while every test rule is "<"
    tests = [r["test_pct"] for r in db.execute(
        "SELECT test_pct FROM v_test_pct WHERE student_id = ? AND course_id = ?", (student_id, course_id))]
    values = {"attendance_pct": attendance_pct(db, student_id, course_id), "test_pct": min(tests, default=None)}
    return [(r, values[r["metric"]]) for r in rules
            if r["metric"] in values and values[r["metric"]] is not None and fires(r, values[r["metric"]])]


def set_status(db, student_id, course_id, new, fired, now):
    """4.3: compare with the current flag and update it. Returns (old, new) if the status changed, else None"""
    cur = db.execute("SELECT * FROM risk_flags WHERE student_id = ? AND course_id IS ? AND is_current = 1",
                     (student_id, course_id)).fetchone()
    old = cur["status"] if cur else "NORMAL"
    if old == "UNDER_INTERVENTION":  # the mentor owns the case now, only a full recovery moves it on
        if new != "NORMAL":
            return None
        new = "RESOLVED"
    if new == old:
        return None
    if new == "RESOLVED":  # recovered on their own, so the mentor's open case is closed too
        db.execute("""UPDATE interventions SET status = 'CLOSED', closed_on = ?, outcome = 'Back within the thresholds'
                      WHERE flag_id = ? AND status = 'OPEN'""", (now.date().isoformat(), cur["flag_id"]))
    flag_id = move_flag(db, student_id, course_id, cur, new, [(r["rule_id"], v) for r, v in fired], now)
    alert(db, student_id, course_id, flag_id, old, new, fired, now)
    return old, new


def move_flag(db, student_id, course_id, cur, status, reasons, now):
    """Retire the current flag and add a new one with its reasons [(rule_id, value)]. Returns the new flag_id"""
    if cur:
        db.execute("UPDATE risk_flags SET is_current = 0, updated_on = ? WHERE flag_id = ?", (ts(now), cur["flag_id"]))
    flag_id = db.execute("INSERT INTO risk_flags (student_id, course_id, status, flagged_on) VALUES (?, ?, ?, ?)",
                         (student_id, course_id, status, ts(now))).lastrowid
    db.executemany("INSERT INTO risk_flag_reasons (flag_id, rule_id, actual_value) VALUES (?, ?, ?)",
                   [(flag_id, *r) for r in reasons])
    return flag_id


# --- mentor interventions (FR11): Warning/At-Risk -> Under Intervention -> Resolved ---

ACTIONS = ("Counselling", "Remedial class", "Parent meeting", "Other")


def open_case(db, flag_id, mentor_id, action, notes, now=None):
    """Mentor opens a case on a current At-Risk flag (state diagram: At-Risk -> Under Intervention).
    Returns the intervention_id"""
    now = now or utcnow()
    if action not in ACTIONS:
        raise ValueError("pick an action from the list")
    cur = db.execute("SELECT * FROM risk_flags WHERE flag_id = ? AND is_current = 1", (flag_id,)).fetchone()
    if cur is None or cur["status"] != "AT_RISK":
        raise ValueError("a case can only be opened on a current At-Risk flag")
    reasons = db.execute("SELECT rule_id, actual_value FROM risk_flag_reasons WHERE flag_id = ?", (flag_id,)).fetchall()
    new_id = move_flag(db, cur["student_id"], cur["course_id"], cur, "UNDER_INTERVENTION", [tuple(r) for r in reasons], now)
    iid = db.execute("INSERT INTO interventions (flag_id, mentor_id, action, notes, opened_on) VALUES (?, ?, ?, ?, ?)",
                     (new_id, mentor_id, action, notes, now.date().isoformat())).lastrowid
    db.commit()
    return iid


def close_case(db, intervention_id, outcome, now=None):
    """Mentor closes an open case: the case is CLOSED and the student's flag becomes RESOLVED.
    The next attendance or marks entry runs the rules again: Normal if nothing fires, else flagged again"""
    now = now or utcnow()
    case = db.execute("SELECT * FROM interventions WHERE intervention_id = ? AND status = 'OPEN'",
                      (intervention_id,)).fetchone()
    if case is None:
        raise ValueError("case is not open")
    cur = db.execute("SELECT * FROM risk_flags WHERE flag_id = ?", (case["flag_id"],)).fetchone()
    db.execute("UPDATE interventions SET status = 'CLOSED', closed_on = ?, outcome = ? WHERE intervention_id = ?",
               (now.date().isoformat(), outcome, intervention_id))
    if cur["is_current"]:
        move_flag(db, cur["student_id"], cur["course_id"], cur, "RESOLVED", [], now)
    db.commit()


def alert(db, student_id, course_id, flag_id, old, new, fired, now):
    """4.4 -> 5.0: tell the mentor and the student. In-app only for the demo, email (SMTP) is not built"""
    s = db.execute(
        """SELECT s.roll_no, s.user_id, u.full_name, f.user_id AS mentor_user_id FROM students s
           JOIN users u ON u.user_id = s.user_id LEFT JOIN faculty f ON f.faculty_id = s.mentor_id
           WHERE s.student_id = ?""", (student_id,)).fetchone()
    where = db.execute("SELECT course_code FROM courses WHERE course_id = ?", (course_id,)).fetchone()
    where = where["course_code"] if where else "2 or more courses"
    why = "; ".join(f"{r['rule_name']} ({v:g})" for r, v in fired) or "back within the thresholds"
    label = lambda st: st.replace("_", " ").title()
    msgs = [(s["mentor_user_id"], f"{s['full_name']} ({s['roll_no']}) is now {label(new)} in {where}, was {label(old)}: {why}"),
            # supportive wording for the student, no "at risk" label (ethics, Stage 6)
            (s["user_id"], f"Your status in {where} changed. Your mentor will get in touch if you need support"
                           if RANK.get(new, 0) else f"Your status in {where} is back to normal")]
    db.executemany(
        """INSERT INTO notifications (recipient_id, flag_id, channel, message, status, attempts, created_at, sent_at)
           VALUES (?, ?, 'IN_APP', ?, 'SENT', 1, ?, ?)""",
        [(uid, flag_id, m, ts(now), ts(now)) for uid, m in msgs if uid])


def evaluate(db, student_ids, course_id, now=None):
    """Run the risk rules for these students after an attendance or marks change.
    Returns [(student_id, old, new)] for every status that changed"""
    now = now or utcnow()
    rules = db.execute("SELECT * FROM risk_rules WHERE is_active = 1").fetchall()
    multi = [r for r in rules if r["metric"] == "courses_below_cutoff"]
    changes = []
    for sid in student_ids:
        fired = course_check(db, rules, sid, course_id)
        if ch := set_status(db, sid, course_id, worst(fired), fired, now):
            changes.append((sid, *ch))
        if multi:  # the "2 or more courses" rule, stored with course_id NULL
            courses = [r["course_id"] for r in db.execute(
                """SELECT DISTINCT sec.course_id FROM enrollments e JOIN sections sec USING (section_id)
                   WHERE e.student_id = ?""", (sid,))]
            # a course counts when any attendance or test rule fires there, Warning or At-Risk (data dictionary 6)
            n = sum(bool(course_check(db, rules, sid, c)) for c in courses)
            fired_multi = [(r, n) for r in multi if fires(r, n)]
            if ch := set_status(db, sid, None, worst(fired_multi), fired_multi, now):
                changes.append((sid, *ch))
    db.commit()
    return changes


def newly_flagged(changes):
    return len({sid for sid, old, new in changes if RANK.get(new, 0) > RANK.get(old, 0)})


# --- pages ------------------------------------------------------------------
# ponytail: "act as faculty" picker instead of real login. Swap for login + bcrypt when auth is built

def me():
    """The faculty member picked on the home page"""
    fid = session.get("faculty_id")
    return get_db().execute(
        "SELECT f.faculty_id, f.user_id, u.full_name FROM faculty f JOIN users u USING (user_id) WHERE f.faculty_id = ?",
        (fid,)).fetchone() if fid else None


def section_for_faculty(section_id):
    sec = get_db().execute(
        """SELECT sec.*, c.course_code, c.course_name FROM sections sec JOIN courses c USING (course_id)
           WHERE sec.section_id = ?""", (section_id,)).fetchone()
    if sec is None:
        abort(404)
    if sec["faculty_id"] != session.get("faculty_id"):
        abort(403)  # sequence diagram flow (a): faculty doesnt teach this section
    return sec


def section_students(section_id):
    return get_db().execute(
        """SELECT s.student_id, s.roll_no, u.full_name FROM enrollments e
           JOIN students s USING (student_id) JOIN users u ON u.user_id = s.user_id
           WHERE e.section_id = ? ORDER BY s.roll_no""", (section_id,)).fetchall()


def read_statuses(students):
    statuses = {s["student_id"]: request.form.get(f"s{s['student_id']}") for s in students}
    return statuses if all(st in ("P", "A", "L") for st in statuses.values()) else None


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        session["faculty_id"] = int(request.form["faculty_id"])
        return redirect(url_for("index"))
    faculty = db.execute(
        "SELECT f.faculty_id, u.full_name, u.role FROM faculty f JOIN users u USING (user_id) ORDER BY f.faculty_id"
    ).fetchall()
    sections = db.execute(
        """SELECT sec.*, c.course_code, c.course_name FROM sections sec JOIN courses c USING (course_id)
           WHERE sec.faculty_id = ?""", (session.get("faculty_id"),)).fetchall()
    who = me()
    notes = db.execute("SELECT * FROM notifications WHERE recipient_id = ? ORDER BY notification_id DESC LIMIT 20",
                       (who["user_id"],)).fetchall() if who else []
    # mentees who need attention, with the reasons and the open case if there is one
    mentees = db.execute(
        """SELECT rf.flag_id, rf.status, s.roll_no, u.full_name, COALESCE(c.course_code, '2 or more courses') AS course,
                  (SELECT GROUP_CONCAT(rr.rule_name || ' (' || rfr.actual_value || ')', '; ')
                     FROM risk_flag_reasons rfr JOIN risk_rules rr USING (rule_id) WHERE rfr.flag_id = rf.flag_id) AS why,
                  i.intervention_id, i.action, i.notes, i.opened_on
           FROM risk_flags rf JOIN students s USING (student_id) JOIN users u ON u.user_id = s.user_id
           LEFT JOIN courses c ON c.course_id = rf.course_id
           LEFT JOIN interventions i ON i.flag_id = rf.flag_id AND i.status = 'OPEN'
           WHERE s.mentor_id = ? AND rf.is_current = 1 AND rf.status IN ('WARNING', 'AT_RISK', 'UNDER_INTERVENTION')
           ORDER BY s.roll_no, rf.course_id""", (session.get("faculty_id"),)).fetchall()
    return render_template("index.html", faculty=faculty, sections=sections, me=who, notes=notes, mentees=mentees,
                           actions=ACTIONS)


def my_mentee_flag(flag_id):
    """403 unless the picked faculty is this student's mentor"""
    row = get_db().execute("SELECT s.mentor_id FROM risk_flags rf JOIN students s USING (student_id) WHERE rf.flag_id = ?",
                           (flag_id,)).fetchone()
    if row is None:
        abort(404)
    if row["mentor_id"] != session.get("faculty_id"):
        abort(403)


@app.post("/flag/<int:flag_id>/case")
def open_case_page(flag_id):
    my_mentee_flag(flag_id)
    try:
        open_case(get_db(), flag_id, session["faculty_id"], request.form["action"], request.form.get("notes", "").strip())
    except ValueError as e:
        flash(str(e), "danger")
    else:
        flash("case opened, status is now Under Intervention", "success")
    return redirect(url_for("index"))


@app.post("/case/<int:intervention_id>/close")
def close_case_page(intervention_id):
    case = get_db().execute("SELECT flag_id FROM interventions WHERE intervention_id = ?", (intervention_id,)).fetchone()
    if case is None:
        abort(404)
    my_mentee_flag(case["flag_id"])
    try:
        close_case(get_db(), intervention_id, request.form.get("outcome", "").strip() or None)
    except ValueError as e:
        flash(str(e), "danger")
    else:
        flash("case closed, status is now Resolved", "success")
    return redirect(url_for("index"))


@app.route("/section/<int:section_id>")
def section(section_id):
    sec = section_for_faculty(section_id)
    db = get_db()
    students = []
    for s in section_students(section_id):
        test = db.execute("SELECT MIN(test_pct) FROM v_test_pct WHERE student_id = ? AND course_id = ?",
                          (s["student_id"], sec["course_id"])).fetchone()[0]
        # no risk status here: only the student, mentor and HOD see that label (ethics, Stage 6)
        students.append(dict(s, pct=attendance_pct(db, s["student_id"], sec["course_id"]), test=test))
    assessments = db.execute("SELECT * FROM assessments WHERE section_id = ? ORDER BY assessment_id",
                             (section_id,)).fetchall()
    sessions = db.execute(
        "SELECT * FROM class_sessions WHERE section_id = ? ORDER BY session_date DESC, period DESC",
        (section_id,)).fetchall()
    return render_template("section.html", sec=sec, students=students, sessions=sessions, assessments=assessments,
                           today=datetime.now().date().isoformat())


@app.route("/section/<int:section_id>/attendance", methods=["GET", "POST"])
def take_attendance(section_id):
    sec = section_for_faculty(section_id)
    db = get_db()
    src = request.form if request.method == "POST" else request.args
    session_date, period = src.get("session_date"), src.get("period", type=int)
    if not session_date or not period:
        abort(400)
    existing = db.execute(
        "SELECT session_id FROM class_sessions WHERE section_id = ? AND session_date = ? AND period = ?",
        (section_id, session_date, period)).fetchone()
    if existing:  # flow (b): already recorded, offer the edit page instead
        flash("attendance for this class is already recorded, you can edit it here", "info")
        return redirect(url_for("edit_session", session_id=existing["session_id"]))
    students = section_students(section_id)

    if request.method == "POST":
        statuses = read_statuses(students)
        if statuses is None:
            flash("mark every student as P, A or L", "danger")
        else:
            _, changes = submit_attendance(db, section_id, session_date, period, sec["faculty_id"], statuses)
            flash(f"attendance saved for {len(statuses)} students, {newly_flagged(changes)} newly flagged", "success")
            return redirect(url_for("section", section_id=section_id))
    return render_template("mark.html", sec=sec, students=students, existing={}, locked=False,
                           session_date=session_date, period=period)


@app.route("/session/<int:session_id>", methods=["GET", "POST"])
def edit_session(session_id):
    db = get_db()
    cs = db.execute("SELECT * FROM class_sessions WHERE session_id = ?", (session_id,)).fetchone()
    if cs is None:
        abort(404)
    sec = section_for_faculty(cs["section_id"])
    students = section_students(sec["section_id"])

    if request.method == "POST":
        statuses = read_statuses(students)
        if statuses is None:
            flash("mark every student as P, A or L", "danger")
            return redirect(url_for("edit_session", session_id=session_id))
        try:
            changes = edit_attendance(db, session_id, statuses, me()["user_id"])
        except Locked:  # flow (c)
            flash("this class is older than 48 hours and locked, ask the HOD to change it", "danger")
            return redirect(url_for("section", section_id=sec["section_id"]))
        flash(f"attendance updated, {newly_flagged(changes)} newly flagged", "success")
        return redirect(url_for("section", section_id=sec["section_id"]))

    existing = {r["student_id"]: r["status"] for r in db.execute(
        "SELECT student_id, status FROM attendance_records WHERE session_id = ?", (session_id,))}
    return render_template("mark.html", sec=sec, students=students, existing=existing, locked=is_locked(cs),
                           session_date=cs["session_date"], period=cs["period"], session_id=session_id)


@app.post("/section/<int:section_id>/assessments")
def new_assessment(section_id):
    sec = section_for_faculty(section_id)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO assessments (section_id, name, max_marks, held_on, created_by) VALUES (?, ?, ?, ?, ?)",
            (section_id, request.form["name"].strip(), request.form.get("max_marks", type=float),
             request.form.get("held_on") or None, sec["faculty_id"]))
    except sqlite3.IntegrityError:
        flash("an assessment with that name already exists, or max marks is missing", "danger")
        return redirect(url_for("section", section_id=section_id))
    db.commit()
    return redirect(url_for("assessment", assessment_id=cur.lastrowid))


@app.route("/assessment/<int:assessment_id>", methods=["GET", "POST"])
def assessment(assessment_id):
    db = get_db()
    a = db.execute("SELECT * FROM assessments WHERE assessment_id = ?", (assessment_id,)).fetchone()
    if a is None:
        abort(404)
    sec = section_for_faculty(a["section_id"])
    students = section_students(sec["section_id"])

    if request.method == "POST":
        marks = {s["student_id"]: request.form.get(f"m{s['student_id']}", type=float) for s in students}
        marks = {sid: m for sid, m in marks.items() if m is not None}  # blank = not entered yet
        try:
            changes = save_marks(db, assessment_id, marks, me()["user_id"])
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("assessment", assessment_id=assessment_id))
        flash(f"marks saved for {len(marks)} students, {newly_flagged(changes)} newly flagged", "success")
        return redirect(url_for("section", section_id=sec["section_id"]))

    existing = {r["student_id"]: r["marks_obtained"] for r in db.execute(
        "SELECT student_id, marks_obtained FROM mark_entries WHERE assessment_id = ?", (assessment_id,))}
    return render_template("marks.html", sec=sec, a=a, students=students, existing=existing)
