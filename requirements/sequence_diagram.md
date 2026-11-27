# Sequence Diagram: Faculty Submits Attendance
## Online Student Attendance & Academic Monitoring System

**Author:** S1 – Requirements & Analysis Lead  
**Version:** 1.1 | **Date:** 25 November 2026  
**Matches:** `src/schema.sql` (AAM-20) and `diagrams/data_dictionary.md` (AAM-24)  
**Scenario:** The core scenario that runs through the DFD Level 2, state diagram, code, and live demo.

---

## Participants

| Participant | Role |
|---|---|
| Faculty | The user who submits the attendance list |
| UI (Browser) | The HTML page rendered by Flask/Bootstrap |
| AttendanceController | The Flask route handler (`POST /section/<section_id>/attendance` and `POST /session/<session_id>`) |
| AttendanceService | Business logic: validate, save, calculate % |
| DB | SQLite / MySQL database (`class_sessions`, `attendance_records`, `risk_rules`, `risk_flags`, `risk_flag_reasons`, `notifications`, `audit_log`) |
| RiskService | Business logic: apply risk rules (FR9) |
| NotificationService | Business logic: create `IN_APP` + `EMAIL` alerts in `notifications` (FR10) |
| Mentor | Receives the status-change notification |

---

## Sequence Diagram (Mermaid)

```mermaid
sequenceDiagram
    actor Faculty
    participant UI as UI (Browser)
    participant AC as AttendanceController
    participant AS as AttendanceService
    participant DB
    participant RS as RiskService
    participant NS as NotificationService
    actor Mentor

    Faculty->>UI: Select section/session, mark P/A/L for each student, click Submit
    UI->>AC: POST /section/<section_id>/attendance {session_date, period, [{student_id, status}]}

    AC->>AS: submit_or_edit_attendance(section_id, session_date, period, entries, faculty_id)

    AS->>DB: SELECT faculty_id FROM sections WHERE section_id = ?
    DB-->>AS: faculty_id of section owner

    alt Faculty is NOT authorised for this section
        AS-->>AC: Error: 403 Forbidden
        AC-->>UI: HTTP 403 "You are not assigned to this section"
        UI-->>Faculty: Error page
    else Session already exists in class_sessions (edit path)
        AS->>DB: SELECT session_id, submitted_at FROM class_sessions WHERE section_id = ? AND session_date = ? AND period = ?
        DB-->>AS: session_id, submitted_at timestamp
        alt NOW() > submitted_at + 48 hours (locked)
            AS-->>AC: Error: session locked
            AC-->>UI: "This session is locked (older than 48 h). Contact the HOD."
            UI-->>Faculty: Lock message
        else Within 48-hour window (edit allowed)
            AS->>DB: UPDATE attendance_records SET status = ?, updated_at = CURRENT_TIMESTAMP
            AS->>DB: INSERT INTO audit_log (user_id, table_name, record_id, action, old_value, new_value, changed_at)
            DB-->>AS: OK
        end
    else First submission
        AS->>DB: INSERT INTO class_sessions (section_id, session_date, period, created_by, submitted_at)
        AS->>DB: INSERT INTO attendance_records (session_id, student_id, status, marked_at)
        DB-->>AS: OK
    end

    Note over AS,DB: FR8 — Recalculate attendance % (via v_attendance_pct)
    AS->>DB: SELECT attendance_pct FROM v_attendance_pct WHERE student_id IN (...) AND course_id = ?
    DB-->>AS: attendance_pct for each student

    Note over AS,RS: FR9 — Evaluate risk rules
    AS->>RS: evaluate_risk(student_id, course_id, attendance_pct)
    RS->>DB: SELECT * FROM risk_rules WHERE is_active = 1
    DB-->>RS: active rules (rule_id 1..4)
    RS->>DB: SELECT flag_id, status FROM risk_flags WHERE student_id = ? AND course_id = ? AND is_current = 1
    DB-->>RS: current status (e.g. NORMAL)

    RS->>RS: Apply rules → new_status = AT_RISK (rule_id 2)

    alt Status has changed (NORMAL → AT_RISK)
        RS->>DB: UPDATE risk_flags SET is_current = 0, updated_on = CURRENT_TIMESTAMP WHERE flag_id = ?
        RS->>DB: INSERT INTO risk_flags (student_id, course_id, status, flagged_on, is_current) VALUES (?, ?, 'AT_RISK', CURRENT_TIMESTAMP, 1)
        RS->>DB: INSERT INTO risk_flag_reasons (flag_id, rule_id, actual_value)
        DB-->>RS: OK (new flag_id)

        RS->>NS: notify_status_change(student_id, mentor_id, flag_id, old='NORMAL', new='AT_RISK', reason)

        Note over NS: FR10 — Create notifications in `notifications` table
        NS->>DB: INSERT INTO notifications (recipient_id, flag_id, channel, message, status) VALUES (mentor_user_id, flag_id, 'IN_APP', msg, 'SENT')
        NS->>DB: INSERT INTO notifications (recipient_id, flag_id, channel, message, status) VALUES (student_user_id, flag_id, 'IN_APP', msg, 'SENT')
        NS->>DB: INSERT INTO notifications (recipient_id, flag_id, channel, message, status) VALUES (mentor_user_id, flag_id, 'EMAIL', msg, 'QUEUED')
        DB-->>NS: OK

        NS-->>Mentor: SMTP Email: "[AAM] Student needs attention — Attendance dropped below 65%"

        alt SMTP email succeeds
            NS->>DB: UPDATE notifications SET status = 'SENT', attempts = attempts + 1, sent_at = CURRENT_TIMESTAMP
        else SMTP email fails
            NS->>DB: UPDATE notifications SET status = 'QUEUED', attempts = attempts + 1
            Note over NS: Queued alert will be retried; attendance save is NOT rolled back
        end

        RS-->>AS: status_changed = True, newly_flagged += 1
    else Status unchanged
        RS-->>AS: status_changed = False
    end

    AS-->>AC: Result {saved: 60, newly_flagged: 2}
    AC-->>UI: HTTP 200 "Attendance saved. 2 students newly flagged."
    UI-->>Faculty: Success screen with newly flagged count (status label hidden from Faculty)
```

---

## Normal Flow — Step-by-Step Description

| Step | Actor | Description |
|---|---|---|
| 1 | Faculty | Selects the section, date, and period and marks each enrolled student P, A, or L. Clicks Submit. |
| 2 | UI | Sends a POST request to `AttendanceController` (`/section/<section_id>/attendance`) with the session info and status list. |
| 3 | AttendanceController | Delegates to `AttendanceService` with the faculty's identity from the session. |
| 4 | AttendanceService | Verifies `sections.faculty_id` matches the logged-in faculty member. |
| 5 | AttendanceService | Checks whether `class_sessions` already has an entry and whether `submitted_at + 48 hours` has passed. |
| 6 | AttendanceService | Inserts into `class_sessions` (setting `submitted_at = CURRENT_TIMESTAMP`) and `attendance_records`. |
| 7 | AttendanceService | Queries `v_attendance_pct` to recalculate attendance % for every student in the section (FR8). |
| 8 | RiskService | Reads active rules from `risk_rules` (`is_active = 1`) and current flags from `risk_flags` (`is_current = 1`), evaluates rules, and determines the new status (`NORMAL`, `WARNING`, `AT_RISK`). |
| 9 | RiskService | For students whose status changed: marks old flag `is_current = 0`, inserts new row in `risk_flags`, inserts rule reason into `risk_flag_reasons`, and calls `NotificationService`. |
| 10 | NotificationService | Inserts `IN_APP` and `EMAIL` records into `notifications`; sends SMTP email and marks `SENT` (or leaves `QUEUED` for retry). |
| 11 | AttendanceController | Returns a success response: `"Attendance saved. 2 students newly flagged."` |
| 12 | UI | Displays the success screen to the faculty without exposing individual `AT_RISK` labels on the faculty view. |

---

## Alternative and Error Flows

| Flow | Trigger | Outcome |
|---|---|---|
| **A — Unauthorised faculty** | `sections.faculty_id` does not match the logged-in faculty | HTTP 403 returned immediately. No data written to `class_sessions` or `attendance_records`. |
| **B — Duplicate submission (edit)** | `class_sessions` row already exists and `NOW() <= submitted_at + 48 hours` | Existing rows in `attendance_records` are updated (`updated_at` set). An `UPDATE` entry is written to `audit_log` with `user_id`, `old_value`, and `new_value`. Risk is re-evaluated. |
| **C — Locked session** | `NOW() > class_sessions.submitted_at + 48 hours` | Edit rejected. Error message shown. Faculty directed to HOD for override. |
| **D — Notification failure** | SMTP server unreachable | `class_sessions`, `attendance_records`, and `risk_flags` stay committed. The `EMAIL` row in `notifications` remains `status = 'QUEUED'` with incremented `attempts` for later retry. Faculty sees no error. |

---

## Notes for the Demo

- This diagram covers **FR4, FR5, FR8, FR9, FR10, and FR15** in one flow using exact table and column names from `src/schema.sql` (AAM-20) and `diagrams/data_dictionary.md` (AAM-24).
- During the live demo, S3 runs the code while S1 narrates using this diagram.
- The `"N newly flagged"` message on the success screen is the observable output of the whole pipeline.
