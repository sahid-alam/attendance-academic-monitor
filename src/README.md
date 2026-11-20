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

Open http://127.0.0.1:5000, pick "Prof. Demo One" and open DEMO-SE.

## Tests

```bash
../.venv/bin/python -m unittest -v
```

## What works so far

- **Attendance (AAM-28):** faculty creates a session and marks each student P, A or L. The attendance % updates after every submit.
  - **% formula:** (P + L) / sessions recorded × 100.
  - **Editing:** allowed for 48 hours after the first submit, then the session locks.
  - **Access:** a faculty member who doesnt teach the course gets a 403.
- **Not yet:** marks (AAM-29) and the risk rules (AAM-30).
  - `save_attendance()` returns the new % per student, which is where the risk engine will plug in.
- **Login:** there is no real login yet. The home page has an "acting as faculty" picker for the demo.
