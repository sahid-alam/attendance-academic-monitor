# Presentation rehearsal pack (AAM-37)

Coordinator: S4 / Madiha Iram. Target: 10 minutes plus questions.
Prepared 26 November 2026. **A real rehearsal has not been performed or certified by this pack.**
Use the editable deck `AAM_PRESENTATION.pptx`, slide PDF and speaker notes in `SLIDES.md`.

## Run of show

| Slides | Speaker | Target | Handoff |
|---|---|---|---|
| 1–2 | S1 | 70 seconds | Problem, users and scope → S4 |
| 3–4 | S4 / Madiha | 105 seconds | Process and task board → S2 |
| 5 | S2 | 50 seconds | DFD levels and balancing → S3 with S1 |
| 6 | S3; S1 narrates the sequence | 110 seconds | Live attendance / designed state transitions → S2 |
| 7–8 | S2 | 90 seconds | Architecture, stack, deployment and bottlenecks → S3 |
| 9–10 | S3 | 85 seconds | Verification and GitHub contribution evidence → S1 |
| 11 | S1 | 50 seconds | Ethics → S4 for closing questions |
| 12 | S4 / Madiha | 40 seconds | Readiness and questions |

Total: 600 seconds. If the faculty sets a different duration, shorten explanations before
rushing the demo. The topic and speaker order matches Stage 7 of `planning/PROJECT_PLAN.md`. All four members speak. S4 covers the two assessed planning stages and
keeps the difference between planned and completed work visible.

## Before the run

- Confirm presenter names and assignment/marking requirements with the team.
- Open the PPTX/PDF and verify diagrams are readable on the actual display.
- Start from the verified commit; use a disposable synthetic database.
- Run tests and initialize the seed before opening the demo; keep the terminal ready.
- Pick Dr. R. Sharma and CS501; avoid reusing a previously created date/period.
- Open the repository PR and Jira board if access is available. Do not show secrets/account settings.
- Keep a labeled static backup of the Diya percentage calculation if the app fails.
- Confirm any adopted changes from PRs #3–#5; re-test and update report/slides before claiming them.

## Demo cues for S3 and S1 (slide 6; verification on slide 9)

On main: show Diya 80% → submit 26 November, period 1, Diya Absent → 72.73%.
Correct to Present → 81.82%; duplicate session opens editing. Explain the 48-hour lock and
403 ownership check with test evidence. Do not narrate a newly generated risk alert or a
mentor workflow on main. Those require the reviewed and verified integration of PR #4.
If the demo fails, state the failure, show the static calculation, and return to the verified
test record rather than hiding the failure or pretending a screenshot is live.

## Questions to practice

| Question | Answer cue |
|---|---|
| Why Scrum after Incremental? | Original six-week/five-increment plan did not fit the deadline; two sprints add explicit review and blocker visibility. Scrum also produces increments |
| What is actually implemented? | Attendance, percentages, duplicate handling, 48-hour lock and edit audit, selected-faculty ownership check |
| Is the system securely authenticated? | No; identity picker is for synthetic demo use; real authentication is a production prerequisite |
| Why 75%, 65% and 40%? | Project assumptions requiring institutional confirmation; 40% is a team default |
| What does Late mean? | Counts as attended in the current formula; institution must approve that policy |
| Are risk alerts working now? | Not on the documented main revision; separate PR #4 proposes in-app alerts and cases |
| Is MySQL deployed? | DDL is supplied, but app uses SQLite; migration and integration tests remain |
| Does 8 passing tests mean ready for real students? | No; security, performance, accessibility, policy and privacy checks remain |
| Did everyone contribute? | Cite actual commits, artifacts and reviews; do not infer equal effort from role allocation |

## Actual rehearsal record (complete after the run)

27 November scope decision: the user deferred AAM-37. The pack is ready; actual rehearsal
completion remains unclaimed and the Jira/GitHub rehearsal tasks remain open.

| Field | Actual evidence |
|---|---|
| Date/time/timezone | Pending |
| Attendees and speaker names | Pending |
| Verified commit / PR | Pending |
| Total elapsed time | Pending |
| Per-speaker timing | Pending |
| Demo outcome / screenshots | Pending |
| Questions asked and unclear explanations | Pending |
| Follow-up fixes, owners and retest | Pending |
| Team review and sign-off | Pending |

AAM-37 can be closed only after a real timed run and follow-up checks are recorded. Creating
these instructions does not complete the rehearsal, and an assistant cannot attest to members'
attendance or understanding.
