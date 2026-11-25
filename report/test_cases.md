# Test cases (AAM-31)

All tests run on the synthetic seed data (`src/seed_synthetic.sql`).
Run them with `python -m unittest -v` inside `src/`. All 18 pass.

Seed students in CS501: Aarav 100%, Diya 80%, Meera 70% (Warning), Kabir 60% (Under Intervention).
Their mentor is Prof. P. Verma.

## Unit tests

| ID | Module | What is tested | Input | Expected result | Result |
|---|---|---|---|---|---|
| TC-01 | Attendance | % formula, Late counts as attended | Seed data | Aarav 100, Diya 80, Meera 70, Kabir 60 | Pass |
| TC-02 | Attendance | No classes recorded yet | Student with no CS502 classes | % shows "none yet", no divide by zero | Pass |
| TC-03 | Attendance | % updates after submit | Diya marked A in a new class | 80% becomes 72.73% (8 of 11) | Pass |
| TC-04 | Attendance | Same class recorded twice | Same section, date and period twice | Second insert rejected | Pass |
| TC-05 | Attendance | Edit window and audit log | Edit after 47 h, then after 49 h | First edit saved and logged with old and new value, second refused as locked | Pass |
| TC-06 | Attendance | Invalid status | Status "X" | Rejected by the database | Pass |
| TC-07 | Marks | Marks outside 0 to max | -1 and 21 out of 20 | Rejected, old mark kept | Pass |
| TC-08 | Marks + Risk | Test below 40% | Meera's test changed from 12 to 7 out of 20 | Warning becomes At-Risk, edit logged in audit_log | Pass |
| TC-09 | Risk | Main scenario | Diya absent | Normal becomes Warning, reason saved (rule 1, 72.73), mentor and student notified | Pass |
| TC-10 | Risk | Thresholds come from the RiskRule table | HOD changes the At-Risk cutoff from 65 to 85 | Diya at 81.82% becomes At-Risk with no code change | Pass |
| TC-11 | Risk | Inactive rule | Warning rule switched off | Diya gets no Warning, Meera's Warning clears | Pass |
| TC-12 | Risk | Recovery | Meera present in 2 more classes | Back to 75%, Warning becomes Normal | Pass |
| TC-13 | Risk | Under Intervention | Kabir absent again | Status stays Under Intervention, the mentor handles it | Pass |
| TC-14 | Risk | Below cutoff in 2 or more courses | Diya gets a low CS501 test while already At-Risk in CS502 | Multi-course flag becomes At-Risk | Pass |

## Functional tests (through the web pages)

| ID | Flow | Steps | Expected result | Result |
|---|---|---|---|---|
| TC-15 | Access control | Prof. Verma opens Dr. Sharma's section | 403 Forbidden | Pass |
| TC-16 | Take attendance | Dr. Sharma submits the form with Diya absent | Page shows 72.73%. The same date and period opens the edit page | Pass |
| TC-17 | Demo flow end to end | Faculty submits, then switch to the mentor | "1 newly flagged" for the faculty, with no status label on the faculty page. The mentor sees "Diya Patel (CSE2302) is now Warning in CS501" | Pass |
| TC-18 | Marks form | Add Internal Test 2, enter 25 out of 20, then valid marks | Error "between 0 and 20", then "marks saved for 2 students" | Pass |
