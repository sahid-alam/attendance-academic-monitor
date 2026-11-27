# Source

App code (Flask, SQLite in dev, Bootstrap), tests and the synthetic seed data.
Only made-up data. No real student records and no `.env`.
Owner: S3 (Development & Testing).

## Run it

```bash
cd src
python3 -m venv ../.venv
../.venv/bin/pip install -r requirements.txt
../.venv/bin/flask --app app init-db     # creates attendance.db with demo data
../.venv/bin/flask --app app run
```

Open http://127.0.0.1:5000, pick "Dr. R. Sharma" and open CS501.

The schema and seed data come from the design (`schema.sql`, AAM-20). `schema_mysql.sql` is the production version.

## Tests

```bash
../.venv/bin/python -m unittest -v
```

## What works so far

- **Attendance (AAM-28):** faculty picks a date and period for their section and marks each student P, A or L. The attendance % updates after every submit.
  - **% formula:** (P + L) / sessions recorded × 100, read from the `v_attendance_pct` view.
  - **Same class twice:** the date and period already recorded opens the edit page instead.
  - **Editing:** allowed for 48 hours after the submit, then the class locks. Every change is written to `audit_log`.
  - **Access:** a faculty member who doesnt teach the section gets a 403.
- **Marks (AAM-29):** faculty adds an assessment with a max mark, then enters marks between 0 and the max. Changing a saved mark is written to `audit_log`.
- **Risk rules (AAM-30):** run after every attendance or marks save.
  - The thresholds are read from `risk_rules`, so the HOD can change them without touching code.
  - A status change saves a new `risk_flags` row with the reasons, and the mentor and the student get an in-app notification.
  - Students under intervention are left to the mentor until they are back above the thresholds.
- **Demo:** act as Dr. R. Sharma, open CS501 and mark Diya absent. She goes from Normal to Warning. Then switch to Prof. P. Verma to see the alert.
- **Tests (AAM-31):** 22 checks in `test_attendance.py` and `test_risk.py`. The test case table is in `report/test_cases.md`.
- **Mentor cases:** the mentor's home page lists mentees who are Warning, At-Risk or Under Intervention, with the reasons. The mentor can open a case on an At-Risk flag (Under Intervention) and close it (Resolved). If the student recovers first, the case closes by itself.
- **Not built:** email (SMTP), reports and an edit window for marks (attendance has one). Alerts are in-app only.
- **Who sees the status:** faculty only sees how many students were newly flagged. The status label goes to the mentor and the student.
- **Login:** there is no real login yet. The home page has an "acting as faculty" picker for the demo.
