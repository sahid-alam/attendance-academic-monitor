# Requirements & Background Survey
## Online Student Attendance & Academic Monitoring System

| Field | Detail |
|---|---|
| Jira issue | **AAM-10** |
| Document version | 1.0 |
| Date | 25 November 2026 |
| Author | S1 – Requirements & Analysis Lead |
| Stage | Stage 1 – Requirements & Analysis |

---

## 1. Purpose of This Survey

Before writing the SRS (`requirements/SRS.md`), we conducted a structured background and stakeholder survey covering three areas:
1. **Existing tools and literature** — how colleges currently track attendance, marks, and early academic risk, and where existing solutions fall short.
2. **University attendance and privacy regulations** — what thresholds and consent rules our system must support as configurable policy.
3. **Stakeholder needs elicitation** — representative pain points and feature priorities across all five system roles (Admin, Faculty, Mentor, HOD, Student).

> **Data note:** Consistent with the project's data-handling rule in `planning/PROJECT_PLAN.md`, no real student or faculty survey responses or personal data are stored in this repository. Section 4 summarises representative stakeholder pain points gathered during project scoping.

---

## 2. Survey of Existing Systems and Literature

| Solution / Reference | How it works | Strengths | Gaps for our college context | How AAM addresses the gap |
|---|---|---|---|---|
| **Paper registers + Excel sheets** *(status quo)* | Faculty mark paper registers; internal marks sit in separate faculty spreadsheets. | Zero setup cost; familiar to staff. | Attendance % is tallied only near exam eligibility checks; marks and attendance are never combined; zero audit trail; easy to lose or overwrite. | Single digital database (`class_sessions`, `attendance_records`, `mark_entries`) with automatic `%` recalculation (**FR4, FR7, FR8**) and immutable `audit_log` (**FR15**). |
| **Generic College ERPs** | Large institutional suites covering admissions, fees, timetable, HR, and attendance. | Centralised institutional data. | Heavy UI, slow on mobile browsers, rigid hardcoded cutoffs, and no lightweight mentor intervention workflow. | Lightweight Flask + Bootstrap web app, sub-2s submission for 60 students, configurable `risk_rules` (**FR14**), and dedicated mentor case tracking (**FR11**). |
| **Classter Early-Warning Systems** *(Classter, EdTech blog)* | School/college platform that flags disengagement using attendance and grade thresholds. | Demonstrates value of combining attendance and marks alerts before finals. | Commercial SaaS licence; complex multi-module setup beyond a single department's scope. | Open-source stack (Flask + SQLite/MySQL) focused specifically on the attendance → marks → risk → intervention flow. |
| **Ken42 At-Risk Indicators** *(Ken42 blog)* | Uses predictive analytics and multi-factor indicators to identify at-risk learners. | Highlights multi-course risk patterns (not just single-subject drops). | Black-box ML predictions are hard for faculty/mentors to explain or trust without historical training data. | Transparent rule-based flags stored in `risk_flag_reasons` showing the exact `rule_id` and `actual_value` (**FR9**), plus a multi-course rule (`courses_below_cutoff >= 2`). |
| **Transparent Early-Warning Framework** *(arXiv:2412.09483)* | Academic research advocating explainable early-warning criteria and supportive mentor follow-up. | Emphasises explainability and non-punitive framing of alerts. | Research prototype, not tailored to Indian university condonation bands or 48-hour edit windows. | Supportive alert wording (*"needs attention"*), private visibility (ethics table), and mentor-reviewed interventions (`interventions`, **FR11**). |

---

## 3. Policy & Regulatory Findings

| Topic | Source / Reference | Finding | Impact on AAM Design |
|---|---|---|---|
| **75 % minimum attendance** | UGC attendance guidelines; NIT Kurukshetra UG/PG regulations (2024–25) | Many Indian universities mandate 75 % attendance for end-semester exam eligibility, though sources differ on whether UGC itself enforces a uniform cutoff across all programmes. | Stored as a configurable `risk_rules` row rather than hardcoded (**FR14**). |
| **65 % – 74.99 % condonation band** | Kerala University condonation policy | Universities commonly treat 65–74.99 % as a condonable band (e.g., medical/official duty) and `< 65 %` as below condonation limit. | Reflected in default rules: `WARNING` for `BETWEEN 65 AND 74.99`, `AT_RISK` for `< 65` (**FR9**). |
| **40 % internal test cutoff** | Team academic assumption | No universal standard applies to internal test pass marks across all colleges; 40 % is a common institutional convention. | Made configurable in `risk_rules` (`test_pct < 40`, **FR14**) and explicitly documented as an assumption. |
| **Student data privacy & consent** | DPDP Act & EdTech compliance overview (`ksandk.com`) | Requires data minimisation, clear privacy notice, and consent before sharing personal data with third parties. *(Note: exact statutory clauses have not yet been verified against the official DPDP Act text; legal review is required before production deployment.)* | RBAC enforced server-side (**FR1**), students see only their own records (**FR12**), and `students.parent_consent` defaults to `0` (opt-in only). |

---

## 4. Stakeholder Requirements Survey (Representative Elicitation)

During Sprint 1 scoping, we mapped the primary pain points and desired capabilities for each of the five active user roles:

| Role | Key Pain Points Identified | Top Requested Capabilities | Mapped Requirement(s) |
|---|---|---|---|
| **Admin** | Re-entering student lists and course mappings manually every semester causes typos and duplicate IDs. | Single screen to manage users, courses, sections, and enrolments, plus CSV bulk upload. | **FR1, FR2** |
| **Faculty** | Marking attendance for 60 students takes too long on clunky portals; accidental wrong clicks need a quick fix window without letting old records be silently altered. | Fast batch `P/A/L` grid (< 2 s save), 48-hour edit window, automatic lock afterwards, and simple marks entry with `0..max_marks` checks. | **FR3, FR4, FR5, FR6, FR7** |
| **Mentor (Faculty Advisor)** | Only hearing about struggling students from the exam cell when it is already too late to counsel them. | Immediate alert when a mentee's status worsens, exact reason why they were flagged, and a place to log counselling/remedial actions and close cases. | **FR10, FR11** |
| **HOD** | No unified view of which courses have high absence rates; hard to audit late edits or adjust rules when university circulars change. | Department dashboard, exportable CSV at-risk list, read-only `audit_log` view, HOD override for locked sessions, and editable risk thresholds. | **FR5, FR13, FR14, FR15** |
| **Student** | Students do not know their exact attendance % mid-semester or how many classes they must attend to get back to 75 %; fear of public "defaulter" lists. | Private self-service dashboard showing attendance %, test marks, private risk status, and a "classes still needed" deficit calculator. | **FR12** (plus Privacy NFR) |

---

## 5. Key Decisions Driven by the Survey

1. **Explainable rules over ML:** Every risk flag stores exact rule references in `risk_flag_reasons` so mentors and students see *why* a flag fired (`attendance_pct < 65` or `test_pct < 40`), avoiding opaque ML predictions.
2. **Configurable thresholds:** Because university cutoffs vary (Section 3), all thresholds live in `risk_rules` (**FR14**).
3. **48-hour edit window + `audit_log`:** Balances faculty convenience for correcting honest mistakes against academic integrity (**FR5, FR15**).
4. **Private, supportive risk visibility:** Surveyed student concerns about stigma led directly to hiding individual `AT_RISK` / `WARNING` labels from general faculty views and public lists, showing them only to the student, their mentor, and the HOD.
5. **Asynchronous/queued email delivery:** Ensures SMTP issues never block faculty attendance submission (**FR10**, `notifications.status = 'QUEUED'`).

---

## 6. Sources

1. [UGC attendance guidelines and Gujarat University's policy](https://bhattandjoshiassociates.com/ugc-guidelines-on-attendance-and-gujarat-universitys-policy/)
2. [Kerala University condonation rules](https://www.keralauniversity.ac.in/pdfs/news/Condonation1602068779.pdf)
3. [NIT Kurukshetra revised attendance rules (UG/PG 2024–25)](https://nitkkr.ac.in/wp-content/uploads/2024/11/Revised-Attendance-Rules-as-per-UG-PG-Regulations-for-appearing-in-the-End-Semester-Examination-from-Academic-Year-2024-25-onwards.pdf)
4. [Classter — Early-warning system launch](https://www.classter.com/blog/edtech/early-warning-system-launch/)
5. [Ken42 — How to identify at-risk students](https://ken42.com/blog/how-to-identify-at-risk-students-using-predictive-analytics)
6. [Transparent early-warning framework (arXiv:2412.09483)](https://arxiv.org/pdf/2412.09483v1.pdf)
7. [DPDP Act compliance for schools and EdTech](https://ksandk.com/md/data-protection-and-data-privacy/dpdp-compliance-for-schools-and-edtech/)
