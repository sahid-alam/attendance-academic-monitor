# Professional responsibility statement (AAM-33)

Prepared for S4 / Madiha Iram, with S1 responsible for the wider ethics analysis.
Proposed team statement for review, 26 November 2026. This document is not a signed
attestation that every control listed below has already been implemented.

## Our commitments

We will use attendance and internal marks to identify students who may need help. A risk
flag is a transparent rule result, not a prediction of ability or a disciplinary decision.
A mentor must check context and speak with the student before deciding on an intervention.
We will state the reason for a flag and provide a route to correct an inaccurate record.

We will collect only necessary student, course, attendance and assessment data. Access must
follow responsibility: students see their own records, mentors their assigned students, and
administrators only the information required for their role. We will avoid public at-risk
lists and use supportive language. Parent contact requires appropriate student consent;
we will not infer consent from an address being stored in the database.

We will protect records with authenticated access, secure password storage, transport
security, appropriate CSRF protection, backups and audit trails. We will never commit real
student data, passwords or deployment secrets. Demo material uses synthetic `.test` addresses
and made-up records. The current identity picker is a demonstration aid, not authentication.

We will consider disability, approved leave, medical circumstances and institutional policy
before interpreting attendance. Thresholds must be approved by the institution and be
explainable and reviewable. No automated flag should deny examination access or stigmatize
a student. A human review and an auditable correction process are required.

We will make forms usable with keyboards and assistive technology and test on ordinary
phones. We will record accessibility and performance results before claiming compliance.
We will agree a retention period and deletion/archival policy with the college rather than
keeping student records indefinitely by default.

We will credit sources, preserve license notices, identify reused components, review each
other's changes and report defects honestly. Contributions will be attributed using actual
commits and reviews; generated drafts require team review. We will distinguish designed,
implemented, tested and deployed behavior in the report and presentation.

## Current implementation limits

Main contains a local Flask/SQLite attendance prototype. Role tables, flags, notifications
and interventions in the schema do not establish working or secure application flows.
The main branch has no real login, full five-role access control, risk engine, marks UI,
notification delivery or production deployment. Separate PRs propose some of those flows.
A faculty/section restriction and attendance edit audit exist, but do not replace authentication.
Production use with real student data requires security, privacy and institutional review.

The project plan mentions India's DPDP Act; the applicable legal requirements, commencement
and college obligations have not been independently verified here. This statement makes no
claim of legal compliance. Consult the college's responsible staff and official sources.

## Review and endorsement

| Role | Review requested | Endorsement evidence |
|---|---|---|
| S1 | Consent, fairness, privacy and policy assumptions | Pending team review |
| S2 | Data access, retention, schema and audit design | Pending team review |
| S3 | Actual security controls and tested limits | Pending team review |
| S4 / Madiha Iram | Report accuracy, attribution and review tracking | Pending team review |

See the [ACM Code of Ethics](https://www.acm.org/code-of-ethics), particularly avoiding harm,
respecting privacy, honoring confidentiality and evaluating system risks. These principles
support the commitments above; they are not a certification of this prototype.
