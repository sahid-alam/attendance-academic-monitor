"""Attendance checks (AAM-28) against the design schema and seed data. Run: python -m unittest -v"""
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta

from app import Locked, app, attendance_pct, connect, edit_attendance, init_db, submit_attendance

# seed: section 1 = CS501 (faculty 1), students 1 Aarav, 2 Diya, 3 Kabir, 4 Meera
ALL_P = {1: "P", 2: "P", 3: "P", 4: "P"}
T0 = datetime(2026, 11, 25, 10)


class AttendanceTest(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        init_db(self.db)

    def test_pct_matches_seed_and_late_counts(self):
        self.assertEqual(attendance_pct(self.db, 1, 1), 100.0)
        self.assertEqual(attendance_pct(self.db, 2, 1), 80.0)  # Diya has 2 L in there
        self.assertEqual(attendance_pct(self.db, 4, 1), 70.0)
        self.assertEqual(attendance_pct(self.db, 3, 1), 60.0)

    def test_pct_none_when_nothing_recorded(self):
        self.assertIsNone(attendance_pct(self.db, 1, 2))  # no CS502 classes in the seed

    def test_submit_updates_pct(self):
        submit_attendance(self.db, 1, "2026-11-25", 1, 1, {**ALL_P, 2: "A"}, now=T0)
        self.assertEqual(attendance_pct(self.db, 2, 1), 72.73)  # Diya 8 of 11

    def test_same_class_twice_is_rejected(self):
        submit_attendance(self.db, 1, "2026-11-25", 1, 1, ALL_P, now=T0)
        with self.assertRaises(sqlite3.IntegrityError):
            submit_attendance(self.db, 1, "2026-11-25", 1, 1, ALL_P, now=T0)

    def test_edit_within_48h_is_logged_then_locked(self):
        sid = submit_attendance(self.db, 1, "2026-11-25", 1, 1, {**ALL_P, 1: "A"}, now=T0)
        edit_attendance(self.db, sid, ALL_P, user_id=2, now=T0 + timedelta(hours=47))
        self.assertEqual(attendance_pct(self.db, 1, 1), 100.0)
        log = self.db.execute("SELECT * FROM audit_log ORDER BY log_id DESC").fetchone()
        self.assertEqual((log["user_id"], json.loads(log["old_value"]), json.loads(log["new_value"])),
                         (2, {"status": "A"}, {"status": "P"}))
        with self.assertRaises(Locked):
            edit_attendance(self.db, sid, {**ALL_P, 1: "A"}, user_id=2, now=T0 + timedelta(hours=49))

    def test_bad_status_rejected_by_db(self):
        with self.assertRaises(sqlite3.IntegrityError):
            submit_attendance(self.db, 1, "2026-11-25", 1, 1, {1: "X"}, now=T0)


class PagesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app.config["DATABASE"] = f"{self.tmp.name}/t.db"
        init_db(connect(app.config["DATABASE"]))
        self.client = app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_other_faculty_gets_403(self):
        self.client.post("/", data={"faculty_id": 2})
        self.assertEqual(self.client.get("/section/1").status_code, 403)
        self.assertEqual(self.client.get("/section/2").status_code, 200)

    def test_take_attendance_through_the_form(self):
        self.client.post("/", data={"faculty_id": 1})
        form = {"session_date": "2026-11-25", "period": 1, **{f"s{k}": v for k, v in {**ALL_P, 2: "A"}.items()}}
        page = self.client.post("/section/1/attendance", data=form, follow_redirects=True).get_data(as_text=True)
        self.assertIn("72.73%", page)
        # same date and period again goes to the edit page (flow b)
        again = self.client.get("/section/1/attendance?session_date=2026-11-25&period=1")
        self.assertEqual(again.status_code, 302)
        self.assertIn("/session/", again.location)


if __name__ == "__main__":
    unittest.main()
