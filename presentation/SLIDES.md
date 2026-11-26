# Presentation slides and speaker notes (AAM-35)

Source: `slides.json`. Rebuild PPTX/PDF and this file with `tools/build_submission.py`.
Target: 10 minutes. Team speaker names and actual rehearsal remain to be confirmed.

## 1. Earlier support starts with reliable records

Speaker: S1 | Target: 25 seconds

ONLINE STUDENT ATTENDANCE & ACADEMIC MONITORING

- A four-person Software Engineering CCA project
- Flask + SQLite attendance prototype; broader monitoring design
- Prepared 26 November 2026 • submission baseline: 27 November

S4 documentation: Madiha Iram

Code baseline: main / 57c0c6a

**Speaker notes:** Introduce the project and all four speakers by their confirmed names. Explain that the talk distinguishes the proposed monitoring system from the attendance prototype we can demonstrate.

## 2. One place to notice a student needs help

Speaker: S1 | Target: 45 seconds

PROBLEM & SCOPE

- Attendance and marks in separate sheets hide emerging problems
- Faculty records events; mentors review explainable support flags
- Admin, Faculty, Mentor, HOD and Student are the five designed roles

Out of scope

Biometrics • ML prediction • SMS

Fees • timetable • mobile app

**Speaker notes:** Explain why early support matters before examination eligibility decisions. Parents have no login; contact needs an appropriate consent process. Avoid claiming survey findings or institutional approvals that are not available.

## 3. Two sprints, with a review before the next step

Speaker: S4 / Madiha Iram | Target: 55 seconds

AAM-13 / AAM-14 • PROCESS MODEL

- 19–22 Nov: requirements, design and planning
- 23–26 Nov: build, verification and submission material
- Daily updates expose blockers; reviews feed the backlog

Why the change?

The original five-increment, six-week schedule exceeded the deadline.

**Speaker notes:** Explain the shift attributed to 19 November in the supplied task summary. Scrum also produces increments; the reason for the change was schedule fit and coordination, not that Incremental cannot work. The diagram is a baseline process, not evidence that meetings happened.

## 4. Make dependencies and late work visible

Speaker: S4 / Madiha Iram | Target: 50 seconds

AAM-15 / AAM-16 / AAM-17 • PLANNING

- WBS assigns outputs, owners, dependencies and review conditions
- Design → build → tests → report → slides → rehearsal
- High risks: integration, developer capacity and late documentation

Original due dates remain visible.

Baseline dates do not establish actual completion.

**Speaker notes:** Describe the WBS support roles and the scored risk register. Report outlining can overlap development, but final results wait for a tested revision. Mention actual late preparation honestly and keep 27 November as the final-check baseline.

## 5. A small app on a relational design

Speaker: S2 | Target: 50 seconds

ARCHITECTURE & DATA

- Server-rendered HTML and Bootstrap → Flask → SQLite
- Users, enrollment and class sessions anchor attendance records
- Schema also models marks, rules, flags, cases, notifications and audit

MySQL DDL is supplied.

The runtime still uses sqlite3.

SMTP is a design target.

**Speaker notes:** Show the existing architecture/ER exports if asked. Explain unique section/date/period and session/student constraints, foreign keys and the percentage view. Tables for a feature do not prove the feature's runtime implementation.

## 6. Trace one scenario through the models

Speaker: S2 | Target: 50 seconds

DFD & BEHAVIORAL DESIGN

- DFD 0: system and five actors; DFD 1: six main processes
- DFD 2 expands risk evaluation and preserves its inputs/outputs
- Intended flow: entry → percentage → risk → mentor support

Main demonstrates entry and percentage.

PR #4 proposes runtime risk and mentor flows.

**Speaker notes:** Explain Level 2 fetching metrics, applying rules, comparing the current flag and raising an alert. Current state is an input for balancing. The proposed behavioral models include Normal, Warning, At-Risk, Under Intervention and Resolved; do not imply all states run on main.

## 7. Live demo: 80% becomes 72.73%

Speaker: S3 | Target: 110 seconds

EXECUTABLE ATTENDANCE SLICE

- Dr. R. Sharma → CS501 → new 26 Nov / period 1 session
- Mark Diya Absent: 8 attended / 11 recorded = 72.73%
- Correct to Present: 9 / 11 = 81.82%; duplicate opens editing

P + L count as attended.

Main does not generate a new risk alert.

Use synthetic data only.

**Speaker notes:** Initialize a disposable database before the talk. Demonstrate the percentage values, duplicate/edit behavior and faculty switch if time permits. Explain the 48-hour lock with tests. If the demo fails, say so and use a clearly labeled static calculation; do not simulate a live alert.

## 8. Eight tests verify the attendance slice

Speaker: S3 | Target: 45 seconds

VERIFICATION & LIMITS

- Percentages, Late, no data and new submissions
- Duplicate rejection, invalid status, edit audit and 48-hour lock
- Selected-faculty ownership and the web form flow

Not established by this suite

Secure login • SMTP • MySQL runtime

Load • accessibility • full role isolation

**Speaker notes:** Cite the fresh verification record for this branch. Explain that PR #4 reports a different suite; those results are not main's results. A passing attendance suite is evidence of the covered behaviors, not a production-readiness certificate.

## 9. A flag should start a conversation

Speaker: S1 | Target: 50 seconds

AAM-33 • PROFESSIONAL RESPONSIBILITY

- Human review, explainable thresholds and a correction route
- Protect privacy, minimize data and require appropriate consent
- Check disability, approved leave and institutional policy

Identity picker ≠ secure login.

75 / 65 / 40 are design assumptions.

Team endorsement remains pending.

**Speaker notes:** Discuss supportive language and no public at-risk lists. No automatic punishment or exam exclusion should follow a threshold. Do not claim DPDP compliance, verified policy or accessibility certification. The statement proposes commitments and lists current implementation gaps.

## 10. Reproduce the demo before presenting it

Speaker: S4 / Madiha Iram | Target: 40 seconds

AAM-36 • DEPLOYMENT

- Create venv → install requirements → initialize synthetic SQLite
- Run tests, then serve on loopback inside the VM
- Back up before reset; init-db drops and recreates tables

No public production deployment claimed.

Real use needs authentication, security review, HTTPS and tested recovery.

**Speaker notes:** Point to report/DEPLOYMENT.md for exact commands and troubleshooting. A cloud VM's loopback is inside the VM, so use its browser or authorized tunnel. Do not expose this identity-picker prototype to real student users.

## 11. Keep contribution evidence reviewable

Speaker: S4 / Madiha Iram | Target: 40 seconds

GIT, JIRA & TEAM HANDOFFS

- S1: requirements and ethics; S2: design and database
- S3: implementation/tests; S4: planning and documentation
- Separate branch, Jira-keyed commits and teammate PR review

Merged: attendance and design.

Pending at inspection: PRs #3, #4, #5.

Allocation is not proof of equal effort.

**Speaker notes:** Show the submission PR and task tracking issues once published. Explain that main is not merged automatically. Link the actual author/reviewer evidence; the role table does not certify attendance or who performed a rehearsal.

## 12. Submission readiness has explicit gates

Speaker: S4 / Madiha Iram | Target: 40 seconds

AAM-34 / AAM-35 / AAM-37 • NEXT CHECKS

- Report, process/planning documents, guide and deck are review artifacts
- Reconcile live Jira criteria and pending integration with the team
- Perform a timed rehearsal; record attendance, fixes and final sign-off

Questions

What is designed? What runs?

What evidence supports each claim?

**Speaker notes:** Close with the implemented attendance outcome and the broader design goal. AAM-37 is still pending until an actual rehearsal is recorded. Invite questions on process choice, data flow and the privacy limits. References: repository plan, Scrum Guide 2020, ACM Code of Ethics and Flask deployment guidance.
