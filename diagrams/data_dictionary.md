# Data Dictionary – Online Student Attendance & Academic Monitoring System

- **Jira:** AAM-24 · **Owner:** S2 (Design & Database) · **Stage 4 – Design**
- **Matches:** ER diagram (AAM-20), `schema.sql`, DFD Level 0/1/2 (AAM-21/22/23)

All names below are the same as the tables and columns in the ER diagram and `schema.sql`.

## 1. Notation

| Symbol | Meaning |
|---|---|
| `=` | is composed of |
| `+` | and |
| <code>[ a &#124; b ]</code> | either a or b (one of) |
| `{ x }` | x repeated one or more times |
| `( x )` | x is optional |
| `** text **` | comment |
| **PK / FK / UQ** | primary key / foreign key / unique |

## 2. Key data items (composite)

These are the items named in the project plan, written with the ER names.

```
attendance_entry  = session_id + student_id + status
status            = [ "P" | "A" | "L" ]            ** Present | Absent | Late **

attendance_pct    = (count(P) + count(L)) / total_sessions × 100
                    ** per student, per course; Late counts as attended **

mark_entry        = assessment_id + student_id + marks_obtained
marks_obtained    = 0 .. max_marks                ** checked by Marks Service **
test_pct          = marks_obtained / max_marks × 100

risk_rule         = rule_id + rule_name + metric + operator + threshold
                    + (threshold_high) + severity + is_active
metric            = [ "attendance_pct" | "test_pct" | "courses_below_cutoff" ]
operator          = [ "<" | "<=" | ">=" | "BETWEEN" ]
severity          = [ "WARNING" | "AT_RISK" ]

risk_flag         = flag_id + student_id + (course_id) + status
                    + { reason } + flagged_on
reason            = rule_id + actual_value        ** stored in risk_flag_reasons **
status (flag)     = [ "NORMAL" | "WARNING" | "AT_RISK"
                    | "UNDER_INTERVENTION" | "RESOLVED" ]
                    ** course_id is empty for the "2 or more courses" rule **

intervention      = intervention_id + flag_id + mentor_id + action + (notes)
                    + opened_on + (closed_on) + (outcome) + status
action            = [ "Counselling" | "Remedial class" | "Parent meeting" | "Other" ]

notification      = notification_id + recipient_id + (flag_id) + channel
                    + message + status + attempts + created_at + (sent_at)
channel           = [ "EMAIL" | "IN_APP" ]

class_session     = session_id + section_id + session_date + period
                    + created_by + submitted_at
                    ** editable until submitted_at + 48 hours, then locked **
```

## 3. Data flows (from the DFDs)

| Data flow | Composition | From → To |
|---|---|---|
| trigger | `student_id + course_id` | 2.0 / 3.0 → 4.0 (4.1) |
| attendance_list | `session_id + { student_id + status }` | Faculty → 2.0 |
| marks_list | `assessment_id + { student_id + marks_obtained }` | Faculty → 3.0 |
| new_status | `student_id + (course_id) + status + { reason }` | 4.2 → 4.3 |
| status_change_alert | `student_id + (course_id) + old_status + new_status + { reason }` | 4.4 → 5.0 |
| risk_alert | `status_change_alert + mentor email` | 5.0 → Mentor |
| intervention_notes | `flag_id + action + (notes) + (outcome)` | Mentor → 5.0 |
| threshold_settings | `{ rule_id + threshold + (threshold_high) + is_active }` | HOD → 1.0 |
| class_summary | `section_id + session_date + present_count + absent_count + newly_flagged_count` | 2.0 → Faculty |
| department_report | `{ roll_no + course_code + attendance_pct + test_pct + status }` (CSV) | 6.0 → HOD |
| student_view | `{ course_code + attendance_pct + test_pct + status } + classes_still_needed` | 6.0 → Student |

## 4. Data stores (DFD) → tables (ER)

| DFD store | Tables |
|---|---|
| D1 Users | `users`, `faculty`, `students` |
| D2 Courses / Enrolments | `courses`, `sections`, `enrollments` |
| D3 Attendance | `class_sessions`, `attendance_records` |
| D4 Marks | `assessments`, `mark_entries` |
| D5 RiskRules | `risk_rules` |
| D6 RiskFlags | `risk_flags`, `risk_flag_reasons` |
| D7 Interventions / Notifications | `interventions`, `notifications` |
| (audit, used by 2.0 and 3.0) | `audit_log` |

## 5. Data elements by table

### users
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| user_id | INT | PK | Unique user number | 7 |
| full_name | VARCHAR(100) | required | Person's name | Kabir Singh |
| email | VARCHAR(120) | UQ | Login and email address | kabir@college.test |
| password_hash | VARCHAR(255) | required | bcrypt hash, never plain text | $2b$12$… |
| role | ENUM | admin / faculty / mentor / hod / student | Decides what the user can see (RBAC) | student |
| is_active | BOOLEAN | default TRUE | Account enabled | TRUE |
| created_at | DATETIME | default now | When the account was made | 2026-11-01 09:00 |

### faculty
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| faculty_id | INT | PK | Unique faculty number | 2 |
| user_id | INT | FK → users, UQ | Login of this faculty member | 3 |
| employee_code | VARCHAR(20) | UQ | College staff code | FAC102 |
| department | VARCHAR(60) | required | Department | CSE |
| designation | VARCHAR(50) | optional | Job title | Associate Professor |

### students
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| student_id | INT | PK | Unique student number | 3 |
| user_id | INT | FK → users, UQ | Login of this student | 7 |
| roll_no | VARCHAR(20) | UQ | College roll number | CSE2303 |
| department | VARCHAR(60) | required | Department | CSE |
| semester | TINYINT | 1–8 | Current semester | 5 |
| mentor_id | INT | FK → faculty, optional | Assigned mentor | 2 |
| parent_email | VARCHAR(120) | optional | Parent contact | parent.kabir@mail.test |
| parent_consent | BOOLEAN | default FALSE | Parent is emailed only if TRUE (student opt-in) | TRUE |

### courses
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| course_id | INT | PK | Unique course number | 1 |
| course_code | VARCHAR(20) | UQ | Course code | CS501 |
| course_name | VARCHAR(100) | required | Course title | Software Engineering |
| department | VARCHAR(60) | required | Offering department | CSE |
| semester | TINYINT | 1–8 | Semester it is taught in | 5 |
| credits | TINYINT | default 3 | Credits | 4 |

### sections
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| section_id | INT | PK | Unique section number | 1 |
| course_id | INT | FK → courses | Course this section belongs to | 1 |
| section_name | VARCHAR(10) | UQ with course + year | Section label | A |
| academic_year | VARCHAR(9) | required | Academic year | 2026-27 |
| faculty_id | INT | FK → faculty | The one faculty who teaches it | 1 |

### enrollments
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| enrollment_id | INT | PK | Unique enrolment number | 5 |
| student_id | INT | FK → students | Student | 3 |
| section_id | INT | FK → sections, UQ with student | Section joined | 1 |
| enrolled_on | DATE | default today | Date of enrolment | 2026-11-01 |

### class_sessions
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| session_id | INT | PK | Unique class number | 9 |
| section_id | INT | FK → sections | Section taught | 1 |
| session_date | DATE | UQ with section + period | Date of the class | 2026-11-12 |
| period | TINYINT | 1–10 | Period number | 2 |
| created_by | INT | FK → faculty | Faculty who recorded it | 1 |
| submitted_at | DATETIME | default now | Start of the 48-hour edit window | 2026-11-12 11:00 |

### attendance_records
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| record_id | INT | PK | Unique record number | 35 |
| session_id | INT | FK → class_sessions | Class | 9 |
| student_id | INT | FK → students, UQ with session | Student | 3 |
| status | ENUM | P / A / L | Present, Absent or Late | L |
| marked_at | DATETIME | default now | When first saved | 2026-11-12 11:00 |
| updated_at | DATETIME | auto on edit | Last edit time | 2026-11-12 15:30 |

### assessments
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| assessment_id | INT | PK | Unique test number | 2 |
| section_id | INT | FK → sections | Section the test is for | 2 |
| name | VARCHAR(50) | UQ with section | Test name | Internal Test 1 |
| max_marks | DECIMAL(5,2) | > 0 | Maximum marks | 20.00 |
| held_on | DATE | optional | Test date | 2026-11-13 |
| created_by | INT | FK → faculty | Faculty who defined it | 2 |

### mark_entries
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| mark_id | INT | PK | Unique mark number | 7 |
| assessment_id | INT | FK → assessments | Test | 2 |
| student_id | INT | FK → students, UQ with assessment | Student | 3 |
| marks_obtained | DECIMAL(5,2) | 0 .. max_marks | Marks scored | 6.00 |
| entered_at | DATETIME | default now | When first saved | 2026-11-15 10:00 |
| updated_at | DATETIME | auto on edit | Last edit time | NULL |

### risk_rules
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| rule_id | INT | PK | Unique rule number | 2 |
| rule_name | VARCHAR(100) | required | Readable name, shown as the reason | Attendance below 65% |
| metric | ENUM | see section 2 | What is measured | attendance_pct |
| operator | ENUM | < / <= / >= / BETWEEN | How it is compared | < |
| threshold | DECIMAL(6,2) | required | Limit (lower limit for BETWEEN) | 65.00 |
| threshold_high | DECIMAL(6,2) | needed for BETWEEN | Upper limit of a band | NULL |
| severity | ENUM | WARNING / AT_RISK | Status given when the rule fires | AT_RISK |
| is_active | BOOLEAN | default TRUE | Rule switched on | TRUE |
| updated_by | INT | FK → users | HOD/Admin who last changed it | 4 |
| updated_at | DATETIME | auto | Last change | 2026-11-01 10:00 |

### risk_flags
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| flag_id | INT | PK | Unique flag number | 2 |
| student_id | INT | FK → students | Flagged student | 3 |
| course_id | INT | FK → courses, optional | Course (empty = multi-course rule) | 1 |
| status | ENUM | see section 2 | Current student status | UNDER_INTERVENTION |
| flagged_on | DATETIME | default now | When the flag was raised | 2026-11-13 11:00 |
| updated_on | DATETIME | auto on edit | Last status change | 2026-11-16 09:00 |
| is_current | BOOLEAN | default TRUE | FALSE for old, replaced flags | TRUE |

### risk_flag_reasons
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| flag_id | INT | PK, FK → risk_flags | Flag | 2 |
| rule_id | INT | PK, FK → risk_rules | Rule that fired | 2 |
| actual_value | DECIMAL(6,2) | required | Value that broke the rule | 60.00 |

### interventions
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| intervention_id | INT | PK | Unique case number | 1 |
| flag_id | INT | FK → risk_flags | Flag being handled | 2 |
| mentor_id | INT | FK → faculty | Mentor in charge | 2 |
| action | ENUM | see section 2 | Type of support | Counselling |
| notes | TEXT | optional | Mentor's notes | Agreed weekly check-in |
| opened_on | DATE | default today | Case opened | 2026-11-16 |
| closed_on | DATE | optional | Case closed | NULL |
| outcome | VARCHAR(255) | optional | Result | NULL |
| status | ENUM | OPEN / CLOSED | Case state | OPEN |

### notifications
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| notification_id | INT | PK | Unique alert number | 3 |
| recipient_id | INT | FK → users | Who receives it | 3 |
| flag_id | INT | FK → risk_flags, optional | Related flag | 5 |
| channel | ENUM | EMAIL / IN_APP | How it is sent | EMAIL |
| message | VARCHAR(500) | required | Alert text | Diya Patel is At-Risk in CS502… |
| status | ENUM | QUEUED / SENT / FAILED | Delivery state (queued alerts are retried) | QUEUED |
| attempts | TINYINT | default 0 | Send attempts so far | 1 |
| created_at | DATETIME | default now | When created | 2026-11-15 10:00 |
| sent_at | DATETIME | optional | When delivered | NULL |

### audit_log
| Field | Type | Key / rule | Description | Example |
|---|---|---|---|---|
| log_id | BIGINT | PK | Unique log number | 1 |
| user_id | INT | FK → users | Who made the change | 2 |
| table_name | VARCHAR(40) | required | Table changed | attendance_records |
| record_id | INT | required | Row changed | 35 |
| action | ENUM | INSERT / UPDATE / DELETE | Kind of change | UPDATE |
| old_value | JSON | optional | Value before | {"status": "A"} |
| new_value | JSON | optional | Value after | {"status": "L"} |
| reason | VARCHAR(255) | optional | Why it was changed | Arrived late; marked absent by mistake |
| changed_at | DATETIME | default now | When | 2026-11-12 15:30 |

## 6. Derived values (views, not stored)

| Name | Formula | Source |
|---|---|---|
| attendance_pct | `(count(P) + count(L)) / total_sessions × 100` | view `v_attendance_pct` |
| test_pct | `marks_obtained / max_marks × 100` | view `v_test_pct` |
| courses_below_cutoff | number of courses where any attendance or test rule fires (WARNING or AT_RISK) | computed by Risk Service (4.2) |
| classes_still_needed | classes the student must attend to reach 75% | computed by Report Service (6.0) |

## 7. Default risk rules (data in `risk_rules`)

| rule_id | Condition | Status |
|---|---|---|
| – | Attendance ≥ 75% and no rule fires | NORMAL |
| 1 | attendance_pct BETWEEN 65 AND 74.99 | WARNING |
| 2 | attendance_pct < 65 | AT_RISK |
| 3 | test_pct < 40 | AT_RISK |
| 4 | courses_below_cutoff ≥ 2 (e.g. Warning in 2 courses) | AT_RISK |

The 75% minimum comes from university rules and the 40% marks cutoff is the team's choice. Both are stored as data so the HOD can change them.
