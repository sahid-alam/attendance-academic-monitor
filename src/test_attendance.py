"""Quick checks for AAM-28. Full test suite comes in AAM-31. Run: python -m unittest -v"""
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta

from app import Locked, app, attendance_pct, connect, init_db, save_attendance


def sid(db, usn):
    return db.execute("SELECT id FROM student WHERE usn = ?", (usn,)).fetchone()["id"]


class AttendanceTest(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        init_db(self.db)
        self.course = 1

    def new_session(self):
        cur = self.db.execute("INSERT INTO class_session (course_id, held_on) VALUES (1, '2026-11-20')")
        return cur.lastrowid

    def test_pct_counts_late_as_present(self):
        self.assertEqual(attendance_pct(self.db, sid(self.db, "TEST002"), self.course), 75.0)
        self.assertEqual(attendance_pct(self.db, sid(self.db, "TEST003"), self.course), 75.0)

    def test_pct_none_when_nothing_recorded(self):
        self.db.execute("DELETE FROM attendance_record")
        self.assertIsNone(attendance_pct(self.db, sid(self.db, "TEST001"), self.course))

    def test_submit_updates_pct(self):
        s = sid(self.db, "TEST002")
        out = save_attendance(self.db, self.new_session(), {s: "A"})
        self.assertEqual(out[s], 66.67)  # 6 of 9

    def test_edit_within_48h_then_locked(self):
        s, session_id = sid(self.db, "TEST001"), self.new_session()
        t0 = datetime(2026, 11, 20, 10)
        save_attendance(self.db, session_id, {s: "A"}, now=t0)
        save_attendance(self.db, session_id, {s: "P"}, now=t0 + timedelta(hours=47))
        self.assertEqual(attendance_pct(self.db, s, self.course), 100.0)
        with self.assertRaises(Locked):
            save_attendance(self.db, session_id, {s: "A"}, now=t0 + timedelta(hours=49))

    def test_bad_status_rejected_by_db(self):
        with self.assertRaises(sqlite3.IntegrityError):
            save_attendance(self.db, self.new_session(), {sid(self.db, "TEST001"): "X"})

    def test_other_faculty_gets_403(self):
        with tempfile.TemporaryDirectory() as d:
            app.config["DATABASE"] = f"{d}/t.db"
            init_db(connect(app.config["DATABASE"]))
            with app.test_client() as client:
                client.post("/", data={"faculty_id": 2})
                self.assertEqual(client.get("/course/1").status_code, 403)
                self.assertEqual(client.get("/course/2").status_code, 200)


if __name__ == "__main__":
    unittest.main()
