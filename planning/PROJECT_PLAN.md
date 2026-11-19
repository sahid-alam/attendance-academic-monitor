# Project Plan: Online Student Attendance & Academic Monitoring System

The guidelines ask us to "propose and document" the system. Code is not marked by itself, but the demo should show one working flow. Process model (4 marks) and planning (4 marks) are worth more than design (3 marks). So most of the effort goes into the models, the plan and the Git history. `/src` stays a small working piece of the system.

**One scenario runs through everything:**
Faculty submits attendance → attendance % recalculated → risk rule fires → student status changes → mentor notified.

The same scenario is used for:
- the Level 2 data flow diagram (DFD)
- the sequence diagram
- the state transition
- Student 3's code
- the live demo

## Who owns each stage

**Bold** marks work the assigned role table did not give to anyone. We split it as follows.

| Stage | Owner | Support |
|---|---|---|
| 1. Problem, scope, requirements | S1 | S4 |
| 2. Process model | **S4** | S1 |
| 3. WBS, Gantt chart, risks, board | S4 | all |
| 4. Architecture, ER diagram, data dictionary | S2 | |
| 4. DFDs | **S2** | S3 |
| 4. Sequence diagram | **S1** | S3 |
| 5. Repo setup | **S3** | |
| 5. README, board | S4 | all commit |
| 5. `/src`: attendance, marks, tests | S3 | S2 (schema) |
| 6. Ethics table | **S1 + S4** | all |
| 7. Report, slides, deployment doc | S4 | all |

## Stage 1: Problem and scope

**Problem statement.** Colleges track attendance in registers or spreadsheets and internal marks in separate sheets. Students who fall below the attendance requirement or fail internal tests are often noticed only when exam eligibility is checked. By then it is too late to help them. The system records attendance and internal marks in one place. It flags at-risk students early and gives the reason for each flag, so mentors can step in.

**Actors**
- **Admin:** sets up courses, users and the academic calendar.
- **Faculty:** records attendance and marks.
- **Mentor (faculty advisor):** acts on risk flags.
- **HOD:** views reports and sets the risk thresholds.
- **Student:** views their own attendance, marks and status.
- **Parent:** secondary stakeholder. Has no login. Receives notices only if the student agrees.

**Objectives**
1. Record attendance and marks digitally.
2. Show each student's attendance % per course, updated after every entry.
3. Detect at-risk students with rules that can be changed and that state their reason.
4. Give mentors a way to record and track interventions.
5. Provide dashboards and reports for each role.

**In scope:** a web application with the five roles above, attendance, internal marks, rule-based risk flags, interventions, email and in-app alerts, CSV export.

**Out of scope:** biometric, RFID or face-recognition attendance, fees, timetable generation, end-semester exam results, ML prediction, mobile app, SMS.

**Assumptions**
- The 75% attendance minimum comes from university rules, so it is a setting that can be changed.
- The internal-marks cutoff (default: below 40% of the maximum) is our team's choice and can also be changed.
- Each course section has one faculty member.
- The college supplies the student lists.

**Default risk rules** (stored in a RiskRule table that the HOD can edit)

| Condition | Status |
|---|---|
| Attendance ≥ 75% | Normal |
| Attendance 65–74.99% (the band many universities allow to be condoned) | Warning |
| Attendance < 65% | At-Risk |
| Any internal test below 40% of its maximum | At-Risk |
| Below a cutoff in 2 or more courses | At-Risk |

**Functional requirements**
- FR1: Login, with role-based access control (RBAC).
- FR2: Admin creates and edits students, faculty, courses, sections and enrolments, and can import them from CSV.
- FR3: Faculty creates a class session (date and period).
- FR4: Faculty marks each enrolled student Present, Absent or Late (P/A/L).
- FR5: Faculty can edit attendance for 48 hours, after which it locks. Every edit is logged.
- FR6: Faculty defines assessments (name and maximum marks).
- FR7: Faculty enters or uploads marks. Each mark must be between 0 and the maximum.
- FR8: Attendance % is recalculated after every submission.
- FR9: Risk rules are checked after every attendance or marks change.
- FR10: The mentor and student are notified when the student's status changes.
- FR11: The mentor records an intervention (such as counselling or a remedial class) and closes it when done.
- FR12: Students view their own attendance, marks and status, including how many classes they still need to attend.
- FR13: The HOD views a department dashboard and an at-risk list, and can export it as CSV.
- FR14: The HOD or Admin sets the thresholds.
- FR15: An audit log records every change to marks or attendance.

**Non-functional requirements**
- **Security:** passwords hashed with bcrypt, access checked on the server, HTTPS.
- **Privacy:** students see only their own records.
- **Performance:** saving attendance for a class of 60 takes under 2 seconds.
- **Usability:** works on mobile; meets the basic WCAG 2.1 AA accessibility checks.
- **Reliability:** daily backups; submitting the same form twice loses no data.
- **Maintainability:** thresholds are stored as data, not in code; a new member can set up the project from the README in 10 minutes or less.

## Stage 2: Process model

**Choice:** Agile Scrum with 2 short sprints, tracked on the Jira board.

**Why it fits**
- The deadline is short (19 to 27 Nov), so we need working pieces every few days, not one big delivery at the end.
- The work splits cleanly into two halves. Sprint 1 is the documents and design, Sprint 2 is the build and testing.
- Each sprint ends with a review and a short retro, so mistakes in the design get caught before coding starts.
- The Jira board shows every task moving across the columns day by day. That is the tracking evidence the CCA marks.
- We still write the SRS and the design up front, in Sprint 1, so nothing the guidelines ask for is skipped.

**Why not Incremental:** we first planned Incremental with 5 increments over about 6 weeks. When the 27 Nov deadline was confirmed there was no room for 5 increments, so we moved to 2 Scrum sprints.

**Sprints**

| Sprint | Dates | Goal |
|---|---|---|
| Sprint 1 | 19 to 22 Nov | Requirements, design and plan done |
| Sprint 2 | 23 to 26 Nov | Attendance and marks working, tested, report ready |
| Submission | 27 Nov | Final check and submit |

Each sprint has planning on day 1, short daily updates on WhatsApp, and a review plus retro on the last day.

## Stage 3: Plan

**Work breakdown structure (WBS)**

| ID | Work package | Owner | Sprint | Due | Depends on |
|---|---|---|---|---|---|
| 1 | Requirements: problem statement, actors, survey, SRS, use cases | S1 | 1 | 20 to 21 Nov | none |
| 2 | Planning: process model, WBS, Gantt chart, risks, board | S4 | 1 | 20 to 21 Nov | none |
| 3 | Design: ER diagram, architecture, DFDs, data dictionary | S2 | 1 | 21 to 22 Nov | 1 |
| 4 | Sequence diagram and student status state diagram | S1 | 1 | 22 Nov | 3 |
| 5 | Development: attendance (23 Nov), marks and risk rules (24 Nov) | S3 | 2 | 23 to 24 Nov | 3 |
| 6 | Testing: tests and test case table | S3 | 2 | 25 Nov | 5 |
| 7 | Ethics table and professional responsibility statement | S1, S4 | 2 | 24 Nov | 1 |
| 8 | Report, slides, deployment doc, rehearsal | S4 (all) | 2 | 25 to 26 Nov | all |

**Milestones**
- **M1:** Requirements and plan done (20 to 21 Nov)
- **M2:** Design frozen, Sprint 1 review (22 Nov)
- **M3:** Attendance module working (23 Nov)
- **M4:** Marks and risk rules working (24 Nov)
- **M5:** Testing done, report and slides final (26 Nov)
- **M6:** Submission (27 Nov)

**Risks**

| Risk | Mitigation |
|---|---|
| Scope creep (biometrics, ML) | Stick to the out-of-scope list |
| Members busy or unavailable | Give every task a backup person, and use 27 Nov as the buffer day |
| S3 overloaded as the only developer | S2 writes the database schema and sample data |
| Diagrams don't match each other | Check DFD balancing at M2 |
| Little Git experience, merge conflicts | One branch per feature; small pull requests (PRs) |
| Real student data ends up in the repo | Use made-up data only; check `.gitignore` |
| Threshold rules unclear | Make them settings and list them as assumptions |
| Deployment fails on demo day | Run locally and keep a recorded backup video |

## Stage 4: Design

### DFD Level 0

The whole system is one process. It exchanges data with five external entities:

| Entity | Sends to the system | Receives from the system |
|---|---|---|
| Admin | Course, user and enrolment data | Confirmations |
| Faculty | Attendance and marks | Class summaries |
| Mentor | Intervention notes | Risk alerts |
| HOD | Threshold settings | Department reports |
| Student | Login and view requests | Their attendance, marks and status |

### DFD Level 1

**Processes**
- 1.0 Manage users and academic setup
- 2.0 Record attendance
- 3.0 Record internal marks
- 4.0 Evaluate academic risk
- 5.0 Manage interventions and notifications
- 6.0 Generate reports

**Data stores**
- D1 Users
- D2 Courses/Enrolments
- D3 Attendance
- D4 Marks
- D5 RiskRules
- D6 RiskFlags
- D7 Interventions/Notifications

### DFD Level 2: process 4.0, Evaluate academic risk

**Inputs**
- A trigger (student and course) from process 2.0 or 3.0
- Data read from D3 (Attendance), D4 (Marks) and D5 (RiskRules)

**Outputs**
- Status written to D6 (RiskFlags)
- A status-change alert sent to process 5.0

**Sub-processes**
- 4.1 Fetch attendance % and marks
- 4.2 Apply the threshold rules
- 4.3 Compare with the current status and update the flag
- 4.4 Raise a status-change alert

**Balancing:** Level 2 must have exactly the same inputs and outputs as process 4.0 at Level 1.

### Data dictionary (key entries)
- `attendance_entry = session_id + student_id + status`, where `status = [P|A|L]`
- `attendance_pct = (P + L) / total_sessions × 100`
- `mark_entry = assessment_id + student_id + marks_obtained (0..max_marks)`
- `risk_flag = student_id + course_id + status + reasons{rule_id} + flagged_on`
- `risk_rule = rule_id + metric + operator + threshold + severity`
- `intervention = flag_id + mentor_id + action + notes + date + outcome`

### Sequence diagram: faculty submits attendance

**Participants:** Faculty, UI, AttendanceController, AttendanceService, DB, RiskService, NotificationService, Mentor.

**Normal flow**
1. Faculty selects the session and submits the attendance list.
2. The list is validated and saved.
3. Attendance % is recalculated.
4. The risk rules are checked. A student's status moves from Normal to At-Risk.
5. A flag is saved, and an alert goes to the mentor and the student.
6. Faculty sees a success screen with "2 students newly flagged".

**Error and alternative flows**
- **(a)** The faculty member does not teach this section: the request is refused (403).
- **(b)** Attendance for this session is already recorded: the system offers to edit it within the 48-hour window.
- **(c)** The record is locked (older than 48 hours): the change is rejected and must be requested from the HOD.
- **(d)** The notification fails: the attendance is still saved, and the alert is queued and retried.

### Student status states

| From | To | When |
|---|---|---|
| Normal | Warning | Attendance falls into the 65–74.99% band |
| Warning | At-Risk | Attendance falls below 65% |
| Normal | At-Risk | A marks rule fires (test below 40%, or below a cutoff in 2 or more courses) |
| At-Risk | Under Intervention | The mentor opens a case |
| Under Intervention | Resolved | The student is back above the thresholds, or the mentor closes the case |
| Resolved | Normal | Automatically, once the case is resolved |
| Warning or At-Risk | Normal | Automatically, if the student recovers before any intervention |

### Architecture

| Layer | Technology |
|---|---|
| Presentation | Server-rendered HTML pages with Bootstrap |
| Application | Flask routes and services (attendance, marks, risk, notify) |
| Data | MySQL (SQLite during development) |
| External | SMTP email |

- **Why this stack:** we already know Python and SQL, and it is one simple stack with no build step.
- **Deployment:** run Flask and MySQL on a laptop or a college lab server. Optionally use the free tier of Render or PythonAnywhere for the demo.
- **Scalability:** one department is easy to handle. To grow, add more app workers and a database index on `(student_id, course_id)`.
- **Bottlenecks:**
  - A single database gets a burst of writes when many faculty submit at the end of a period.
  - Risk rules are recalculated on every submission.
  - Email is sent while the user waits.
  - Later fix: a job queue and caching.

### ER entities
User (role), Student, Faculty, Course, Section, Enrollment, ClassSession, AttendanceRecord, Assessment, MarkEntry, RiskRule, RiskFlag, Intervention, Notification, AuditLog

## Stage 5: Repository

**Folders**
- `/requirements`: SRS, use cases, survey
- `/planning`: WBS, Gantt chart, risks, board exports
- `/diagrams`: `.drawio` source files and `.png` exports
- `/src`: app code, tests and `seed_synthetic.sql` (made-up sample data)
- `/report`
- `/presentation`
- `README.md`

**Branches**
- `main` is protected.
- Work happens on branches such as `feature/srs`, `feature/dfd`, `feature/attendance`, `feature/marks` and `docs/report`.
- Every pull request is reviewed by one other member before merging.
- Commit messages reference the issue they close, for example "Closes #12".

**Housekeeping:** keep `.env` out of Git and use made-up data only.

**Task board: Jira Free**, linked to the repo with the free "GitHub for Atlassian" app.
- Columns: Backlog / To Do / In Progress / Review / Done.
- Every issue has an owner, priority and due date. Epics serve as milestones and the 2 sprints follow the plan above.
- Put the Jira issue key in each commit and PR (e.g. `AAM-12 add attendance form`) so they appear on the Jira issue.
- Invite the professor by email early and confirm they can open the board (Jira Free has no public link).
- Backup: a public GitHub Project, which anyone can open from a URL.

## Stage 6: Ethics

| Issue | Mitigation |
|---|---|
| Privacy of marks and attendance | Access by role: students see only their own data, mentors see only their mentees |
| Consent | Students are mostly adults, so parents are notified only if the student opts in. A privacy notice explains what is collected and why. Collect only what is needed (in line with India's data protection law, the DPDP Act) |
| Security | Passwords hashed with bcrypt; checked against the OWASP Top 10 (e.g. SQL injection, broken access control); no secrets in the repo; HTTPS |
| Stigma of the "At-Risk" label | Only the student, mentor and HOD can see it; supportive wording such as "Needs support"; no public lists |
| Accuracy of risk flags | Fixed rules that state their reason; a mentor reviews before any action; audit log; marks editable only within the edit window |
| Bias (medical leave, disability, sports duty) | Approved leave is not counted as absence; the mentor can override with a recorded reason |
| Accessibility | Labelled forms, keyboard navigation, good contrast; works on low-end phones |
| Data retention | Archive records after the course ends; daily backups |
| Licensing and IP | Only MIT/BSD-licensed libraries (Flask, Bootstrap) and our own icons; cite every source; add a LICENSE file |

**Professional responsibility.** We collect only the data we need and keep it confidential. We state the system's limits clearly: the risk rules are fixed thresholds, not predictions, and the thresholds depend on university regulations. Every member understands the whole project and takes responsibility for it.

## Stage 7: Demo (every member speaks)

| Item | Speaker |
|---|---|
| Problem, users, scope | S1 |
| Process model and why we chose it | S4 |
| Task board: tasks, owners, milestones, status | S4 |
| DFD Level 0 → 1 → 2 and balancing | S2 |
| Live scenario: attendance submitted → student flagged → mentor intervenes → Resolved (explain the state transitions) | S3, with S1 narrating the sequence diagram |
| Architecture, stack, deployment, bottlenecks | S2 |
| GitHub: README, folders, commits, PRs | S3 |
| Ethics table | S1 |

**Contribution evidence:** commits per member, task-board assignees, and a contribution table in the report.

## To verify
- The 75% attendance rule: sources disagree on whether the UGC itself requires it. Many universities allow a 65–74% band to be condoned.
- The 40% internal-marks cutoff: no standard source found. It is our own choice.
- The details of the DPDP Act: not checked against the official text yet. Don't cite them as settled.

## Sources
- [UGC attendance guidelines](https://bhattandjoshiassociates.com/ugc-guidelines-on-attendance-and-gujarat-universitys-policy/)
- [Kerala University condonation](https://www.keralauniversity.ac.in/pdfs/news/Condonation1602068779.pdf)
- [NIT Kurukshetra attendance rules](https://nitkkr.ac.in/wp-content/uploads/2024/11/Revised-Attendance-Rules-as-per-UG-PG-Regulations-for-appearing-in-the-End-Semester-Examination-from-Academic-Year-2024-25-onwards.pdf)
- [Classter early-warning systems](https://www.classter.com/blog/edtech/early-warning-system-launch/)
- [Ken42: at-risk indicators](https://ken42.com/blog/how-to-identify-at-risk-students-using-predictive-analytics)
- [Transparent early-warning framework (arXiv)](https://arxiv.org/pdf/2412.09483v1.pdf)
- [DPDP Act and student data](https://ksandk.com/md/data-protection-and-data-privacy/dpdp-compliance-for-schools-and-edtech/)
