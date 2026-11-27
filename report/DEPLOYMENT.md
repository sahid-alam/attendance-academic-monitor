# Deployment and demo guide (AAM-36)

Target: the attendance prototype on main at `57c0c6a` and this documentation branch.
Prepared 26 November 2026. Supported runtime: Python 3.12, Flask 3.1.0, SQLite.
The included MySQL schema is a design artifact; the application uses `sqlite3` and cannot
switch to MySQL through a connection string alone.

## 1. Clean setup

Run from the repository root in a cloud VM, lab computer or development machine:

```bash
git clone https://github.com/sahid-alam/attendance-academic-monitor.git
cd attendance-academic-monitor
git switch docs/madiha-aam-submission
python3 -m venv .venv
.venv/bin/python -m pip install -r src/requirements.txt
```

The branch must be published before someone else can check it out. The repository contains
no real student records. Use only the synthetic seed for this demonstration.

## 2. Initialize a disposable demo database

WARNING: `init-db` drops and recreates the application tables. Run it only against a disposable
demo database. Stop the app and make a backup before resetting a database you wish to retain.

```bash
export DATABASE="$PWD/src/attendance.db"
.venv/bin/flask --app src/app.py init-db
.venv/bin/flask --app src/app.py run --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`. A cloud VM's loopback address is inside the VM; view it through
its desktop browser or an authorized tunnel. The prototype has an identity picker and must
not be exposed publicly. The session key is generated at startup if `SECRET_KEY` is unset;
a restart then clears existing sessions. A stable secret, if needed for a controlled demo,
belongs in environment settings, never in Git or a shared screenshot.

## 3. Demonstrate what this revision implements

1. Pick **Dr. R. Sharma**, open **CS501**. Confirm seed attendance: Aarav 100%, Diya 80%,
   Kabir 60%, Meera 70%. The seed already includes historical flags; these do not prove
   runtime risk evaluation exists on main.
2. Create a session dated **26 November 2026**, period **1**. Mark Aarav P, Diya A,
   Kabir P and Meera P. Submit once.
3. Confirm Diya becomes **72.73%**: 8 attended of 11 recorded sessions. Late counts as
   attended. The current main revision updates the percentage only; it does not generate
   a new warning or mentor alert.
4. Request the same date/period again. It should open the existing session for editing.
   Correct Diya to P within 48 hours and confirm **81.82%** (9/11).
5. Switch to **Prof. P. Verma** and try `/section/1`. Expect **403**. Explain that the
   check restricts the selected demo faculty and does not authenticate their identity.
6. Explain the older-than-48-hours lock and audit behavior using the test results below.

Do not promise marks, risk alerts or mentor-case UI unless PR #4 has been reviewed, merged
and verified at the revision being demonstrated. Re-run the suite and update this guide
before changing the demo scope. Do not merge a dependency only to make a slide claim true.

## 4. Verify

```bash
.venv/bin/python -m unittest discover -s src -v
```

At the inspected base revision the suite contains 8 attendance/page checks. It covers seed
percentages, no-data handling, submission updates, duplicate sessions, audit/locking,
invalid status, section ownership and form flow. It does not establish production security,
performance under 60 users, WCAG conformance or MySQL compatibility.

## 5. Backup, reset and recovery

For a file-backed demo, stop Flask with Ctrl-C before copying `src/attendance.db` to a private
backup outside the repository. Preserve any SQLite sidecar files if a journal mode creates
them. Restore only while the app is stopped, then restart and verify the seed/selected state.
Do not commit the database: `*.db` is ignored. To reset synthetic data, stop the app and run
`init-db` again only after confirming `DATABASE` points to the disposable demo database.

| Symptom | Check / recovery |
|---|---|
| `No module named flask` | Use `.venv/bin/python` / `.venv/bin/flask`; install requirements there |
| `no such table` | Confirm `DATABASE`; initialize that disposable database |
| 403 opening a section | Choose the faculty assigned to that section |
| Duplicate date/period | Use existing-session edit, or choose a new period |
| Old class locked | Expected after 48 hours from first submission; do not change system clock |
| Missing marks or mentor page | This main revision lacks those routes; use the documented scope |
| Port busy | Stop your own old demo process or choose another free port |
| Styles absent offline | Bootstrap uses a CDN; core forms may work without styles. Prepare a screenshot backup |

## 6. Production readiness and rollback

No public production deployment is claimed. A production release needs real authentication,
complete server-side authorization, CSRF controls, security testing, approved privacy and
retention rules, HTTPS, a production WSGI server, monitoring and tested backups. Migrating
to MySQL requires application data-access changes and integration testing, not only running
the supplied schema. Document SMTP separately when implemented.

For the submission, preserve the verified commit and demo database state. If an integration
fails, return to the verified commit on a separate checkout and use the attendance-only demo;
retain the failed integration as a review item. The slide backup must be labeled as recorded
or static evidence rather than presented as a live execution.

## 7. Controlled lab-server procedure (not a deployment record)

These are instructions for an authorized lab host, **not evidence that a server deployment
has been performed**. Obtain the lab hostname, SSH username and access from the lab supervisor.
Use an approved Python environment and a dedicated checkout in your own account. Replace
`LAB_USER@LAB_HOST` below with the supplied details; never share SSH credentials in Git.

From your own computer:

```bash
ssh LAB_USER@LAB_HOST
```

On the lab server (POSIX shell, Python 3.12 or a compatible installed Python):

```bash
mkdir -p "$HOME/aam-lab-demo"
cd "$HOME/aam-lab-demo"
git clone --branch docs/madiha-aam-submission --single-branch \
  https://github.com/sahid-alam/attendance-academic-monitor.git app
cd app
git rev-parse HEAD  # retain this revision in the demo record
python3 -m venv .venv
.venv/bin/python -m pip install -r src/requirements.txt
mkdir -p "$HOME/aam-lab-demo/data" "$HOME/aam-lab-demo/backups"
chmod 700 "$HOME/aam-lab-demo/data" "$HOME/aam-lab-demo/backups"
export DATABASE="$HOME/aam-lab-demo/data/attendance-demo.db"
# Destructive initialization: only this disposable, synthetic demo database.
.venv/bin/flask --app src/app.py init-db
.venv/bin/python -m unittest discover -s src -v
.venv/bin/flask --app src/app.py run --host 127.0.0.1 --port 5000
```

Keep this SSH terminal open while Flask runs in the foreground. This development server is
for the supervised demo only. The identity picker **is not secure authentication**: all data
must remain synthetic. Do not bind to `0.0.0.0`, publish a public preview, or open a firewall
port to bypass tunnel restrictions. If the directory already exists, inspect it and reuse
only the intended checkout; do not overwrite another person's work.

In a **second terminal on your own computer**, create a loopback-only tunnel:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:5001:127.0.0.1:5000 LAB_USER@LAB_HOST
```

Open `http://127.0.0.1:5001` on your computer and run the section 3 demonstration. The tunnel
connects your local port 5001 to Flask's loopback port 5000 on the lab host. Only an authorized
SSH user should have access. If tunneling is prohibited, use the lab's approved remote desktop
and its browser at `http://127.0.0.1:5000`, or arrange a supervised local demo with the lab
supervisor. Do not expose the prototype to the public as an alternative.

### Stop, back up, restore and reset

Stop Flask with **Ctrl-C in the server terminal**; stop the SSH tunnel with **Ctrl-C in the
second terminal**. This procedure leaves no background app process. Confirm the app has stopped
before copying or restoring SQLite. In the server checkout, with Flask stopped:

```bash
export DATABASE="$HOME/aam-lab-demo/data/attendance-demo.db"
# SQLite backup API includes committed data even if sidecar journal files exist.
.venv/bin/python - <<'PY'
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
source = Path(os.environ['DATABASE'])
if not source.is_file():
    raise SystemExit('Demo database missing; check DATABASE before backup')
backup = Path.home() / 'aam-lab-demo/backups' / (
    'attendance-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.db'
)
with sqlite3.connect(f'{source.as_uri()}?mode=ro', uri=True) as src:
    with sqlite3.connect(backup) as dst:
        src.backup(dst)
backup.chmod(0o600)
print(backup)
PY
```

For reset, confirm `DATABASE` is the dedicated `attendance-demo.db` above and preserve the
backup first, then run `.venv/bin/flask --app src/app.py init-db` again. For restore, keep Flask
stopped and use SQLite's backup API to copy the chosen backup into the demo database (open the
backup read-only as the source and `DATABASE` as the destination). Avoid copying over an open
database or leaving mismatched sidecar files. Restart with the same loopback command and verify
the restored attendance state. Never commit either database or backup.

### Fallback if the live lab demo fails

1. Check SSH access, port conflicts, dependencies and `DATABASE` using the recovery table above.
2. If the lab remains unavailable, start the same verified revision on the presenter's laptop
   using sections 1–2 and synthetic data. Label this **local fallback**, not a lab deployment.
3. If no live execution is possible, show the prepared screenshots/slides and recorded test
   evidence, labeled **static / previously recorded evidence**. Explain what failed and which
   behavior could not be demonstrated live; do not claim that the lab deployment succeeded.

Record the actual host arrangement, revision, verification output and outcome only after a
real supervised run. Server deployment and team acceptance remain pending until that happens.
