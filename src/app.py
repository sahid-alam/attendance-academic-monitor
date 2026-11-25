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
    is already recorded (sequence diagram flow b). Returns the new session_id"""
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
    return cur.lastrowid


def edit_attendance(db, session_id, statuses, user_id, now=None):
    """Change a recorded session within 48 hours. Every changed entry goes to audit_log"""
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
    return render_template("index.html", faculty=faculty, sections=sections, me=me())


@app.route("/section/<int:section_id>")
def section(section_id):
    sec = section_for_faculty(section_id)
    db = get_db()
    students = [dict(s, pct=attendance_pct(db, s["student_id"], sec["course_id"]))
                for s in section_students(section_id)]
    sessions = db.execute(
        "SELECT * FROM class_sessions WHERE section_id = ? ORDER BY session_date DESC, period DESC",
        (section_id,)).fetchall()
    return render_template("section.html", sec=sec, students=students, sessions=sessions,
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
            submit_attendance(db, section_id, session_date, period, sec["faculty_id"], statuses)
            flash(f"attendance saved for {len(statuses)} students", "success")
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
            edit_attendance(db, session_id, statuses, me()["user_id"])
        except Locked:  # flow (c)
            flash("this class is older than 48 hours and locked, ask the HOD to change it", "danger")
            return redirect(url_for("section", section_id=sec["section_id"]))
        flash("attendance updated", "success")
        return redirect(url_for("section", section_id=sec["section_id"]))

    existing = {r["student_id"]: r["status"] for r in db.execute(
        "SELECT student_id, status FROM attendance_records WHERE session_id = ?", (session_id,))}
    return render_template("mark.html", sec=sec, students=students, existing=existing, locked=is_locked(cs),
                           session_date=cs["session_date"], period=cs["period"], session_id=session_id)
