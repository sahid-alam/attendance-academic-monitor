# S4 deliverable acceptance checklist

Madiha Iram / S4. Live Jira descriptions inspected on **27 November 2026** against the full
repository, the project plan and open PRs. The user authorized publication, Jira completion
and merging PR #16. **AAM-37 is explicitly deferred** and remains open.

| Jira | Actual Jira requirement | Verified repository evidence |
|---|---|---|
| AAM-13 | Draw.io Scrum flow, two sprints | [Process](PROCESS_MODEL.md), [editable draw.io](process-model.drawio), matching PNG; review and retrospective are separate events |
| AAM-14 | Scrum rationale, two sprint goals, deadline, small chunks, Waterfall comparison | [Justification](PROCESS_JUSTIFICATION.md) covers all requested points |
| AAM-15 | Work packages with owner, week and dependency based on the plan | [WBS](WBS.md), 23 packages; all original owners/dates/dependencies preserved |
| AAM-16 | Both sprints, 19–26 Nov, milestones M1–M6 | [Gantt](GANTT.md), matching PNG; M6 is the original 27 Nov submission checkpoint |
| AAM-17 | Likelihood, impact and mitigation for original eight risks | [Register](RISK_REGISTER.md), original eight plus four additional risks |
| AAM-33 | Short student-data and risk-rule limitations statement | [Statement](../report/PROFESSIONAL_RESPONSIBILITY.md); team endorsement is a separate pending commitment, not claimed by document completion |
| AAM-34 | Full report across stages; contribution table at the end | [Report](../report/FINAL_REPORT.md), regenerated PDF; runnable baseline distinguished from open feature PRs |
| AAM-35 | Demo slides for every member in the plan's speaker order | [Deck](../presentation/AAM_PRESENTATION.pptx), PDF and notes; S1 → S4 → S2 → S3 with S1 → S2 → S3 → S1, plus S4 closing; 12 slides / 600 planned seconds |
| AAM-36 | Local and lab-server run instructions; failed-demo fallback | [Guide](../report/DEPLOYMENT.md), synthetic SQLite, loopback tunnel, start/stop, backup/reset and labeled fallback |
| AAM-37 | Full live-demo run with timing; everyone practises | [Pack](../presentation/REHEARSAL.md) prepared; actual team run deferred by user, **not complete** |

## Acceptance boundaries

The nine document tasks are ready for Jira closure after the verified PR is merged. This
accepts their actual Jira descriptions; it does not certify team endorsement, a completed
rehearsal, production security, an actual lab deployment or institutional submission.
Original baseline dates are preserved and no historical completion is backdated.

[Issue map](ISSUE_MAP.md) links each task to its GitHub review issue. The rehearsal issue
remains open. Stage epics require review of all their children and are not closed by this
checklist alone. PRs #3–#5 remain separate, unmerged work; the user scoped this merge to PR #16.

## Verification

- Full eight-test attendance suite and fresh disposable-database smoke flow passed.
- Report and slides regenerated from the corrected source and inspected as rendered PDFs.
- Draw.io source, six milestones, WBS preservation, local links and slide structure checked.
- Slide speaker order compared directly with Stage 7 of the plan.
- See [verification](../report/VERIFICATION.md) for exact scope and limitations.
