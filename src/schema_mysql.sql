-- =====================================================================
--  AAM-20 : Database schema
--  Online Student Attendance & Academic Monitoring System
--  Database : MySQL 8.0.16+ (production). SQLite version for development: schema.sql
--  Backend  : Flask + SQLAlchemy
--  Owner    : S2 (Design & Database)      Used by: S3 (/src)
--
--  Entities (from the project plan, Stage 4):
--    User, Student, Faculty, Course, Section, Enrollment, ClassSession,
--    AttendanceRecord, Assessment, MarkEntry, RiskRule, RiskFlag,
--    Intervention, Notification, AuditLog
--  + risk_flag_reasons : bridge table for "reasons{rule_id}" in a flag
--
--  Run:   mysql -u root -p < schema_mysql.sql
--  Then:  mysql -u root -p aam_db < seed_synthetic.sql
-- =====================================================================

DROP DATABASE IF EXISTS aam_db;
CREATE DATABASE aam_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aam_db;

-- ---------------------------------------------------------------------
-- 1. users : one login per person. role drives RBAC (FR1).
--    Mentor and HOD are faculty members with an extra role.
-- ---------------------------------------------------------------------
CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,                 -- bcrypt hash only
    role           ENUM('admin','faculty','mentor','hod','student') NOT NULL,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. faculty : teaching staff (also used for mentors and HODs)
-- ---------------------------------------------------------------------
CREATE TABLE faculty (
    faculty_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL UNIQUE,
    employee_code  VARCHAR(20)  NOT NULL UNIQUE,
    department     VARCHAR(60)  NOT NULL,
    designation    VARCHAR(50),
    CONSTRAINT fk_faculty_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. students : each student has one mentor (a faculty member).
--    Parent has no login; notices go to parent only if consent is given.
-- ---------------------------------------------------------------------
CREATE TABLE students (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL UNIQUE,
    roll_no         VARCHAR(20)  NOT NULL UNIQUE,
    department      VARCHAR(60)  NOT NULL,
    semester        TINYINT      NOT NULL CHECK (semester BETWEEN 1 AND 8),
    mentor_id       INT,
    parent_email    VARCHAR(120),
    parent_consent  BOOLEAN      NOT NULL DEFAULT FALSE,  -- opt-in (ethics)
    CONSTRAINT fk_students_user   FOREIGN KEY (user_id)   REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_students_mentor FOREIGN KEY (mentor_id) REFERENCES faculty(faculty_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. courses
-- ---------------------------------------------------------------------
CREATE TABLE courses (
    course_id     INT AUTO_INCREMENT PRIMARY KEY,
    course_code   VARCHAR(20)  NOT NULL UNIQUE,
    course_name   VARCHAR(100) NOT NULL,
    department    VARCHAR(60)  NOT NULL,
    semester      TINYINT      NOT NULL CHECK (semester BETWEEN 1 AND 8),
    credits       TINYINT      NOT NULL DEFAULT 3
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. sections : one course can run in several sections.
--    Assumption: each section has one faculty member.
-- ---------------------------------------------------------------------
CREATE TABLE sections (
    section_id     INT AUTO_INCREMENT PRIMARY KEY,
    course_id      INT          NOT NULL,
    section_name   VARCHAR(10)  NOT NULL,                 -- e.g. 'A'
    academic_year  VARCHAR(9)   NOT NULL,                 -- e.g. '2026-27'
    faculty_id     INT          NOT NULL,
    CONSTRAINT uq_section UNIQUE (course_id, section_name, academic_year),
    CONSTRAINT fk_sections_course  FOREIGN KEY (course_id)  REFERENCES courses(course_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_sections_faculty FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6. enrollments : which student is in which section (M:N bridge)
-- ---------------------------------------------------------------------
CREATE TABLE enrollments (
    enrollment_id  INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    section_id     INT NOT NULL,
    enrolled_on    DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT uq_enrollment UNIQUE (student_id, section_id),
    CONSTRAINT fk_enr_student FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_enr_section FOREIGN KEY (section_id) REFERENCES sections(section_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7. class_sessions : one class (date + period) of a section (FR3).
--    UNIQUE stops the same session being recorded twice (alt flow b).
--    Edits allowed until submitted_at + 48 hours (FR5, alt flow c).
-- ---------------------------------------------------------------------
CREATE TABLE class_sessions (
    session_id     INT AUTO_INCREMENT PRIMARY KEY,
    section_id     INT      NOT NULL,
    session_date   DATE     NOT NULL,
    period         TINYINT  NOT NULL CHECK (period BETWEEN 1 AND 10),
    created_by     INT      NOT NULL,                     -- faculty
    submitted_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_session UNIQUE (section_id, session_date, period),
    CONSTRAINT fk_sess_section FOREIGN KEY (section_id) REFERENCES sections(section_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_sess_faculty FOREIGN KEY (created_by) REFERENCES faculty(faculty_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8. attendance_records : attendance_entry = session_id + student_id + status
--    status = P (present) | A (absent) | L (late)     (FR4)
-- ---------------------------------------------------------------------
CREATE TABLE attendance_records (
    record_id      INT AUTO_INCREMENT PRIMARY KEY,
    session_id     INT      NOT NULL,
    student_id     INT      NOT NULL,
    status         ENUM('P','A','L') NOT NULL,
    marked_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_attendance UNIQUE (session_id, student_id),  -- double submit safe
    CONSTRAINT fk_att_session FOREIGN KEY (session_id) REFERENCES class_sessions(session_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_att_student FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE,
    INDEX idx_att_student (student_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9. assessments : a test defined by faculty (name + max marks)  (FR6)
-- ---------------------------------------------------------------------
CREATE TABLE assessments (
    assessment_id  INT AUTO_INCREMENT PRIMARY KEY,
    section_id     INT          NOT NULL,
    name           VARCHAR(50)  NOT NULL,                 -- e.g. 'Internal Test 1'
    max_marks      DECIMAL(5,2) NOT NULL CHECK (max_marks > 0),
    held_on        DATE,
    created_by     INT          NOT NULL,
    CONSTRAINT uq_assessment UNIQUE (section_id, name),
    CONSTRAINT fk_asmt_section FOREIGN KEY (section_id) REFERENCES sections(section_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_asmt_faculty FOREIGN KEY (created_by) REFERENCES faculty(faculty_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 10. mark_entries : mark_entry = assessment_id + student_id + marks_obtained
--     0 <= marks_obtained <= assessments.max_marks  (FR7)
--     (upper bound is in another table, so the Marks Service checks it)
-- ---------------------------------------------------------------------
CREATE TABLE mark_entries (
    mark_id         INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id   INT          NOT NULL,
    student_id      INT          NOT NULL,
    marks_obtained  DECIMAL(5,2) NOT NULL CHECK (marks_obtained >= 0),
    entered_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_mark UNIQUE (assessment_id, student_id),
    CONSTRAINT fk_mark_asmt    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_mark_student FOREIGN KEY (student_id)    REFERENCES students(student_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 11. risk_rules : risk_rule = rule_id + metric + operator + threshold + severity
--     Thresholds are data, not code; the HOD/Admin edits them (FR14).
--     BETWEEN uses threshold .. threshold_high (for the 65-74.99 band).
-- ---------------------------------------------------------------------
CREATE TABLE risk_rules (
    rule_id         INT AUTO_INCREMENT PRIMARY KEY,
    rule_name       VARCHAR(100) NOT NULL,
    metric          ENUM('attendance_pct','test_pct','courses_below_cutoff') NOT NULL,
    operator        ENUM('<','<=','>=','BETWEEN') NOT NULL,
    threshold       DECIMAL(6,2) NOT NULL,
    threshold_high  DECIMAL(6,2) NULL,
    severity        ENUM('WARNING','AT_RISK') NOT NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    updated_by      INT,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_between CHECK (operator <> 'BETWEEN' OR threshold_high IS NOT NULL),
    CONSTRAINT fk_rule_user FOREIGN KEY (updated_by) REFERENCES users(user_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12. risk_flags : risk_flag = student_id + course_id + status
--                              + reasons{rule_id} + flagged_on
--     Student status states: NORMAL, WARNING, AT_RISK,
--                            UNDER_INTERVENTION, RESOLVED
--     course_id is NULL for the "2 or more courses" rule.
-- ---------------------------------------------------------------------
CREATE TABLE risk_flags (
    flag_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT      NOT NULL,
    course_id    INT      NULL,
    status       ENUM('NORMAL','WARNING','AT_RISK','UNDER_INTERVENTION','RESOLVED')
                 NOT NULL DEFAULT 'NORMAL',
    flagged_on   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_on   DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    is_current   BOOLEAN  NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_flag_student FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_flag_course  FOREIGN KEY (course_id)  REFERENCES courses(course_id)
        ON DELETE CASCADE,
    INDEX idx_flag_student_course (student_id, course_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12a. risk_flag_reasons : which rule(s) caused a flag (explainable flags)
-- ---------------------------------------------------------------------
CREATE TABLE risk_flag_reasons (
    flag_id       INT          NOT NULL,
    rule_id       INT          NOT NULL,
    actual_value  DECIMAL(6,2) NOT NULL,                  -- e.g. 62.50 (%)
    PRIMARY KEY (flag_id, rule_id),
    CONSTRAINT fk_reason_flag FOREIGN KEY (flag_id) REFERENCES risk_flags(flag_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_reason_rule FOREIGN KEY (rule_id) REFERENCES risk_rules(rule_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 13. interventions : intervention = flag_id + mentor_id + action + notes
--                                    + date + outcome          (FR11)
-- ---------------------------------------------------------------------
CREATE TABLE interventions (
    intervention_id  INT AUTO_INCREMENT PRIMARY KEY,
    flag_id          INT  NOT NULL,
    mentor_id        INT  NOT NULL,
    action           ENUM('Counselling','Remedial class','Parent meeting','Other') NOT NULL,
    notes            TEXT,
    opened_on        DATE NOT NULL DEFAULT (CURRENT_DATE),
    closed_on        DATE NULL,
    outcome          VARCHAR(255),
    status           ENUM('OPEN','CLOSED') NOT NULL DEFAULT 'OPEN',
    CONSTRAINT fk_int_flag   FOREIGN KEY (flag_id)   REFERENCES risk_flags(flag_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_int_mentor FOREIGN KEY (mentor_id) REFERENCES faculty(faculty_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 14. notifications : email + in-app alerts (FR10).
--     If email fails, attendance is still saved; alert stays QUEUED
--     and is retried (alt flow d).
-- ---------------------------------------------------------------------
CREATE TABLE notifications (
    notification_id  INT AUTO_INCREMENT PRIMARY KEY,
    recipient_id     INT          NOT NULL,              -- users.user_id
    flag_id          INT          NULL,
    channel          ENUM('EMAIL','IN_APP') NOT NULL,
    message          VARCHAR(500) NOT NULL,
    status           ENUM('QUEUED','SENT','FAILED') NOT NULL DEFAULT 'QUEUED',
    attempts         TINYINT      NOT NULL DEFAULT 0,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at          DATETIME     NULL,
    CONSTRAINT fk_notif_user FOREIGN KEY (recipient_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notif_flag FOREIGN KEY (flag_id)      REFERENCES risk_flags(flag_id)
        ON DELETE SET NULL,
    INDEX idx_notif_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 15. audit_log : every change to marks or attendance (FR5, FR15)
-- ---------------------------------------------------------------------
CREATE TABLE audit_log (
    log_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT,
    table_name   VARCHAR(40) NOT NULL,                   -- e.g. 'attendance_records'
    record_id    INT         NOT NULL,
    action       ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    old_value    JSON        NULL,
    new_value    JSON        NULL,
    reason       VARCHAR(255),
    changed_at   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL,
    INDEX idx_audit_table_record (table_name, record_id)
) ENGINE=InnoDB;

-- =====================================================================
-- Views used by the Risk Service (process 4.1 "Fetch attendance % and marks")
-- =====================================================================

-- attendance_pct = (P + L) / total_sessions x 100   (per student, per course)
CREATE VIEW v_attendance_pct AS
SELECT  ar.student_id,
        sec.course_id,
        COUNT(*)                                            AS total_sessions,
        SUM(ar.status IN ('P','L'))                         AS attended,
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
        a.name                                          AS assessment,
        me.marks_obtained,
        a.max_marks,
        ROUND(100.0 * me.marks_obtained / a.max_marks, 2) AS test_pct
FROM mark_entries me
JOIN assessments a ON a.assessment_id = me.assessment_id
JOIN sections sec  ON sec.section_id  = a.section_id;
