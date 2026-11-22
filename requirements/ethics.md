# Ethics Table and Professional Responsibility Statement
## Online Student Attendance & Academic Monitoring System

**Authors:** S1 (Requirements & Analysis) · S4 (Project Management)  
**Version:** 1.0 | **Date:** 22 November 2026

---

## Ethics Table

| Ethical Issue | Description of the Risk | Mitigation in AAM |
|---|---|---|
| **Privacy of academic records** | Attendance percentages and internal marks are personal data. If exposed to other students or the public, they can cause embarrassment or discrimination. | Access is enforced by RBAC (FR1). Students see only their own records (FR12). Mentors see only their assigned mentees (FR11). No public-facing pages show individual records. |
| **Informed consent and data minimisation** | Students may not know what data is collected or why, and unnecessary data should not be held. | A privacy notice is shown at first login explaining what is collected, how it is used, and how long it is kept. The system collects only the data needed (attendance status, marks, risk status) — no location data, biometrics, or social information. This is in line with the data minimisation principle of India's DPDP Act, 2023. |
| **Parental notification and consent** | Sending academic data to a parent without the student's consent violates the student's privacy, particularly for adult students. | Parent notification is opt-in only. The student must actively enable it. No parent notification is sent by default. |
| **Stigma of the "At-Risk" label** | Labelling a student as "At-Risk" in a system that others can see may cause social stigma or affect how faculty treat the student. | The at-risk status is visible only to the student, their assigned mentor, and the HOD — not to other students, other faculty, or any public list. The UI uses supportive wording (e.g., "Needs attention") rather than harsh labels. |
| **Accuracy and fairness of risk flags** | Automatic rule-based flags can be wrong if the underlying data is wrong (e.g., a faculty member marks someone absent by mistake). | Rules are transparent: each flag shows the exact rule that triggered it and the data value. A mentor must review before any formal action is taken. Attendance can be corrected within 48 hours (FR5). The HOD can override a locked record. Every change is in the audit log (FR15). |
| **Bias against students with approved absences** | A student absent for a medical reason, disability accommodation, or official sports duty would be unfairly penalised if those absences count the same as unexcused ones. | Approved leave is recorded and excluded from the absence count. The mentor can record an override with a written reason. The audit log captures the override for accountability. |
| **Security of personal data** | If the system is breached, students' academic records could be exposed or tampered with. | Passwords are hashed with bcrypt (never stored in plain text). All routes enforce RBAC server-side. HTTPS is mandatory. The application is checked against the OWASP Top 10 (SQL injection, broken access control, CSRF). No secrets are committed to the Git repository. |
| **Accessibility** | Students who use assistive technology (screen readers, keyboard-only navigation) or access the system on low-end phones must not be excluded. | The UI uses properly labelled HTML form elements, sufficient colour contrast (WCAG 2.1 AA), and keyboard-navigable components. The design is mobile-responsive from a minimum of 360 px width. |
| **Data retention and deletion** | Keeping student records indefinitely after a course ends is unnecessary and creates ongoing privacy risk. | Academic records are archived (read-only) after the semester ends. The archive policy is documented in the README. Daily backups ensure recovery without indefinite live exposure. |
| **Licensing and intellectual property** | Using unlicensed libraries or assets in a system that handles personal data creates legal risk. | Only permissively licensed open-source libraries are used (Flask — BSD; Bootstrap — MIT). Every external source is cited. A LICENSE file is included in the repository. |

---

## Professional Responsibility Statement

> Every member of the team understands the full project — not just their own section — and accepts shared responsibility for it.

We collect only the data the system needs to function: attendance statuses, internal marks, risk flags, and the contact details required to deliver notifications. We do not collect location data, device information, or anything that is not directly relevant to academic monitoring.

We acknowledge the limits of this system clearly. The risk rules are fixed numerical thresholds, not predictions about a student's future performance. A flag is a signal for a human mentor to investigate, not an automated judgment or penalty. The thresholds themselves depend on university regulations that may differ between institutions; the defaults we have chosen are configurable precisely because no single value is universally correct.

We have not verified every detail of the DPDP Act, 2023 against the official text; institutions deploying this system should seek legal advice before going live with real student data.

The at-risk label is designed to trigger support, not punishment. We are responsible for ensuring that the system is used in that spirit, and we document that intent here so that future maintainers carry it forward.

**All team members reviewed and agreed this statement on 22 November 2026.**

| Member | Role |
|---|---|
| S1 | Requirements & Analysis Lead |
| S2 | Design & Database |
| S3 | Development & Testing |
| S4 | Project Management & Documentation |
