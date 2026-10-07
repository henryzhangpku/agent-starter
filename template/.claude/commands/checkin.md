---
description: Status from PLAN.md and a test run, in four lines, logged with the clock
---

Read PLAN.md and NOTES.md, run `python -m pytest -q` and `python scripts/clock.py status`,
and give me the check-in in four lines: what works (ticked steps, tests
passing), what is next, what I need to decide, and any risk to the demo time.
Fill the matching row of the check-in table in PLAN.md, then log it:
`python scripts/clock.py checkin "<works>; <next>; <deciding>; <risk>"`.
Do not change any code.
