-- Made-up demo data. None of these people exist
-- 8 past sessions per course. Each student's pattern string is their P/A/L per session
-- Students are spread over the bands, and a couple sit just above a threshold
-- so one live submit with an A tips them over for the demo

INSERT INTO faculty (name) VALUES ('Prof. Demo One'), ('Prof. Demo Two');

INSERT INTO course (code, name, faculty_id) VALUES
    ('DEMO-SE', 'Software Engineering', 1),
    ('DEMO-DB', 'Database Systems', 2);

INSERT INTO student (usn, name) VALUES
    ('TEST001', 'Aarav Sample'),
    ('TEST002', 'Diya Sample'),
    ('TEST003', 'Kabir Sample'),
    ('TEST004', 'Meera Sample'),
    ('TEST005', 'Rohan Sample'),
    ('TEST006', 'Sana Sample');

INSERT INTO enrollment (student_id, course_id)
SELECT s.id, c.id FROM student s, course c;

WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 8)
INSERT INTO class_session (course_id, held_on, recorded_at)
SELECT c.id, date('2026-11-01', '+' || n.i || ' days'), datetime('2026-11-01', '+' || n.i || ' days', '+10 hours')
FROM course c, n;

CREATE TEMP TABLE pattern (usn TEXT, p TEXT);
INSERT INTO pattern VALUES
    ('TEST001', 'PPPPPPPP'),  -- 100%  Normal
    ('TEST002', 'PPPPPPAA'),  -- 75%   Normal, one more A drops to Warning
    ('TEST003', 'PPPPPLAA'),  -- 75%   Normal, L counts as present
    ('TEST004', 'PPPPPAAA'),  -- 62.5% At-Risk
    ('TEST005', 'PPPPPPPA'),  -- 87.5% Normal
    ('TEST006', 'PPPPAPAA');  -- 62.5% At-Risk

WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 8)
INSERT INTO attendance_record (session_id, student_id, status)
SELECT cs.id, s.id, substr(p.p, n.i, 1)
FROM n
JOIN class_session cs ON cs.held_on = date('2026-11-01', '+' || n.i || ' days')
JOIN student s
JOIN pattern p ON p.usn = s.usn;
