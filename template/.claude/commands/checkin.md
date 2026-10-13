---
description: Status from PLAN.md and a test run, in four lines, logged with the clock
---

Read PLAN.md and NOTES.md, run `python -m pytest -q` and `python .claude/scripts/clock.py status`,
and give me the check-in in four lines: what works (ticked steps, tests
passing), what is next, what I need to decide, and the risk: a real risk to the product or the business if it ran tomorrow (a rule we might get wrong, a case we have not tested, a number that could mislead), never "none" and never only the schedule; say the schedule separately if it matters.
Fill the matching row of the check-in table in PLAN.md, then log it:
`python .claude/scripts/clock.py checkin "<works>; <next>; <deciding>; <risk>"`.
Then overwrite STATUS.md (create it if missing) with: the time, the four
lines, the test count, and the next check-in time, so anyone on the team can
read the current state without asking. Do not change any code, and do not make a commit just for the check-in;
STATUS.md rides along with the next real commit.
