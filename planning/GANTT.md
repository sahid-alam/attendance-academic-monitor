# Baseline Gantt chart (AAM-16)

Owner: S4 / Madiha Iram. Calendar dates: November 2026, from `PROJECT_PLAN.md`.
This is the baseline plan, not proof that work happened on these dates. Assignment due dates
for AAM-13–AAM-17 are 20/21 November; late preparation on 26 November must remain visible.

![Baseline schedule](gantt.png)

```mermaid
gantt
    title AAM baseline: 19–27 November 2026
    dateFormat YYYY-MM-DD
    axisFormat %d Nov
    section Sprint 1
    Requirements / S1                :a, 2026-11-19, 3d
    Process model / S4               :b, 2026-11-19, 2d
    WBS, schedule, risks / S4        :c, 2026-11-19, 3d
    Architecture, DB, DFDs / S2      :d, 2026-11-21, 2d
    Sequence and state / S1          :e, 2026-11-22, 1d
    Requirements and plan / M1 (gate 21; window 20–21) :milestone, 2026-11-21, 0d
    Design review / M2              :milestone, 2026-11-22, 0d
    section Sprint 2
    Attendance / S3                 :f, 2026-11-23, 1d
    Attendance working / M3         :milestone, 2026-11-23, 0d
    Marks, risk, intervention / S3   :g, 2026-11-24, 1d
    Marks and risk working / M4     :milestone, 2026-11-24, 0d
    Ethics / S1 + S4                :h, 2026-11-23, 2d
    Verification / S3               :i, 2026-11-25, 1d
    Deployment guide / S4 + S3       :j, 2026-11-25, 1d
    Report and slides / S4 + all    :k, 2026-11-25, 2d
    Rehearsal / all                 :l, 2026-11-26, 1d
    Submission readiness / M5       :milestone, 2026-11-26, 0d
    section Submission checkpoint (outside 19–26 Nov sprint work)
    Final checks and submission     :m, 2026-11-27, 1d
    Submission / M6                 :milestone, 2026-11-27, 0d
```

The chart marks all six gates. M1 retains its 20–21 November review window; its diamond
marks the closing gate on 21 November. Sprint work ends on 26 November; M6 is the separate
27 November submission checkpoint. Milestone markers describe the baseline, not acceptance evidence.

## Milestones and dependency gates

| Milestone | Baseline | Gate |
|---|---|---|
| M1 | 20–21 Nov | Requirements and plan accepted |
| M2 | 22 Nov | Schema/models aligned; Sprint 1 review |
| M3 | 23 Nov | Attendance slice working |
| M4 | 24 Nov | Marks and risk features ready for verification |
| M5 | 26 Nov | Tests, report, slides and rehearsal reviewed |
| M6 | 27 Nov | Final submission and receipt |

Design starts against available requirements on 21 November; final freeze waits for review.
Report outlining overlaps verification on 25 November, while results and slides are finalized
only after the selected revision is tested. Rehearsal on 26 November follows slide review.
See `WBS.md` for detailed predecessors. The diagram uses calendar days and does not imply
all tasks have equal effort or that each person can perform overlapping tasks simultaneously.

## Catch-up checkpoint: 26 November

Documentation is being prepared after its original due dates. The repository inspection found
an attendance prototype on main and separate PRs for SRS and marks/risk work. Prioritize the
required documents, validate the main demo, and state pending integration honestly. Keep
rehearsal and final review as explicit remaining gates. Do not redraw the baseline as if late
work had finished on time; add actual completion dates only when supported by evidence.
