# Software Requirements Specification (SRS)
## Online Student Attendance & Academic Monitoring System

| Field | Detail |
|---|---|
| Document version | 1.0 |
| Date | 22 November 2026 |
| Author | S1 – Requirements & Analysis Lead |
| Project | AAM – Attendance & Academic Monitor |
| Status | Final (Sprint 1) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Functional Requirements (FR1 – FR15)](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Use Case Specifications](#5-use-case-specifications)
6. [Requirements Traceability Matrix](#6-requirements-traceability-matrix)

---

## 1. Introduction

### 1.1 Purpose
This document is the Software Requirements Specification (SRS) for the Online Student Attendance & Academic Monitoring System (AAM). It defines what the system must do, the constraints it must work within, and the quality attributes it must meet. It is the reference for all design, development, and testing work done in Sprint 2.

### 1.2 Scope
**System name:** Online Student Attendance & Academic Monitoring System (AAM)

**What the system does:**
The system is a web application that lets college faculty record attendance and internal marks in one place. It automatically calculates attendance percentages, applies configurable risk rules, and notifies mentors when a student becomes at-risk — early enough for intervention before exam eligibility is affected.

**In scope:**
- Web application with five roles: Admin, Faculty, Mentor, HOD, Student
- Attendance recording per class session (P / A / L)
- Internal marks recording and assessment management
- Rule-based academic risk flagging and notifications
- Mentor intervention tracking
- Dashboard and CSV export for HOD
- In-app and email alerts
- Audit log for every attendance and marks change

**Out of scope:**
- Biometric, RFID, or face-recognition attendance capture
- Student fee management
- Timetable and schedule generation
- End-semester examination results
- Machine-learning–based predictions
- Native mobile application
- SMS notifications

### 1.3 Problem Statement
Colleges currently track attendance in paper registers and internal marks in separate spreadsheets. Students who fall below the attendance requirement or fail internal tests are often identified only when exam eligibility is checked at the semester end — by which point it is too late to help them. The AAM system records both attendance and marks digitally in a single place, calculates risk continuously after every entry, and surfaces at-risk students early so that mentors can intervene.

### 1.4 Definitions

| Term | Meaning |
|---|---|
| P / A / L | Present / Absent / Late — the three attendance statuses |
| Attendance % | `(P + L) / total_sessions × 100` for a student in a course |
| At-Risk | A student whose attendance % or internal marks fall below the configured threshold |
| Warning | A student whose attendance is in the 65–74.99% condonation band |
| Risk Rule | A configurable threshold (metric, operator, threshold value, severity) stored in the database |
| Intervention | A mentoring action (counselling, remedial class, etc.) recorded against a risk flag |
| Audit Log | An immutable record of who changed what attendance or marks entry, and when |
| RBAC | Role-Based Access Control — every server-side route checks the caller's role |
| HOD | Head of Department |
| DPDP Act | India's Digital Personal Data Protection Act, 2023 |

---

## 2. Overall Description

### 2.1 User Classes and Characteristics

| Role | Description | Key permissions |
|---|---|---|
| **Admin** | Sets up the academic environment. Usually an office staff member. | Create/edit users, courses, sections, enrolments; bulk import via CSV |
| **Faculty** | Teaches one or more course sections. Marks attendance and enters internal marks. | Record and edit attendance within 48 h; define assessments; enter marks |
| **Mentor (Faculty Advisor)** | Acts on academic risk alerts for their assigned students. | View risk flags; record interventions; close cases |
| **HOD** | Head of Department. Oversees the full department. | View all dashboards; set risk thresholds; export at-risk CSV |
| **Student** | Enrolled in one or more courses. | View own attendance, marks, risk status, and deficit calculator |
| **Parent** | Secondary stakeholder. No login to the system. | Receives email/in-app notice only if the student explicitly opts in |

### 2.2 Assumptions and Dependencies

1. The 75 % minimum attendance threshold is a university rule and is stored as a configurable setting, not hard-coded.
2. The 40 % internal-marks cutoff is the team's default and is also configurable.
3. Each course section is taught by exactly one faculty member.
4. The college provides the initial student roster; the Admin imports it.
5. An SMTP relay is available for email notifications.
6. The application is deployed on a laptop or college lab server for the demo; for production a service such as PythonAnywhere or Render is used.

### 2.3 Operating Environment

| Layer | Technology |
|---|---|
| Presentation | Server-rendered HTML + Bootstrap (mobile-responsive) |
| Application | Python 3 / Flask |
| Database | SQLite (development) / MySQL (production) |
| External | SMTP email for notifications |

### 2.4 Constraints

- All data shown to a student must be scoped to that student only (privacy constraint).
- Passwords must never be stored in plain text.
- No real student data may appear in the Git repository; only synthetic seed data is used.
- The edit window for attendance is exactly 48 hours from the first submission timestamp.

---

## 3. Functional Requirements

The requirements below trace directly to the DFD Level 1 processes (1.0 – 6.0) and data stores (D1 – D7) defined by S2.

---

### FR1 – Authentication and Role-Based Access Control

**Priority:** High | **DFD process:** 1.0 | **Data store:** D1 Users

**Description:**
Every user must log in with a username and password before accessing any part of the system. The server checks the user's role on every request and denies access if the role does not have permission for that resource.

**Actors:** All roles

**Inputs:**
- Username (email or USN)
- Password (plain text, over HTTPS only)

**Processing:**
1. The server fetches the user record from D1.
2. The submitted password is compared with the stored bcrypt hash.
3. If the hash matches, a server-side session is created containing the `user_id` and `role`.
4. On every subsequent request, the session's role is checked against the route's required role; a mismatch returns HTTP 403.

**Outputs:**
- Successful login → redirect to the role's home dashboard
- Failed login → error message (do not reveal whether username or password was wrong)
- Unauthorised access → HTTP 403 page

**Error conditions:**
- Account does not exist → same error message as a wrong password (prevents enumeration)
- Too many failed attempts → lock the account for 15 minutes (brute-force protection)

---

### FR2 – Admin: Manage Users, Courses, Sections, and Enrolments

**Priority:** High | **DFD process:** 1.0 | **Data store:** D1, D2

**Description:**
The Admin can create, read, update, and delete (CRUD) student records, faculty records, courses, course sections, and student–section enrolments. The Admin can also bulk-import any of these from a CSV file.

**Actors:** Admin

**Inputs:**
- For individual creation: form fields (name, USN/employee ID, email, role, course code, section name, etc.)
- For bulk import: a CSV file with a defined column header row

**Processing:**
1. For individual creation: validate required fields, check for duplicates (e.g., USN uniqueness), write to D1 or D2.
2. For CSV import: parse each row, validate, insert valid rows, collect and display a summary of rows that were rejected and why.
3. All changes are written to the AuditLog (D7).

**Outputs:**
- Confirmation page listing records created / updated
- For CSV import: a row-by-row import report (success count, skip count, reasons)

**Error conditions:**
- Duplicate USN / course code → reject that row and continue with the rest
- Required field missing → validation error shown next to the field
- CSV file has wrong format → reject the whole file with a clear message

---

### FR3 – Faculty: Create a Class Session

**Priority:** High | **DFD process:** 2.0 | **Data store:** D2, D3

**Description:**
Before marking attendance, a faculty member creates a class session by specifying the date and period for a course section they teach.

**Actors:** Faculty

**Inputs:**
- Course / section (selected from a list of sections the faculty member teaches)
- Date (calendar picker)
- Period number or time slot

**Processing:**
1. Verify the faculty member is assigned to the selected section (server-side check).
2. Check for a duplicate session on the same date and period for that section.
3. Create a `class_session` record with `recorded_at` initially NULL (set to current timestamp on first attendance submission).

**Outputs:**
- New session created → redirected to the attendance marking screen for that session

**Error conditions:**
- Faculty does not teach the selected section → HTTP 403
- Session already exists for that date/period → offer to open the existing session instead

---

### FR4 – Faculty: Mark Attendance (P / A / L)

**Priority:** High | **DFD process:** 2.0 | **Data store:** D3

**Description:**
For an open class session, the faculty member marks every enrolled student as Present (P), Absent (A), or Late (L) and submits the list in a single batch.

**Actors:** Faculty

**Inputs:**
- Session ID (from FR3)
- For each enrolled student: status ∈ {P, A, L}

**Processing:**
1. Confirm the session belongs to a section the faculty member teaches.
2. Confirm the session is not locked (see FR5).
3. For each student: upsert an `attendance_record` row (insert on first submission, update on edit).
4. Set `class_session.recorded_at` to the current timestamp if this is the first submission.
5. Trigger FR8 (recalculate attendance %) for each student in the section.
6. Trigger FR9 (evaluate risk rules) for each student.

**Outputs:**
- Success screen: "Attendance saved. 2 students newly flagged."
- FR10 is triggered for any student whose status changed.

**Error conditions:**
- Session is locked → show lock message; direct faculty to HOD for override
- Faculty not authorised for the section → HTTP 403

---

### FR5 – Attendance Edit Window and Locking

**Priority:** High | **DFD process:** 2.0 | **Data store:** D3, D7 AuditLog

**Description:**
Faculty may edit the attendance for a session within 48 hours of the first submission timestamp (`class_session.recorded_at`). After 48 hours the record locks and can only be changed by the HOD.

**Actors:** Faculty (edit), HOD (unlock/override)

**Processing:**
1. On every edit request, the system checks `NOW() - recorded_at`.
2. If `< 48 h`: allow the edit. Write the before/after values and the editor's `user_id` and timestamp to the AuditLog (D7).
3. If `≥ 48 h`: reject the edit, return an error message, and log the rejected attempt.

**Outputs:**
- Successful edit → updated attendance record + audit log entry
- Locked record → error message: "This session is locked. Contact the HOD to request a correction."

---

### FR6 – Faculty: Define Assessments

**Priority:** High | **DFD process:** 3.0 | **Data store:** D4

**Description:**
Faculty can create assessment records (e.g., "Internal Test 1", "Assignment 2") for a course section, specifying the name and the maximum marks achievable.

**Actors:** Faculty

**Inputs:**
- Course / section
- Assessment name (free text, max 100 characters)
- Maximum marks (positive integer)

**Processing:**
1. Verify faculty teaches the section.
2. Validate that maximum marks > 0.
3. Insert into the Assessment table (D4).

**Outputs:**
- Confirmation that the assessment was created
- Updated list of assessments for the course

**Error conditions:**
- Duplicate assessment name in the same section → warn and confirm before saving
- Maximum marks ≤ 0 → validation error

---

### FR7 – Faculty: Enter or Upload Marks

**Priority:** High | **DFD process:** 3.0 | **Data store:** D4

**Description:**
Faculty enters the marks each enrolled student obtained in an assessment. Marks can be entered individually through a form or uploaded as a CSV. Each mark must satisfy `0 ≤ marks_obtained ≤ max_marks`.

**Actors:** Faculty

**Inputs:**
- Assessment ID (from FR6)
- For each enrolled student: marks obtained (numeric)
- Or: a CSV file with columns `usn, marks_obtained`

**Processing:**
1. Validate each value: 0 ≤ value ≤ max_marks; reject non-numeric input.
2. Upsert a `mark_entry` row for each student.
3. Write changes to the AuditLog (D7).
4. Trigger FR9 (evaluate risk rules) for each student whose marks changed.

**Outputs:**
- Confirmation: marks saved for N students
- For CSV: import report (accepted / rejected rows)

**Error conditions:**
- Mark > max_marks or < 0 → reject that row; show the out-of-range value
- Student not enrolled in the section → reject the row

---

### FR8 – Automatic Attendance % Recalculation

**Priority:** High | **DFD process:** 2.0 / 4.0 | **Data store:** D3, D6

**Description:**
Every time attendance is submitted or edited for a session, the system recalculates the attendance percentage for every student in that section and stores the result.

**Actors:** System (triggered automatically after FR4 or FR5)

**Formula:**
```
attendance_pct = (count of P records + count of L records)
                 ─────────────────────────────────────────  × 100
                        total class_sessions held
```

**Processing:**
1. Query `attendance_record` for all sessions in the course for the student.
2. Count P and L statuses. Count total sessions.
3. Compute the percentage; round to two decimal places.
4. Store the result for use by FR9 and FR12.

**Outputs:**
- Updated `attendance_pct` in the student's course record (available to FR9 and FR12)

---

### FR9 – Rule-Based Academic Risk Evaluation

**Priority:** High | **DFD process:** 4.0 (sub-processes 4.1 – 4.4) | **Data stores:** D3, D4, D5, D6

**Description:**
After every attendance submission (FR4 / FR5) or marks entry (FR7), the system evaluates all active risk rules against the affected student's data and updates the student's risk flag status.

**Actors:** System (triggered automatically)

**Default risk rules (configurable via FR14):**

| Rule ID | Metric | Condition | Severity |
|---|---|---|---|
| R1 | attendance_pct | ≥ 75 % | Normal |
| R2 | attendance_pct | 65 – 74.99 % | Warning |
| R3 | attendance_pct | < 65 % | At-Risk |
| R4 | marks_obtained / max_marks | < 40 % for any single test | At-Risk |
| R5 | marks_obtained / max_marks | < cutoff in ≥ 2 courses | At-Risk |

**Processing (sub-processes 4.1 – 4.4):**
1. **4.1 Fetch data:** Read the student's current attendance % (D3) and marks (D4) for the course. Read active rules from D5.
2. **4.2 Apply rules:** Evaluate each rule; determine the highest severity that applies (At-Risk > Warning > Normal).
3. **4.3 Compare and update:** Compare the new severity with the status currently stored in D6. If changed, write the new status, timestamp, and triggered rule IDs to D6.
4. **4.4 Raise alert:** If the status changed, generate an alert event and pass it to FR10.

**Outputs:**
- Updated risk flag in D6
- Alert event passed to FR10 (if status changed)

---

### FR10 – Automated Status-Change Notifications

**Priority:** High | **DFD process:** 5.0 | **Data store:** D7

**Description:**
When a student's risk status changes (detected in FR9), the system sends an in-app notification and an email to the student's mentor and to the student.

**Actors:** System (triggered by FR9)

**Inputs:**
- Student ID, old status, new status, triggered rule IDs (from FR9)

**Processing:**
1. Look up the student's mentor from D1.
2. Create an in-app notification record in D7 for both the mentor and the student.
3. Send an email via SMTP to both.
4. If the email send fails: save the notification to a retry queue in D7; do not roll back the attendance or marks save.

**Outputs:**
- In-app notification visible to mentor and student on next login
- Email to mentor and student

**Message content:**
- Student name, course, old status → new status, the rule that triggered the change, timestamp.
- Wording is supportive: "needs attention" rather than "failed".

**Error conditions:**
- SMTP failure → notification queued for retry; attendance/marks save is not affected

---

### FR11 – Mentor Intervention Tracking

**Priority:** Medium | **DFD process:** 5.0 | **Data store:** D7

**Description:**
When a mentor receives an at-risk alert, they can open an intervention case, record the action taken (e.g., counselling session, remedial class referral), add notes, and later mark the case as resolved.

**Actors:** Mentor

**Inputs (open case):**
- Risk flag ID (from D6)
- Action type (dropdown: counselling, remedial class, parent meeting, other)
- Notes (free text)

**Inputs (close case):**
- Outcome (free text, e.g., "Student attended 3 remedial sessions; attendance now 76 %")

**Processing:**
1. Create an `intervention` record linked to the risk flag in D7.
2. Set the student's risk status to "Under Intervention" in D6.
3. On close: set the outcome, timestamp, and status to "Resolved" in D6. Trigger FR9 to re-evaluate; if the student is now above thresholds, status moves to Normal automatically.

**Outputs:**
- Intervention record visible to mentor and HOD
- Student status updated in D6

---

### FR12 – Student Self-Service Portal and Deficit Calculator

**Priority:** High | **DFD process:** 6.0 | **Data stores:** D3, D4, D6

**Description:**
A logged-in student can view their own attendance percentage, marks, and risk status for each enrolled course. The portal also shows a deficit calculator: how many consecutive classes the student must attend to reach the 75 % threshold.

**Actors:** Student

**Data displayed:**
- Per course: attendance % (updated in real time), course name, faculty name
- Per assessment: marks obtained, max marks, percentage
- Current risk status and the rule that triggered it (if at-risk)
- Deficit calculator result

**Deficit calculator formula:**
```
classes_needed = ceil( (0.75 × (total_sessions + x) - (attended + L)) / 1 )
solve for minimum x ≥ 0 such that (attended + L + x) / (total_sessions + x) ≥ 0.75
```

**Constraints:**
- Student can only see their own records. Any URL that references another student's data returns HTTP 403.

---

### FR13 – HOD Analytics Dashboard and CSV Export

**Priority:** Medium | **DFD process:** 6.0 | **Data stores:** D3, D4, D6

**Description:**
The HOD has a department-level dashboard that shows attendance and marks summaries per course, and a sortable at-risk student list with reason codes. The HOD can export the at-risk list as a CSV.

**Actors:** HOD

**Dashboard panels:**
- Course-level attendance summary (average attendance %, number of at-risk students per course)
- Department-wide at-risk list: student name, USN, course, current status, triggered rules, last-updated timestamp
- Trend over time (last 4 weeks)

**CSV export columns:**
`student_name, usn, course_code, course_name, attendance_pct, risk_status, triggered_rules, last_updated`

**Outputs:**
- Rendered HTML dashboard
- Downloadable `.csv` file (UTF-8, comma-delimited)

---

### FR14 – Dynamic Threshold Configuration

**Priority:** Medium | **DFD process:** 1.0 | **Data store:** D5

**Description:**
The HOD or Admin can view, add, edit, or deactivate risk rules stored in D5 without changing any application code. Changes take effect on the next run of FR9.

**Actors:** HOD, Admin

**Inputs:**
- Rule metric (dropdown: `attendance_pct`, `marks_pct`, `multi_course_deficit`)
- Operator (dropdown: `<`, `<=`, `>=`, `>`)
- Threshold value (numeric)
- Severity (dropdown: Normal, Warning, At-Risk)
- Active flag (boolean)

**Processing:**
1. Validate inputs (threshold must be a number between 0 and 100 for percentage metrics).
2. Write the new or updated rule to D5.
3. The rule is applied by FR9 on the next attendance or marks submission.

**Outputs:**
- Updated rules table displayed to the HOD/Admin
- Confirmation message

---

### FR15 – System Audit Log

**Priority:** High | **DFD process:** all | **Data store:** D7 AuditLog

**Description:**
Every change to an attendance record or a marks entry is recorded in an immutable audit log. The log captures who changed what, the before value, the after value, and the timestamp. The log cannot be edited or deleted by any user role.

**Actors:** System (automatic); HOD (read-only view)

**Fields logged:**

| Field | Description |
|---|---|
| `log_id` | Auto-incremented primary key |
| `table_name` | `attendance_record` or `mark_entry` |
| `record_id` | The PK of the changed row |
| `changed_by` | `user_id` of the actor |
| `change_type` | INSERT, UPDATE, or REJECTED_EDIT |
| `old_value` | JSON snapshot of the row before the change (NULL for INSERT) |
| `new_value` | JSON snapshot of the row after the change |
| `changed_at` | UTC timestamp |

**Outputs:**
- HOD can view the audit log filtered by student, course, or date range
- Log entries cannot be modified or deleted (enforced at the application layer)

---

## 4. Non-Functional Requirements

### 4.1 Security
- Passwords are hashed with bcrypt (cost factor ≥ 12); plain-text passwords are never stored or logged.
- Every server-side route checks the session role before processing the request (RBAC enforced at the server, not only in the UI).
- The application is served over HTTPS only.
- Mitigations are in place for the OWASP Top 10: parameterised queries prevent SQL injection; CSRF tokens protect all state-changing forms; session cookies are `HttpOnly`, `Secure`, and `SameSite=Lax`.
- No secrets (API keys, DB passwords, `.env` files) are committed to the Git repository.

### 4.2 Privacy
- Students can only access their own attendance and marks data; any URL referencing another student's record returns HTTP 403.
- Mentors can only view the records of students assigned to them.
- The at-risk label is visible only to the student, their mentor, and the HOD — not to other students or faculty.
- Parent notifications are sent only if the student has opted in.
- Data collected is limited to what is necessary (data minimisation, in line with the DPDP Act, 2023).

### 4.3 Performance
- Submitting attendance for a class of 60 students (including risk re-evaluation) completes in under 2 seconds on the target server.
- The HOD dashboard loads in under 3 seconds for a department of up to 500 students.

### 4.4 Usability and Accessibility
- All pages are responsive and usable on a mobile screen (minimum 360 px wide).
- The system meets WCAG 2.1 Level AA for contrast ratios, keyboard navigation, and form labelling.
- A new team member should be able to set up and run the project locally by following the README in 10 minutes or less.

### 4.5 Reliability
- Submitting the same attendance form twice (double-click / network retry) produces the same result — no duplicate records (idempotent upsert).
- The database is backed up daily.
- Notification failures (SMTP errors) do not roll back the attendance or marks save.

### 4.6 Maintainability
- Risk thresholds are stored as data in D5, not hard-coded. Changing a threshold requires no code change.
- The codebase follows a layered structure (routes → services → data) so each layer can be changed independently.

---

## 5. Use Case Specifications

### UC-01: Faculty Marks Attendance and Risk Engine Runs

| Field | Detail |
|---|---|
| **Use case ID** | UC-01 |
| **Name** | Faculty marks class attendance |
| **Primary actor** | Faculty |
| **Secondary actors** | System (risk engine), Mentor (notification recipient), Student (notification recipient) |
| **Preconditions** | Faculty is logged in. A class session for today exists (or is created in FR3). The session is not locked. |
| **Trigger** | Faculty navigates to the attendance page for the session and clicks Submit. |

**Main Success Scenario:**

| Step | Actor | Action |
|---|---|---|
| 1 | Faculty | Selects the course section and date. |
| 2 | System | Displays the enrolled student list with P/A/L radio buttons. |
| 3 | Faculty | Marks each student P, A, or L and clicks Submit. |
| 4 | System | Validates that every student has a status. Saves all attendance records. Sets `recorded_at` if first submission. |
| 5 | System | Recalculates attendance % for every student in the section (FR8). |
| 6 | System | Runs risk rules for each student (FR9). |
| 7 | System | For any student whose status changed: saves the new flag (D6) and triggers a notification (FR10). |
| 8 | System | Displays: "Attendance saved. 2 students newly flagged as At-Risk." |

**Alternative and Exception Flows:**

| ID | Condition | System Response |
|---|---|---|
| A1 | Faculty does not teach this section | HTTP 403: "You are not assigned to this section." |
| A2 | Attendance already submitted for this session | Offer to edit within the 48-hour window (FR5). |
| A3 | Session is locked (> 48 h old) | "This session is locked. Contact the HOD for a correction." Reject the submission. |
| A4 | Notification email fails | Attendance is saved normally. Notification is queued for retry. Faculty sees no error. |

---

### UC-02: Risk Flag Raised – Mentor Opens an Intervention

| Field | Detail |
|---|---|
| **Use case ID** | UC-02 |
| **Name** | Mentor responds to an at-risk alert |
| **Primary actor** | Mentor |
| **Preconditions** | A student's risk status changed to At-Risk (triggered by UC-01 or by a marks entry). The mentor has received a notification. |
| **Trigger** | Mentor clicks the notification or navigates to the At-Risk list. |

**Main Success Scenario:**

| Step | Actor | Action |
|---|---|---|
| 1 | Mentor | Logs in; sees the in-app notification badge. |
| 2 | Mentor | Opens the notification; reviews the student's attendance % and the rule that triggered the flag. |
| 3 | Mentor | Clicks "Open Intervention". |
| 4 | Mentor | Selects action type (e.g., Counselling) and enters notes. |
| 5 | System | Creates an intervention record (D7). Updates student's status to "Under Intervention" (D6). |
| 6 | Later — Mentor | Enters outcome text and clicks "Close Case". |
| 7 | System | Marks the case Resolved (D7). Re-runs FR9. If student is above thresholds, sets status to Normal (D6). |

**Exception Flows:**

| ID | Condition | System Response |
|---|---|---|
| E1 | Mentor tries to view a student not assigned to them | HTTP 403. |
| E2 | Student recovers (attendance > 75 %) before the mentor opens a case | FR9 automatically sets status back to Normal; alert is noted as resolved automatically. |

---

### UC-03: Student Checks Attendance and Uses Deficit Calculator

| Field | Detail |
|---|---|
| **Use case ID** | UC-03 |
| **Name** | Student views their academic status |
| **Primary actor** | Student |
| **Preconditions** | Student is logged in. At least one class session has been held. |
| **Trigger** | Student navigates to their dashboard. |

**Main Success Scenario:**

| Step | Actor | Action |
|---|---|---|
| 1 | Student | Logs in. Lands on the student dashboard. |
| 2 | System | Displays a table: one row per enrolled course, showing course name, attendance %, risk status. |
| 3 | Student | Clicks on a course row to see session-level breakdown and assessment marks. |
| 4 | System | Shows each session date and P/A/L, each assessment and marks obtained, and the deficit calculator result. |
| 5 | Student | Reads: "You need to attend 6 more consecutive classes in this course to reach 75 %." |

**Exception Flows:**

| ID | Condition | System Response |
|---|---|---|
| E1 | Student tries to access another student's URL | HTTP 403. |
| E2 | No sessions held yet | Dashboard shows 0 sessions; attendance % shown as "No data yet". |

---

## 6. Requirements Traceability Matrix

| Req ID | Description (short) | Primary Actor | DFD Process | Data Stores | Priority |
|---|---|---|---|---|---|
| FR1 | Login and RBAC | All | 1.0 | D1 | High |
| FR2 | Admin: manage users, courses, enrolments | Admin | 1.0 | D1, D2 | High |
| FR3 | Faculty: create class session | Faculty | 2.0 | D2, D3 | High |
| FR4 | Faculty: mark attendance P/A/L | Faculty | 2.0 | D3 | High |
| FR5 | 48-hour edit window and lock | Faculty, HOD | 2.0 | D3, D7 | High |
| FR6 | Faculty: define assessments | Faculty | 3.0 | D4 | High |
| FR7 | Faculty: enter / upload marks | Faculty | 3.0 | D4, D7 | High |
| FR8 | Auto-recalculate attendance % | System | 2.0 / 4.0 | D3, D6 | High |
| FR9 | Rule-based risk evaluation | System | 4.0 | D3, D4, D5, D6 | High |
| FR10 | Status-change notifications | System | 5.0 | D7 | High |
| FR11 | Mentor intervention tracking | Mentor | 5.0 | D6, D7 | Medium |
| FR12 | Student portal and deficit calculator | Student | 6.0 | D3, D4, D6 | High |
| FR13 | HOD dashboard and CSV export | HOD | 6.0 | D3, D4, D6 | Medium |
| FR14 | Dynamic threshold configuration | HOD, Admin | 1.0 | D5 | Medium |
| FR15 | Audit log | System, HOD | All | D7 | High |
