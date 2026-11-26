# Risk register (AAM-17)

Owner: S4 / Madiha Iram. Assessment: 26 November 2026.
Likelihood L: 1 unlikely, 2 possible, 3 likely. Impact I: 1 minor/local, 2 rework or partial
loss, 3 submission/privacy/demo failure. Score = L × I: 1–2 low, 3–4 medium, 6–9 high.
Scores are planning judgments, not measured probabilities. Review high risks daily and at M5.

| ID | Risk / trigger | L | I | Score | Owner / backup | Preventive response | Contingency / current state |
|---|---|---|---|---|---|---|---|
| R1 | Scope growth: request for biometrics, ML or SMS | 2 | 3 | 6 high | S4 / S1 | Enforce in/out scope; defer new features | Demonstrate attendance slice; open backlog item. Open |
| R2 | Member unavailable: missed daily update or handoff | 2 | 3 | 6 high | S4 / all | Share artifacts early; backups in WBS | Reassign urgent work and record actual contributor. Open |
| R3 | Developer bottleneck: dependent task slips a day | 3 | 3 | 9 high | S3 / S2 | S2 owns schema/seed; prioritize core flow | Freeze optional features; document partial implementation. Open |
| R4 | Design inconsistency: names or DFD flows differ | 2 | 2 | 4 medium | S2 / S1 | Cross-check schema, dictionary and DFD levels | Raise correction issue before sign-off. Open |
| R5 | Integration failure: PRs overlap or tests regress | 3 | 3 | 9 high | S3 / S2 | Small branches; test selected merged revision | Demo verified revision; describe pending PRs. Open |
| R6 | Privacy leak: real records, secrets or public risk list | 2 | 3 | 6 high | S1 / S4 | Synthetic data only; review tracked files | Restrict access, remove exposure, rotate exposed secrets and notify owner. Open |
| R7 | Incorrect eligibility rule: college policy differs | 2 | 3 | 6 high | S1 / S2 | Treat 75/65/40 as assumptions; get college approval | Explain advisory output; no automatic punitive decision. Open |
| R8 | Demo setup fails: clean start or network unavailable | 2 | 3 | 6 high | S3 / S4 | Test SQLite setup; preload assets; prepare backup | Use labeled screenshots and explain verified steps; no fake live run. Open |
| R9 | Documentation late: baseline due dates already passed | 3 | 3 | 9 high | S4 / S1 | Map every rubric item to an artifact | Prioritize process/planning/report; preserve baseline dates. Active |
| R10 | Publishing blocked: GitHub returns 403 | 1 | 3 | 3 medium | S4 / S3 | Verify account, repo permissions and API access early | 26 Nov: Iramc0re login and Write permission verified; API network grant applied. Access blocker mitigated; verify branch/PR on publication |
| R11 | Demo identity picker mistaken for secure login | 3 | 3 | 9 high | S3 / S1 | Label prototype; use synthetic data; loopback binding | Do not expose to real users; schedule auth/security work. Open |
| R12 | Rehearsal missing: no timed run by M5 | 2 | 2 | 4 medium | S4 / all | Assign speakers and use rehearsal checklist | Shorten talk, practice handoffs, record unfinished checks. Open |

## Escalation and ownership

An owner reports a triggered risk to S4 with its impact and next action; S4 reprioritizes the
board with the team. Privacy/security exposure is escalated immediately. A contingency is
not evidence that a risk has been resolved. Close a risk only with a dated verification note.
The submission date leaves little recovery time; reducing claims to verified scope is safer
than integrating unreviewed work immediately before the presentation.
