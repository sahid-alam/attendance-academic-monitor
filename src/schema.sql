-- =====================================================================
--  AAM-20 : Database schema (SQLite, for development)
--  Online Student Attendance & Academic Monitoring System
--  Owner: S2 (Design & Database)        Used by: S3 (/src code)
--  Same tables and columns as schema_mysql.sql, the ER diagram and the
--  data dictionary. MySQL version (production): schema_mysql.sql
--
--  Run:   sqlite3 app.db < schema.sql
--         sqlite3 app.db < seed_synthetic.sql
--  Note: SQLite has no ON UPDATE, so the app sets updated_at / updated_on.
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS v_test_pct;
DROP VIEW  IF EXISTS v_attendance_pct;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS interventions;
DROP TABLE IF EXISTS risk_flag_reasons;
DROP TABLE IF EXISTS risk_flags;
DROP TABLE IF EXISTS risk_rules;
DROP TABLE IF EXISTS mark_entries;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS class_sessions;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS faculty;
DROP TABLE IF EXISTS users;

-- 1. users : one login per person; role drives RBAC (FR1)
CREATE TABLE users (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      VARCHAR(100) NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,                 -- bcrypt hash only
    role           TEXT NOT NULL CHECK (role IN ('admin','faculty','mentor','hod','student')),
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. faculty : teaching staff (also mentors and HODs)
CREATE TABLE faculty (
    faculty_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    employee_code  VARCHAR(20) NOT NULL UNIQUE,
    department     VARCHAR(60) NOT NULL,
    designation    VARCHAR(50)
);

-- 3. students : each has one mentor; parent emailed only with consent
CREATE TABLE students (
    student_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    roll_no         VARCHAR(20) NOT NULL UNIQUE,
    department      VARCHAR(60) NOT NULL,
    semester        INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    mentor_id       INTEGER REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    parent_email    VARCHAR(120),
    parent_consent  INTEGER NOT NULL DEFAULT 0 CHECK (parent_consent IN (0,1))
);

-- 4. courses
CREATE TABLE courses (
    course_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code   VARCHAR(20)  NOT NULL UNIQUE,
    course_name   VARCHAR(100) NOT NULL,
    department    VARCHAR(60)  NOT NULL,
    semester      INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    credits       INTEGER NOT NULL DEFAULT 3
);

-- 5. sections : a course runs in sections; each section has one faculty member
CREATE TABLE sections (
    section_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id      INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    section_name   VARCHAR(10) NOT NULL,
    academic_year  VARCHAR(9)  NOT NULL,
    faculty_id     INTEGER NOT NULL REFERENCES faculty(faculty_id),
    CONSTRAINT uq_section UNIQUE (course_id, section_name, academic_year)
);

-- 6. enrollments : student <-> section (M:N bridge)
CREATE TABLE enrollments (
    enrollment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id     INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    section_id     INTEGER NOT NULL REFERENCES sections(section_id) ON DELETE CASCADE,
    enrolled_on    TEXT NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_enrollment UNIQUE (student_id, section_id)
);

-- 7. class_sessions : one class (date + period) (FR3)
--    UNIQUE stops double recording; edits allowed until submitted_at + 48 h (FR5)
CREATE TABLE class_sessions (
    session_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id     INTEGER NOT NULL REFERENCES sections(section_id) ON DELETE CASCADE,
    session_date   TEXT    NOT NULL,
    period         INTEGER NOT NULL CHECK (period BETWEEN 1 AND 10),
    created_by     INTEGER NOT NULL REFERENCES faculty(faculty_id),
    submitted_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_session UNIQUE (section_id, session_date, period)
);

-- 8. attendance_records : session_id + student_id + status (P/A/L) (FR4)
CREATE TABLE attendance_records (
    record_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id     INTEGER NOT NULL REFERENCES class_sessions(session_id) ON DELETE CASCADE,
    student_id     INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    status         TEXT NOT NULL CHECK (status IN ('P','A','L')),
    marked_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TEXT,
    CONSTRAINT uq_attendance UNIQUE (session_id, student_id)
);
CREATE INDEX idx_att_student ON attendance_records (student_id);

-- 9. assessments : name + max marks (FR6)
CREATE TABLE assessments (
    assessment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id     INTEGER NOT NULL REFERENCES sections(section_id) ON DELETE CASCADE,
    name           VARCHAR(50) NOT NULL,
    max_marks      DECIMAL(5,2) NOT NULL CHECK (max_marks > 0),
    held_on        TEXT,
    created_by     INTEGER NOT NULL REFERENCES faculty(faculty_id),
    CONSTRAINT uq_assessment UNIQUE (section_id, name)
);

-- 10. mark_entries : assessment_id + student_id + marks_obtained (FR7)
--     marks_obtained <= max_marks is checked by the Marks Service
CREATE TABLE mark_entries (
    mark_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id   INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    student_id      INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    marks_obtained  DECIMAL(5,2) NOT NULL CHECK (marks_obtained >= 0),
    entered_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT,
    CONSTRAINT uq_mark UNIQUE (assessment_id, student_id)
);

-- 11. risk_rules : thresholds are data, not code; HOD/Admin edits (FR14)
CREATE TABLE risk_rules (
    rule_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name       VARCHAR(100) NOT NULL,
    metric          TEXT NOT NULL CHECK (metric IN ('attendance_pct','test_pct','courses_below_cutoff')),
    operator        TEXT NOT NULL CHECK (operator IN ('<','<=','>=','BETWEEN')),
    threshold       DECIMAL(6,2) NOT NULL,
    threshold_high  DECIMAL(6,2),
    severity        TEXT NOT NULL CHECK (severity IN ('WARNING','AT_RISK')),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    updated_by      INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    updated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_between CHECK (operator <> 'BETWEEN' OR threshold_high IS NOT NULL)
);

-- 12. risk_flags : student status (course_id NULL = "2 or more courses" rule)
CREATE TABLE risk_flags (
    flag_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id    INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
    status       TEXT NOT NULL DEFAULT 'NORMAL'
                 CHECK (status IN ('NORMAL','WARNING','AT_RISK','UNDER_INTERVENTION','RESOLVED')),
    flagged_on   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_on   TEXT,
    is_current   INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0,1))
);
CREATE INDEX idx_flag_student_course ON risk_flags (student_id, course_id);

-- 12a. risk_flag_reasons : which rule(s) caused a flag
CREATE TABLE risk_flag_reasons (
    flag_id       INTEGER NOT NULL REFERENCES risk_flags(flag_id) ON DELETE CASCADE,
    rule_id       INTEGER NOT NULL REFERENCES risk_rules(rule_id),
    actual_value  DECIMAL(6,2) NOT NULL,
    PRIMARY KEY (flag_id, rule_id)
);

-- 13. interventions : mentor cases (FR11)
CREATE TABLE interventions (
    intervention_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    flag_id          INTEGER NOT NULL REFERENCES risk_flags(flag_id) ON DELETE CASCADE,
    mentor_id        INTEGER NOT NULL REFERENCES faculty(faculty_id),
    action           TEXT NOT NULL CHECK (action IN ('Counselling','Remedial class','Parent meeting','Other')),
    notes            TEXT,
    opened_on        TEXT NOT NULL DEFAULT CURRENT_DATE,
    closed_on        TEXT,
    outcome          VARCHAR(255),
    status           TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','CLOSED'))
);

-- 14. notifications : email + in-app alerts; QUEUED ones are retried (FR10)
CREATE TABLE notifications (
    notification_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    flag_id          INTEGER REFERENCES risk_flags(flag_id) ON DELETE SET NULL,
    channel          TEXT NOT NULL CHECK (channel IN ('EMAIL','IN_APP')),
    message          VARCHAR(500) NOT NULL,
    status           TEXT NOT NULL DEFAULT 'QUEUED' CHECK (status IN ('QUEUED','SENT','FAILED')),
    attempts         INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at          TEXT
);
CREATE INDEX idx_notif_status ON notifications (status);

-- 15. audit_log : every change to marks or attendance (FR5, FR15)
CREATE TABLE audit_log (
    log_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    table_name   VARCHAR(40) NOT NULL,
    record_id    INTEGER NOT NULL,
    action       TEXT NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
    old_value    TEXT,                                    -- JSON text
    new_value    TEXT,                                    -- JSON text
    reason       VARCHAR(255),
    changed_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_table_record ON audit_log (table_name, record_id);

-- attendance_pct = (P + L) / total_sessions x 100   (per student, per course)
CREATE VIEW v_attendance_pct AS
SELECT  ar.student_id,
        sec.course_id,
        COUNT(*)                                                 AS total_sessions,
        SUM(ar.status IN ('P','L'))                              AS attended,
        ROUND(100.0 * SUM(ar.status IN ('P','L')) / COUNT(*), 2) AS attendance_pct
FROM attendance_records ar
JOIN class_sessions cs ON cs.session_id = ar.session_id
JOIN sections sec      ON sec.section_id = cs.section_id
GROUP BY ar.student_id, sec.course_id;

-- test_pct = marks_obtained / max_marks x 100   (per student, per assessment)
CREATE VIEW v_test_pct AS
SELECT  me.student_id,
        sec.course_id,
        a.assessment_id,
        a.name                                             AS assessment,
        me.marks_obtained,
        a.max_marks,
        ROUND(100.0 * me.marks_obtained / a.max_marks, 2)  AS test_pct
FROM mark_entries me
JOIN assessments a ON a.assessment_id = me.assessment_id
JOIN sections sec  ON sec.section_id  = a.section_id;
