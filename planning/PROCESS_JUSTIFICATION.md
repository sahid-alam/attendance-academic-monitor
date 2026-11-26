# Process model justification (AAM-14)

Owner: S4 / Madiha Iram. Prepared 26 November 2026.

## Decision and rationale

Use an adapted Scrum process with two short sprints: 19–22 November for requirements,
design and planning, and 23–26 November for implementation, testing and submission material.
The repository plan sets submission for 27 November. This gives the four-person team a review
point before coding and another before submission while retaining the required documents.

The original idea was an Incremental model with five increments over about six weeks.
The supplied task summary dates the change to 19 November; the repository plan confirms the
change and deadline rationale, but does not provide signed meeting minutes for that date.
This document explains the decision; it must not be presented as contemporaneous minutes.

## Comparison

| Criterion | Original five-increment plan | Two-sprint Scrum plan |
|---|---|---|
| Time available | About six weeks assumed | Fits 19–26 November plus submission day |
| Feedback | Feedback at each increment, but original schedule exceeds deadline | Review after four days, then again before submission |
| Coordination | Needed a revised increment schedule | Short daily updates and a single prioritized board |
| Required documents | Possible under Incremental | SRS, models and plan are explicit Sprint 1 outputs |
| Late changes | Can revise later increments | Refine Sprint 2 backlog after Sprint 1 review |
| Cost | Low ceremony, but substantial replanning | Planning/review time is limited and proportionate to four people |

Incremental delivery itself is not incompatible with Scrum: each sprint produces an increment.
The reason for changing the original plan is its six-week schedule and missing coordination
cadence, not a claim that Incremental cannot work under a short deadline. A compressed
Incremental approach was possible, but the team plan prefers named reviews, daily blocker
visibility and Jira sprint goals. Waterfall was less attractive because late design mistakes
would have little correction time after a single implementation phase.

## Applying Scrum to this project

Sprint 1 reviews the attendance scenario across the SRS, DFD levels, schema and state model.
For example, review must resolve whether a notification is a required design behavior or a
working implementation before the demo claims it. Sprint 2 prioritizes a reproducible attendance
slice and the assessed process/planning/report artifacts. The board exposes blockers such as an
unmerged schema change, instead of discovering them during presentation setup.

The stages remain logical deliverables, not independent waterfall phases: feedback can revise
requirements and models. If a sprint goal is missed, record the unfinished item and revised
priority. Do not change historical due dates to hide delay.

## Limits and evidence

Two four-day sprints provide limited experience for estimating velocity. Do not extrapolate a
reliable long-term velocity or claim that Scrum caused measured productivity gains. Reviews,
retrospectives and daily updates are planned practices until dated records establish they happened.
The baseline is `PROJECT_PLAN.md`; task status must be reconciled with the live Jira board.
For the underlying framework see the [2020 Scrum Guide](https://scrumguides.org/scrum-guide.html).
This project uses a student-team adaptation, particularly in role allocation and sprint length.
