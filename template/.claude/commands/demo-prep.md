---
description: Step 6 - stop building; run everything, tidy README and DECISIONS, write the 5-minute walkthrough
---

We are stopping feature work. Do these in order and do not add features:
1. Run the full suite and the end-to-end command; show the result.
2. `python scripts/clock.py done stop`.
3. **Senior-engineer pass on the code** (the team will open the repo):
   use the reviewer on the whole product package, not a diff, for
   simplicity only. Apply the safe simplifications: delete dead code and
   unused helpers, merge one-caller abstractions, cut duplicate or
   implementation-detail tests, clear names. Behaviour must not change: the
   acceptance tests stay green. Report lines and tests before and after.
4. **Clean the repo** so it reads like an engineer's project, not a kit:
   delete template files we never used (any of CARD.md, LANE.md,
   FANOUT_PROMPT.md, LOOP_PROMPT.md, AGENTS.md, CONTRACTS.md, TASKS.md,
   TEAM.md, NOTES.md, CHECKINS.md still holding template text or no longer
   useful), keep PROMPT.md, PLAN.md, DECISIONS.md, STATUS.md, README.md.
   Commit messages already say what each step did; do not rewrite history.
5. Update README.md: what it does, how to run it, the result, known gaps.
6. Tidy DECISIONS.md to the three decisions that matter most, each with the
   alternative we rejected and why.
7. Write WALKTHROUGH.md: a 5-minute spoken script - the problem in one line,
   the live demo command and what to point at, `git log --oneline` as the
   story of the day, the three decisions, what it gets wrong, what I would do
   next with a week. Add, for each of the three core functions, a
   two-sentence plain-English explanation I can say if asked about the code.
Commit with "demo prep". $ARGUMENTS
