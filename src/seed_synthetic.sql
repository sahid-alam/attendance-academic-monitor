-- =====================================================================
--  seed_synthetic.sql : MADE-UP sample data for demo and testing
--  (no real student data, as required by the project plan)
--  Works in SQLite (dev) and MySQL (production). Run after the schema:
--    SQLite: sqlite3 app.db < seed_synthetic.sql
--    MySQL : mysql -u root -p aam_db < seed_synthetic.sql
--
--  Demo scenario (same one used in DFD L2, sequence and state diagrams):
--  Faculty submits attendance -> attendance % recalculated -> risk rule
--  fires -> student status changes -> mentor notified.
--
--  Expected results for CS501 (10 sessions):
--    Aarav 100%  NORMAL     Diya 80%  NORMAL
--    Meera  70%  WARNING    Kabir 60% AT_RISK -> UNDER_INTERVENTION
--  CS502 Internal Test 1 (max 20):
--    Diya 7/20 = 35%  -> AT_RISK      Kabir 6/20 = 30% -> AT_RISK
--    Kabir is below a cutoff in 2 courses -> AT_RISK (multi-course rule)
--  password_hash values are placeholders; the app creates real bcrypt hashes.
-- =====================================================================

INSERT INTO users (user_id, full_name, email, password_hash, role) VALUES
 (1, 'System Admin',   'admin@college.test',   'bcrypt_placeholder', 'admin'),
 (2, 'Dr. R. Sharma',  'rsharma@college.test', 'bcrypt_placeholder', 'faculty'),
 (3, 'Prof. P. Verma', 'pverma@college.test',  'bcrypt_placeholder', 'mentor'),
 (4, 'Dr. A. Rao',     'arao@college.test',    'bcrypt_placeholder', 'hod'),
 (5, 'Aarav Mehta',    'aarav@college.test',   'bcrypt_placeholder', 'student'),
 (6, 'Diya Patel',     'diya@college.test',    'bcrypt_placeholder', 'student'),
 (7, 'Kabir Singh',    'kabir@college.test',   'bcrypt_placeholder', 'student'),
 (8, 'Meera Iyer',     'meera@college.test',   'bcrypt_placeholder', 'student');

INSERT INTO faculty (faculty_id, user_id, employee_code, department, designation) VALUES
 (1, 2, 'FAC101', 'CSE', 'Assistant Professor'),
 (2, 3, 'FAC102', 'CSE', 'Associate Professor'),
 (3, 4, 'FAC100', 'CSE', 'Professor and HOD');

INSERT INTO students (student_id, user_id, roll_no, department, semester, mentor_id, parent_email, parent_consent) VALUES
 (1, 5, 'CSE2301', 'CSE', 5, 2, NULL,                     FALSE),
 (2, 6, 'CSE2302', 'CSE', 5, 2, NULL,                     FALSE),
 (3, 7, 'CSE2303', 'CSE', 5, 2, 'parent.kabir@mail.test', TRUE),
 (4, 8, 'CSE2304', 'CSE', 5, 2, NULL,                     FALSE);

INSERT INTO courses (course_id, course_code, course_name, department, semester, credits) VALUES
 (1, 'CS501', 'Software Engineering',        'CSE', 5, 4),
 (2, 'CS502', 'Database Management Systems', 'CSE', 5, 4);

INSERT INTO sections (section_id, course_id, section_name, academic_year, faculty_id) VALUES
 (1, 1, 'A', '2026-27', 1),
 (2, 2, 'A', '2026-27', 2);

INSERT INTO enrollments (student_id, section_id, enrolled_on) VALUES
 (1,1,'2026-11-01'),(2,1,'2026-11-01'),(3,1,'2026-11-01'),(4,1,'2026-11-01'),
 (1,2,'2026-11-01'),(2,2,'2026-11-01'),(3,2,'2026-11-01'),(4,2,'2026-11-01');

-- 10 class sessions of CS501 section A (period 2)
INSERT INTO class_sessions (session_id, section_id, session_date, period, created_by, submitted_at) VALUES
 (1, 1, '2026-11-02', 2, 1, '2026-11-02 11:00:00'),
 (2, 1, '2026-11-03', 2, 1, '2026-11-03 11:00:00'),
 (3, 1, '2026-11-04', 2, 1, '2026-11-04 11:00:00'),
 (4, 1, '2026-11-05', 2, 1, '2026-11-05 11:00:00'),
 (5, 1, '2026-11-06', 2, 1, '2026-11-06 11:00:00'),
 (6, 1, '2026-11-09', 2, 1, '2026-11-09 11:00:00'),
 (7, 1, '2026-11-10', 2, 1, '2026-11-10 11:00:00'),
 (8, 1, '2026-11-11', 2, 1, '2026-11-11 11:00:00'),
 (9, 1, '2026-11-12', 2, 1, '2026-11-12 11:00:00'),
 (10, 1, '2026-11-13', 2, 1, '2026-11-13 11:00:00');

-- Attendance (P = present, A = absent, L = late; L counts as attended)
INSERT INTO attendance_records (session_id, student_id, status, marked_at) VALUES
  (1,1,'P','2026-11-02 11:00:00'), (1,2,'P','2026-11-02 11:00:00'), (1,3,'A','2026-11-02 11:00:00'), (1,4,'P','2026-11-02 11:00:00'),
  (2,1,'P','2026-11-03 11:00:00'), (2,2,'P','2026-11-03 11:00:00'), (2,3,'P','2026-11-03 11:00:00'), (2,4,'A','2026-11-03 11:00:00'),
  (3,1,'P','2026-11-04 11:00:00'), (3,2,'L','2026-11-04 11:00:00'), (3,3,'A','2026-11-04 11:00:00'), (3,4,'P','2026-11-04 11:00:00'),
  (4,1,'P','2026-11-05 11:00:00'), (4,2,'P','2026-11-05 11:00:00'), (4,3,'P','2026-11-05 11:00:00'), (4,4,'P','2026-11-05 11:00:00'),
  (5,1,'P','2026-11-06 11:00:00'), (5,2,'A','2026-11-06 11:00:00'), (5,3,'P','2026-11-06 11:00:00'), (5,4,'A','2026-11-06 11:00:00'),
  (6,1,'P','2026-11-09 11:00:00'), (6,2,'P','2026-11-09 11:00:00'), (6,3,'P','2026-11-09 11:00:00'), (6,4,'P','2026-11-09 11:00:00'),
  (7,1,'P','2026-11-10 11:00:00'), (7,2,'P','2026-11-10 11:00:00'), (7,3,'P','2026-11-10 11:00:00'), (7,4,'L','2026-11-10 11:00:00'),
  (8,1,'P','2026-11-11 11:00:00'), (8,2,'L','2026-11-11 11:00:00'), (8,3,'A','2026-11-11 11:00:00'), (8,4,'P','2026-11-11 11:00:00'),
  (9,1,'P','2026-11-12 11:00:00'), (9,2,'A','2026-11-12 11:00:00'), (9,3,'L','2026-11-12 11:00:00'), (9,4,'A','2026-11-12 11:00:00'),
  (10,1,'P','2026-11-13 11:00:00'), (10,2,'P','2026-11-13 11:00:00'), (10,3,'A','2026-11-13 11:00:00'), (10,4,'P','2026-11-13 11:00:00');

INSERT INTO assessments (assessment_id, section_id, name, max_marks, held_on, created_by) VALUES
 (1, 1, 'Internal Test 1', 20.00, '2026-11-12', 1),
 (2, 2, 'Internal Test 1', 20.00, '2026-11-13', 2);

INSERT INTO mark_entries (assessment_id, student_id, marks_obtained, entered_at) VALUES
 (1,1,18.00,'2026-11-14 10:00:00'),(1,2,15.00,'2026-11-14 10:00:00'),
 (1,3, 9.00,'2026-11-14 10:00:00'),(1,4,12.00,'2026-11-14 10:00:00'),
 (2,1,17.00,'2026-11-15 10:00:00'),(2,2, 7.00,'2026-11-15 10:00:00'),
 (2,3, 6.00,'2026-11-15 10:00:00'),(2,4,13.00,'2026-11-15 10:00:00');

-- Default risk rules from the project plan (HOD can edit these)
-- Attendance >= 75% and no rule firing = NORMAL
INSERT INTO risk_rules (rule_id, rule_name, metric, operator, threshold, threshold_high, severity, updated_by) VALUES
 (1, 'Attendance in condonable band (65-74.99%)', 'attendance_pct',       'BETWEEN', 65.00, 74.99, 'WARNING', 4),
 (2, 'Attendance below 65%',                      'attendance_pct',       '<',       65.00, NULL,  'AT_RISK', 4),
 (3, 'Internal test below 40% of maximum',        'test_pct',             '<',       40.00, NULL,  'AT_RISK', 4),
 (4, 'Below a cutoff in 2 or more courses',       'courses_below_cutoff', '>=',       2.00, NULL,  'AT_RISK', 4);

-- Current flags after the risk rules ran
INSERT INTO risk_flags (flag_id, student_id, course_id, status, flagged_on) VALUES
 (1, 4, 1,    'WARNING',            '2026-11-13 11:00:05'),
 (2, 3, 1,    'UNDER_INTERVENTION', '2026-11-13 11:00:05'),
 (3, 3, 2,    'AT_RISK',            '2026-11-15 10:00:05'),
 (4, 3, NULL, 'AT_RISK',            '2026-11-15 10:00:05'),
 (5, 2, 2,    'AT_RISK',            '2026-11-15 10:00:05');

-- Why each flag was raised (explainable flags)
INSERT INTO risk_flag_reasons (flag_id, rule_id, actual_value) VALUES
 (1, 1, 70.00),
 (2, 2, 60.00),
 (3, 3, 30.00),
 (4, 4,  2.00),
 (5, 3, 35.00);

-- Mentor opened a case for Kabir (At-Risk -> Under Intervention)
INSERT INTO interventions (flag_id, mentor_id, action, notes, opened_on, status) VALUES
 (2, 2, 'Counselling', 'Discussed missed classes; agreed weekly check-in.', '2026-11-16', 'OPEN');

-- Alerts: one email still QUEUED (retry flow when SMTP fails)
INSERT INTO notifications (recipient_id, flag_id, channel, message, status, attempts, created_at, sent_at) VALUES
 (3, 2, 'EMAIL',  'Kabir Singh (CSE2303) is At-Risk in CS501: attendance 60% < 65%.', 'SENT',   1, '2026-11-13 11:00:06', '2026-11-13 11:00:09'),
 (7, 2, 'IN_APP', 'Your attendance in CS501 is 60%. Your mentor will contact you.',  'SENT',   1, '2026-11-13 11:00:06', '2026-11-13 11:00:06'),
 (3, 5, 'EMAIL',  'Diya Patel (CSE2302) is At-Risk in CS502: Internal Test 1 35% < 40%.', 'QUEUED', 1, '2026-11-15 10:00:06', NULL);

-- Audit trail: faculty corrected one attendance entry within 48 hours
INSERT INTO audit_log (user_id, table_name, record_id, action, old_value, new_value, reason, changed_at) VALUES
 (2, 'attendance_records', 35, 'UPDATE', json_object('status','A'), json_object('status','L'),
  'Student arrived late; marked absent by mistake', '2026-11-12 15:30:00');

-- Quick checks:
-- SELECT * FROM v_attendance_pct ORDER BY course_id, student_id;
-- SELECT * FROM v_test_pct WHERE test_pct < 40;
