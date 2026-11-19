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
| Student 4 (TBD) | Project Management & Documentation |

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

Setup steps for `src/` are coming in Sprint 2.

## Links

- Jira board: (link coming)

## License

MIT. See [LICENSE](LICENSE).
