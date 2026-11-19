"""Attendance module (AAM-28): faculty creates a session and marks P/A/L for each student"""
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

HERE = Path(__file__).parent
EDIT_WINDOW = timedelta(hours=48)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-not-secret")
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


# --- attendance logic -------------------------------------------------------

def attendance_pct(db, student_id, course_id):
    """(P + L) / sessions recorded so far x 100, None if nothing recorded yet"""
    row = db.execute(
        """SELECT COUNT(*) AS total, SUM(ar.status IN ('P', 'L')) AS attended
           FROM attendance_record ar JOIN class_session cs ON cs.id = ar.session_id
           WHERE ar.student_id = ? AND cs.course_id = ?""",
        (student_id, course_id),
    ).fetchone()
    if not row["total"]:
        return None
    return round(row["attended"] * 100 / row["total"], 2)


def is_locked(cs, now=None):
    return bool(cs["recorded_at"]) and (now or datetime.now()) - datetime.fromisoformat(cs["recorded_at"]) > EDIT_WINDOW


def save_attendance(db, session_id, statuses, now=None):
    """Save P/A/L for one session and return {student_id: new %}.
    The returned dict is what the risk engine (AAM-30) will read"""
    now = now or datetime.now()
    cs = db.execute("SELECT * FROM class_session WHERE id = ?", (session_id,)).fetchone()
    if is_locked(cs, now):
        raise Locked()
    db.executemany(
        """INSERT INTO attendance_record (session_id, student_id, status) VALUES (?, ?, ?)
           ON CONFLICT (session_id, student_id) DO UPDATE SET status = excluded.status""",
        [(session_id, sid, st) for sid, st in statuses.items()],
    )
    if not cs["recorded_at"]:
        db.execute("UPDATE class_session SET recorded_at = ? WHERE id = ?",
                   (now.isoformat(sep=" ", timespec="seconds"), session_id))
    db.commit()
    return {sid: attendance_pct(db, sid, cs["course_id"]) for sid in statuses}


# --- pages ------------------------------------------------------------------
# ponytail: "act as faculty" picker instead of real login. Swap for login + hashed passwords when auth is built

def course_for_faculty(course_id):
    course = get_db().execute("SELECT * FROM course WHERE id = ?", (course_id,)).fetchone()
    if course is None:
        abort(404)
    if course["faculty_id"] != session.get("faculty_id"):
        abort(403)  # sequence diagram flow (a): faculty doesnt teach this course
    return course


def enrolled_students(course_id):
    return get_db().execute(
        """SELECT s.* FROM student s JOIN enrollment e ON e.student_id = s.id
           WHERE e.course_id = ? ORDER BY s.usn""",
        (course_id,),
    ).fetchall()


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        session["faculty_id"] = int(request.form["faculty_id"])
        return redirect(url_for("index"))
    faculty = db.execute("SELECT * FROM faculty").fetchall()
    courses = db.execute("SELECT * FROM course WHERE faculty_id = ?", (session.get("faculty_id"),)).fetchall()
    return render_template("index.html", faculty=faculty, courses=courses)


@app.route("/course/<int:course_id>")
def course(course_id):
    c = course_for_faculty(course_id)
    db = get_db()
    students = [dict(s, pct=attendance_pct(db, s["id"], course_id)) for s in enrolled_students(course_id)]
    sessions = db.execute(
        "SELECT * FROM class_session WHERE course_id = ? ORDER BY held_on DESC", (course_id,)
    ).fetchall()
    return render_template("course.html", course=c, students=students, sessions=sessions,
                           today=datetime.now().date().isoformat())


@app.post("/course/<int:course_id>/sessions")
def new_session(course_id):
    course_for_faculty(course_id)
    db = get_db()
    cur = db.execute("INSERT INTO class_session (course_id, held_on) VALUES (?, ?)",
                     (course_id, request.form["held_on"]))
    db.commit()
    return redirect(url_for("mark", session_id=cur.lastrowid))


@app.route("/session/<int:session_id>", methods=["GET", "POST"])
def mark(session_id):
    db = get_db()
    cs = db.execute("SELECT * FROM class_session WHERE id = ?", (session_id,)).fetchone()
    if cs is None:
        abort(404)
    c = course_for_faculty(cs["course_id"])
    students = enrolled_students(c["id"])

    if request.method == "POST":
        statuses = {s["id"]: request.form.get(f"s{s['id']}") for s in students}
        if any(st not in ("P", "A", "L") for st in statuses.values()):
            flash("mark every student as P, A or L", "danger")
            return redirect(url_for("mark", session_id=session_id))
        try:
            new_pct = save_attendance(db, session_id, statuses)
        except Locked:
            flash("this session is older than 48 hours and locked, ask the HOD to change it", "danger")
            return redirect(url_for("course", course_id=c["id"]))
        flash(f"attendance saved for {len(new_pct)} students, % updated", "success")
        return redirect(url_for("course", course_id=c["id"]))

    existing = {r["student_id"]: r["status"] for r in db.execute(
        "SELECT student_id, status FROM attendance_record WHERE session_id = ?", (session_id,))}
    return render_template("mark.html", course=c, cs=cs, students=students, existing=existing, locked=is_locked(cs))
