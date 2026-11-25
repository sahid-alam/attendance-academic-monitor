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
- **Not yet:** marks (AAM-29) and the risk rules (AAM-30).
- **Login:** there is no real login yet. The home page has an "acting as faculty" picker for the demo.
