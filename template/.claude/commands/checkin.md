---
description: Status from PLAN.md and a test run, in four lines, logged with the clock
---

Read PLAN.md and NOTES.md, run `python -m pytest -q` and `python scripts/clock.py status`,
and give me the check-in in four lines: what works (ticked steps, tests
passing), what is next, what I need to decide, and any risk to the demo time.
Fill the matching row of the check-in table in PLAN.md, then log it:
`python scripts/clock.py checkin "<works>; <next>; <deciding>; <risk>"`.
Then overwrite STATUS.md (create it if missing) with: the time, the four
lines, the test count, and the next check-in time, so anyone on the team can
read the current state without asking. Do not change any code, and do not make a commit just for the check-in;
STATUS.md rides along with the next real commit.
