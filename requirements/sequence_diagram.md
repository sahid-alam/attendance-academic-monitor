# Sequence Diagram: Faculty Submits Attendance
## Online Student Attendance & Academic Monitoring System

**Author:** S1 – Requirements & Analysis Lead  
**Version:** 1.0 | **Date:** 22 November 2026  
**Scenario:** The core scenario that runs through the DFD Level 2, state diagram, code, and live demo.

---

## Participants

| Participant | Role |
|---|---|
| Faculty | The user who submits the attendance list |
| UI (Browser) | The HTML page rendered by Flask/Bootstrap |
| AttendanceController | The Flask route handler (`POST /attendance/submit`) |
| AttendanceService | Business logic: validate, save, calculate % |
| DB | SQLite / MySQL database (stores D3, D6, D7) |
| RiskService | Business logic: apply risk rules (FR9) |
| NotificationService | Business logic: send in-app + email alerts (FR10) |
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

    Faculty->>UI: Select session, mark P/A/L for each student, click Submit
    UI->>AC: POST /attendance/submit {session_id, [{student_id, status}]}

    AC->>AS: validate_and_save(session_id, entries, faculty_id)

    AS->>DB: SELECT section owner WHERE session_id = ?
    DB-->>AS: faculty_id of section owner

    alt Faculty is NOT authorised for this section
        AS-->>AC: Error: 403 Forbidden
        AC-->>UI: HTTP 403 "You are not assigned to this section"
        UI-->>Faculty: Error page
    else Session already has records (edit path)
        AS->>DB: SELECT recorded_at WHERE session_id = ?
        DB-->>AS: recorded_at timestamp
        alt recorded_at is > 48 hours ago (locked)
            AS-->>AC: Error: session locked
            AC-->>UI: "This session is locked. Contact the HOD."
            UI-->>Faculty: Lock message
        else Within 48-hour window (edit allowed)
            AS->>DB: UPDATE attendance_record SET status = ? (upsert)
            AS->>DB: INSERT INTO audit_log (old_value, new_value, changed_by, changed_at)
            DB-->>AS: OK
        end
    else First submission
        AS->>DB: INSERT attendance_record for each student (P/A/L)
        AS->>DB: UPDATE class_session SET recorded_at = NOW()
        DB-->>AS: OK
    end

    Note over AS,DB: FR8 — Recalculate attendance %
    AS->>DB: SELECT COUNT(*) P+L / total_sessions per student
    DB-->>AS: attendance_pct for each student

    Note over AS,RS: FR9 — Evaluate risk rules
    AS->>RS: evaluate_risk(student_id, course_id, attendance_pct)
    RS->>DB: SELECT rules FROM risk_rule WHERE active = 1
    DB-->>RS: rule set (R1–R5)
    RS->>DB: SELECT current status FROM risk_flag WHERE student_id = ? AND course_id = ?
    DB-->>RS: current_status (e.g. Normal)

    RS->>RS: Apply rules → new_status = At-Risk

    alt Status has changed (Normal → At-Risk)
        RS->>DB: UPDATE risk_flag SET status = At-Risk, triggered_rules = [R3], flagged_on = NOW()
        DB-->>RS: OK
        RS->>NS: notify_status_change(student_id, mentor_id, old=Normal, new=At-Risk, rules=[R3])

        Note over NS: FR10 — Send notifications
        NS->>DB: INSERT notification for Mentor (in-app)
        NS->>DB: INSERT notification for Student (in-app)
        DB-->>NS: OK

        NS-->>Mentor: Email: "[AAM] Student needs attention — Attendance dropped below 65%"
        NS-->>Faculty: (async, no blocking) notification queued

        alt SMTP email fails
            NS->>DB: INSERT notification_retry queue
            Note over NS: Attendance save is NOT rolled back
        end

        RS-->>AS: status_changed = True, flagged_count += 1
    else Status unchanged
        RS-->>AS: status_changed = False
    end

    AS-->>AC: Result {saved: 60, flagged: 2}
    AC-->>UI: HTTP 200 "Attendance saved. 2 students newly flagged as At-Risk."
    UI-->>Faculty: Success screen with flagged student count
```

---

## Normal Flow — Step-by-Step Description

| Step | Actor | Description |
|---|---|---|
| 1 | Faculty | Selects the session and marks each of the 60 enrolled students P, A, or L. Clicks Submit. |
| 2 | UI | Sends a POST request to `AttendanceController` with the session ID and the full status list. |
| 3 | AttendanceController | Delegates to `AttendanceService` with the faculty's identity from the session. |
| 4 | AttendanceService | Verifies the faculty is assigned to the section. |
| 5 | AttendanceService | Verifies the session is not locked. |
| 6 | AttendanceService | Saves all attendance records; sets `recorded_at` if this is the first submission. |
| 7 | AttendanceService | Recalculates attendance % for every student in the section (FR8). |
| 8 | RiskService | Fetches active rules, reads current risk flags, applies rules, and determines the new status for each student. |
| 9 | RiskService | For students whose status changed: updates D6 and calls `NotificationService`. |
| 10 | NotificationService | Writes in-app notifications to D7 and sends emails to the mentor and student. |
| 11 | AttendanceController | Returns a success response: "Attendance saved. 2 students newly flagged." |
| 12 | UI | Displays the success screen to the faculty. |

---

## Alternative and Error Flows

| Flow | Trigger | Outcome |
|---|---|---|
| **A — Unauthorised faculty** | Faculty does not teach the selected section | HTTP 403 returned immediately. No data written. |
| **B — Duplicate submission (edit)** | Attendance already recorded; within 48-hour window | Existing records are updated (upsert). Audit log entry written. Risk re-evaluated. |
| **C — Locked session** | Attendance is older than 48 hours | Edit rejected. Error message shown. Faculty directed to HOD. Rejected attempt logged in audit log. |
| **D — Notification failure** | SMTP server unreachable | Attendance and risk flag saved normally. Email queued in `notification_retry` table. Faculty sees no error message. |

---

## Notes for the Demo

- This diagram covers **FR4, FR5, FR8, FR9, FR10, and FR15** in one flow.
- During the live demo, S3 runs the code while S1 narrates using this diagram.
- The "2 students newly flagged" message on the success screen is the observable output of the whole pipeline.
