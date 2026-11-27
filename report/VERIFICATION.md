# Verification record

Verified 26 November 2026 in the cloud VM. Base application commit:
`57c0c6a7cbf54fa9b923b767548a1f4d4e47eb2b`.
The submission branch changes documentation and artifact-generation tools, not app behavior.

## Existing suite

Command from the repository root:

```bash
.venv/bin/python -m unittest discover -s src -v
```

Fresh result: **8 tests passed**, no failures (0.203 seconds on the recorded run).

| Test | Observed result |
|---|---|
| `test_pct_matches_seed_and_late_counts` | Pass |
| `test_pct_none_when_nothing_recorded` | Pass |
| `test_submit_updates_pct` | Pass |
| `test_same_class_twice_is_rejected` | Pass |
| `test_edit_within_48h_is_logged_then_locked` | Pass |
| `test_bad_status_rejected_by_db` | Pass |
| `test_other_faculty_gets_403` | Pass |
| `test_take_attendance_through_the_form` | Pass |

## Clean setup and demo smoke check

A fresh temporary SQLite database was initialized with the documented Flask CLI command
and the synthetic seed. Through Flask's test client the home page and CS501 returned 200.
Diya displayed 80.00%; marking her absent in a new 26 November / period 1 session produced
72.73%; requesting the same session redirected to editing; correcting to Present produced
81.82% and an audit row changing A to P. Selecting another faculty and opening the first
section returned 403. The temporary database was deleted after the run.

The machine-readable [smoke record](DEMO_SMOKE.json) includes the exact timestamp in
Asia/Kolkata. This was a Flask test-client check, not a browser usability test, public
production deployment or team presentation rehearsal.

## Submission artifacts

Build command: `.venv/bin/python tools/build_submission.py`.
Generated artifacts: process and Gantt PNGs, report PDF, 12-slide PPTX, presentation PDF,
and Markdown speaker notes. The source deck allocates exactly 600 seconds across S1–S4.
PDF exports were rendered for visual inspection; the report body/table and sample diagram/
demo slides were checked for legibility. The PowerPoint package is read back structurally;
its rendering in Microsoft PowerPoint remains a presenter check.

Local Markdown links, generated-file existence, slide count, speaker notes, PDF page counts,
and text extraction are checked before publication. Rebuild requires the separate authoring
dependencies in `tools/submission_requirements.txt`; application requirements are unchanged.

## Limits and pending evidence

No test here establishes production authentication, student isolation, SMTP delivery, MySQL
runtime compatibility, load performance, WCAG conformance, DPDP compliance or institutional
threshold approval. PRs #3–#5 remain separate proposals at inspection time. No tests from
those branches are represented as main's results.

Jira acceptance criteria/statuses require live board access. Responsibility endorsement,
teammate PR review, a real timed rehearsal and final submission receipt remain pending.

## Follow-up corrections — 27 November 2026

Scope: AAM-13, AAM-15, AAM-16 and AAM-36 on `docs/madiha-aam-submission`, following
published commit `17a5469`. No application runtime changes were made. Existing report,
slide and rehearsal exports were retained; they are outside this follow-up's scope.

- `tools/build_submission.py` completed successfully. Updated planning PNGs and draw.io
  source were retained; incidental report/presentation export changes were discarded.
- `python -m unittest discover -s src -v`: **8/8 passed** in a fresh local virtual environment
  (Python 3.14, Flask 3.1.0). The documented Python 3.12 lab procedure was not run on a lab host.
- `git diff --check`: passed.
- All 23 WBS work-package rows retain their original owners, due dates, dependencies and
  acceptance conditions; the added week/period column separates the sprints and submission.
- Both PNGs passed image-integrity checks and visual inspection. All six milestone gates
  appear on the Gantt chart, including the M1 review window and separate 27 November M6.
- Draw.io source XML validated: 19 individual shapes and 15 connectors, unique IDs and valid
  endpoints. Its exact XML was loaded into diagrams.net through an encoded editor link;
  an individual Sprint planning event could be selected with editable shape controls.
  Feedback routing and the two separate review/retrospective pairs were visually inspected.
- All **50 repository-local Markdown links** resolved.
- PRs #3, #4 and #5 remained open and unmerged when rechecked on 27 November; main remained
  `57c0c6a`. Attendance-only implementation claims therefore remain accurate for this branch.
- AAM-14 justification, AAM-17 risk register and AAM-33 responsibility statement were reviewed
  for consistency with the corrections. Team endorsement remains pending.

The lab-server section is a reproducible procedure, not a deployment claim. SSH access, a
supervised lab execution, team acceptance and actual submission still need their own evidence.
Earlier smoke-test results above remain historical; the eight-test suite was rerun for this follow-up.
Jira was inspected under Madiha's signed-in account; no Jira statuses were changed in this follow-up.
