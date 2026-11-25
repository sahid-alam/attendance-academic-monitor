"""Marks (AAM-29) and risk rule (AAM-30) checks against the design seed data. Run: python -m unittest -v
Seed: CS501 = section 1 / course 1 (Dr. R. Sharma), CS502 = section 2 / course 2.
Students 1 Aarav 100%, 2 Diya 80%, 3 Kabir 60% (under intervention), 4 Meera 70% (warning).
Mentor for all of them is Prof. P. Verma, user 3"""
import json
import tempfile
import unittest
from datetime import datetime, timedelta

from app import app, connect, init_db, save_marks, submit_attendance

ALL_P = {1: "P", 2: "P", 3: "P", 4: "P"}
T0 = datetime(2026, 11, 25, 10)


class RiskTest(unittest.TestCase):
    def setUp(self):
        self.db = connect(":memory:")
        init_db(self.db)
        self.period = 0

    def take(self, statuses):
        self.period += 1
        return submit_attendance(self.db, 1, "2026-11-25", self.period, 1, {**ALL_P, **statuses},
                                 now=T0 + timedelta(minutes=self.period))[1]

    def current(self, student_id, course_id=1):
        row = self.db.execute("SELECT * FROM risk_flags WHERE student_id = ? AND course_id IS ? AND is_current = 1",
                              (student_id, course_id)).fetchone()
        return row["status"] if row else "NORMAL"

    def test_main_scenario_absent_moves_diya_to_warning_and_mentor_is_told(self):
        self.assertEqual(self.take({2: "A"}), [(2, "NORMAL", "WARNING")])  # 80% -> 72.73%
        flag = self.db.execute("SELECT * FROM risk_flags WHERE student_id = 2 AND course_id = 1 AND is_current = 1").fetchone()
        reason = self.db.execute("SELECT * FROM risk_flag_reasons WHERE flag_id = ?", (flag["flag_id"],)).fetchone()
        self.assertEqual((reason["rule_id"], reason["actual_value"]), (1, 72.73))
        notes = self.db.execute("SELECT recipient_id, message FROM notifications WHERE flag_id = ?",
                                (flag["flag_id"],)).fetchall()
        self.assertEqual({n["recipient_id"] for n in notes}, {3, 6})  # mentor and Diya
        self.assertNotIn("Risk", [n["message"] for n in notes if n["recipient_id"] == 6][0])

    def test_thresholds_come_from_the_table(self):
        self.db.execute("UPDATE risk_rules SET threshold = 85 WHERE rule_id = 2")  # HOD raises the cutoff
        self.assertIn((2, "NORMAL", "AT_RISK"), self.take({}))  # Diya 81.82% is now below 85

    def test_inactive_rule_is_ignored(self):
        self.db.execute("UPDATE risk_rules SET is_active = 0 WHERE rule_id = 1")
        changes = self.take({2: "A"})
        self.assertNotIn(2, [sid for sid, *_ in changes])  # Diya at 72.73% no longer gets a Warning
        self.assertIn((4, "WARNING", "NORMAL"), changes)  # and Meera's Warning clears

    def test_recovery_goes_back_to_normal(self):
        self.take({})  # Meera 8 of 11
        changes = self.take({})
        self.assertIn((4, "WARNING", "NORMAL"), changes)  # 9 of 12 = 75%
        self.assertIn((3, "AT_RISK", "NORMAL"), changes)  # Kabir is above 65% now, so only 1 course is below a cutoff

    def test_under_intervention_is_left_to_the_mentor(self):
        self.assertEqual(self.take({3: "A"}), [])
        self.assertEqual(self.current(3), "UNDER_INTERVENTION")

    def test_low_test_mark_makes_at_risk_and_edit_is_logged(self):
        changes = save_marks(self.db, 1, {4: 7}, user_id=2, now=T0)  # Meera 12 -> 7 of 20 = 35%
        self.assertEqual(changes, [(4, "WARNING", "AT_RISK")])
        log = self.db.execute("SELECT * FROM audit_log WHERE table_name = 'mark_entries'").fetchone()
        self.assertEqual((json.loads(log["old_value"]), json.loads(log["new_value"])),
                         ({"marks_obtained": 12}, {"marks_obtained": 7}))

    def test_two_courses_below_cutoff_rule(self):
        # Diya is At-Risk in CS502 (35% test). A low CS501 test makes it 2 courses
        changes = save_marks(self.db, 1, {2: 5}, user_id=2, now=T0)
        self.assertIn((2, "NORMAL", "AT_RISK"), changes)
        self.assertEqual(self.current(2, None), "AT_RISK")

    def test_marks_outside_range_are_rejected(self):
        for bad in (-1, 21):
            with self.assertRaises(ValueError):
                save_marks(self.db, 1, {1: bad}, user_id=2, now=T0)
        self.assertEqual(self.db.execute("SELECT marks_obtained FROM mark_entries WHERE assessment_id = 1 AND student_id = 1")
                         .fetchone()[0], 18)


class RiskPagesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app.config["DATABASE"] = f"{self.tmp.name}/t.db"
        init_db(connect(app.config["DATABASE"]))
        self.client = app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_demo_flow_faculty_submits_mentor_sees_alert(self):
        self.client.post("/", data={"faculty_id": 1})
        form = {"session_date": "2026-11-25", "period": 1, **{f"s{k}": v for k, v in {**ALL_P, 2: "A"}.items()}}
        page = self.client.post("/section/1/attendance", data=form, follow_redirects=True).get_data(as_text=True)
        self.assertIn("1 newly flagged", page)
        self.assertNotIn("Warning", page)  # faculty sees the count, not the label
        self.client.post("/", data={"faculty_id": 2})  # switch to the mentor
        self.assertIn("Diya Patel (CSE2302) is now Warning in CS501", self.client.get("/").get_data(as_text=True))

    def test_marks_form(self):
        self.client.post("/", data={"faculty_id": 1})
        self.client.post("/section/1/assessments", data={"name": "Internal Test 2", "max_marks": 20})
        aid = 3  # seed has 2 assessments
        bad = self.client.post(f"/assessment/{aid}", data={"m1": 25}, follow_redirects=True).get_data(as_text=True)
        self.assertIn("between 0 and 20", bad)
        ok = self.client.post(f"/assessment/{aid}", data={"m1": 18, "m2": 4}, follow_redirects=True).get_data(as_text=True)
        self.assertIn("marks saved for 2 students", ok)


if __name__ == "__main__":
    unittest.main()
