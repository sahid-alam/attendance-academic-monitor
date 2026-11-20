-- Tables for the attendance module (AAM-28)
-- Names follow the ER entities in planning/PROJECT_PLAN.md
-- SQLite for development. MySQL in production needs AUTO_INCREMENT instead of AUTOINCREMENT

DROP TABLE IF EXISTS attendance_record;
DROP TABLE IF EXISTS class_session;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS faculty;

CREATE TABLE faculty (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL
);

CREATE TABLE student (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    usn   TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL
);

CREATE TABLE course (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    faculty_id  INTEGER NOT NULL REFERENCES faculty(id)
);

CREATE TABLE enrollment (
    student_id  INTEGER NOT NULL REFERENCES student(id),
    course_id   INTEGER NOT NULL REFERENCES course(id),
    PRIMARY KEY (student_id, course_id)
);

-- recorded_at is set on the first submit. Edits are allowed for 48 hours after that
CREATE TABLE class_session (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id    INTEGER NOT NULL REFERENCES course(id),
    held_on      TEXT NOT NULL,
    recorded_at  TEXT
);

CREATE TABLE attendance_record (
    session_id  INTEGER NOT NULL REFERENCES class_session(id),
    student_id  INTEGER NOT NULL REFERENCES student(id),
    status      TEXT NOT NULL CHECK (status IN ('P', 'A', 'L')),
    PRIMARY KEY (session_id, student_id)
);
