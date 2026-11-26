# Work breakdown structure (AAM-15)

Owner: S4 / Madiha Iram. Dates are the original November 2026 baseline, not actual completion.
S1 = Requirements & Analysis; S2 = Design & Database; S3 = Development & Testing;
S4 = Project Management & Documentation (Madiha). Other names require team confirmation.

| WBS | Work package / output | Accountable; support / backup | Baseline due | Depends on | Acceptance condition |
|---|---|---|---|---|---|
| 1.1 | Problem, scope, actors and objectives | S1; S4 | 20 Nov | None | Five roles and exclusions stated |
| 1.2 | SRS, use cases and traceability | S1; S3 | 21 Nov | 1.1 | FR1–FR15 and errors mapped to design |
| 1.3 | Stakeholder evidence / survey | S1; S4 | 21 Nov | 1.1 | Actual responses cited, or absence disclosed |
| 2.1 | Scrum process diagram (AAM-13) | S4; S1 | 20 Nov | 1.1 | Two sprints, events, increments and feedback |
| 2.2 | Model justification (AAM-14) | S4; S1 | 20 Nov | 2.1 | Switch rationale and tradeoffs documented |
| 3.1 | WBS (AAM-15) | S4; S2 | 20 Nov | 1.1 | Outputs, owners and dependencies recorded |
| 3.2 | Gantt and milestones (AAM-16) | S4; S3 | 21 Nov | 3.1 | Dates consistent with dependencies and deadline |
| 3.3 | Risk register (AAM-17) | S4; all | 21 Nov | 3.1 | Risk scores, triggers and response owners |
| 3.4 | Board tracking and review evidence | S4; all | 26 Nov | 3.1 | Live task links, owners and evidence; no invented history |
| 4.1 | Architecture, ER and schema | S2; S3 | 22 Nov | 1.2 | Entity names and schema agree |
| 4.2 | DFD levels 0, 1, 2 and dictionary | S2; S1 | 22 Nov | 1.2 | Parent/child flows balance; data entries defined |
| 4.3 | Sequence and student state models | S1; S3 | 22 Nov | 4.1, 4.2 | Normal and exception flows represented |
| 5.1 | Attendance vertical slice | S3; S2 | 23 Nov | 4.1 | Form saves P/A/L, percentages update, edit lock works |
| 5.2 | Marks and risk evaluation | S3; S2 | 24 Nov | 5.1, 4.3 | Valid marks, reasons and status changes tested |
| 5.3 | Mentor intervention and notification | S3; S1 | 24 Nov | 5.2 | Access and state transitions verified; channels identified |
| 5.4 | Test suite and case table | S3; S2 | 25 Nov | 5.1–5.3 | Current revision tested; failures and exclusions recorded |
| 6.1 | Ethics analysis | S1; S4 | 24 Nov | 1.2 | Privacy, consent, bias and accessibility addressed |
| 6.2 | Responsibility statement (AAM-33) | S4; S1 | 24 Nov | 6.1 | Commitments and implementation limits explicit |
| 7.1 | Deployment guide (AAM-36) | S4; S3 | 25 Nov | 5.1 | Clean SQLite setup and safe reset verified |
| 7.2 | Final report (AAM-34) | S4; all | 26 Nov | 1–6, 7.1 | Evidence-based report with citations and limitations |
| 7.3 | Slides (AAM-35) | S4; all | 26 Nov | 7.2 | Four speaker roles, readable visuals and demo instructions |
| 7.4 | Rehearsal (AAM-37) | S4; all | 26 Nov | 7.3, 7.1 | Actual timed run recorded with fixes and attendees |
| 7.5 | Final check and submission | S4; all | 27 Nov | 7.2–7.4 | Review, links, artifacts and submission receipt checked |

## Control and handoff

A parent work package is complete only when its children meet their review conditions.
S4 coordinates handoffs; the named technical owner verifies their material in the report.
The backup role assists when the owner is unavailable; it does not imply their acceptance.
Use a task's actual status and Git/PR link in Jira, preserving baseline due dates.

The dependency chain 1.2 → 4.1/4.2 → 5.1 → 5.2/5.3 → 5.4 → 7.2 → 7.3 → 7.4 → 7.5
has little spare time. Planning and ethics can proceed alongside design/build, while report
outlining can begin early. Final report sign-off still waits for the tested implementation.
