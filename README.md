# Online Student Attendance & Academic Monitoring System

A web app for a college to record attendance and internal marks in one place.
It flags students who are falling behind early and shows the reason for each flag, so their mentor can step in before exam eligibility is checked.
This is our 4-person Software Engineering CCA team project.

## Team

| Student | Role |
|---|---|
| Student 1 (TBD) | Requirements & Analysis |
| Student 2 (TBD) | Design & Database |
| Student 3 (TBD) | Development & Testing |
| Madiha Iram (S4) | Project Management & Documentation |

## Process model

Agile Scrum with 2 sprints. Sprint 1 (19 to 22 Nov) is requirements, design and plan. Sprint 2 (23 to 26 Nov) is build and test. Submission is on 27 Nov.

## Tools

- **Jira** for the task board, project key `AAM`
- **GitHub** for code, docs and reviews
- **draw.io** for the diagrams
- **Flask, MySQL and Bootstrap** for the app (SQLite during development)

## Folder structure

| Folder | Contents |
|---|---|
| `requirements/` | SRS, use cases, survey |
| `planning/` | Project plan, WBS, Gantt chart, risks, Jira exports |
| `diagrams/` | `.drawio` sources and `.png` exports |
| `src/` | App code and tests |
| `report/` | The report |
| `presentation/` | The slides |

## Workflow

1. Pick a Jira issue and make a branch for it, eg `feature/attendance` or `docs/srs`.
2. Start every commit message with the Jira key, eg `AAM-12 add attendance form`.
3. Open a pull request into `main`. One teammate reviews it before it is merged.

Use made-up data only. Never commit real student data, passwords or `.env` files.

## Setup

Follow the [deployment and demo guide](report/DEPLOYMENT.md) for the verified Flask/SQLite attendance prototype. It uses synthetic data and a demo identity picker.

```bash
python3 -m venv .venv
.venv/bin/pip install -r src/requirements.txt
.venv/bin/flask --app src/app.py init-db  # destructive reset: disposable demo database only
.venv/bin/flask --app src/app.py run --host 127.0.0.1 --port 5000
.venv/bin/python -m unittest discover -s src -v
```

## Links

- [Jira backlog](https://sahidsworkspace-39968046.atlassian.net/jira/software/projects/AAM/boards/2/backlog) (workspace membership required)
- [S4 deliverable checklist](planning/DELIVERY_CHECKLIST.md)
- [Final report](report/FINAL_REPORT.md) / [PDF](report/FINAL_REPORT.pdf)
- [Slide deck](presentation/AAM_PRESENTATION.pptx) / [PDF](presentation/AAM_PRESENTATION.pdf)
- [Verification evidence](report/VERIFICATION.md)

## License

MIT. See [LICENSE](LICENSE).
