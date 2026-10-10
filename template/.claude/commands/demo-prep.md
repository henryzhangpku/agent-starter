---
description: Step 6 - stop building; run everything, tidy README and DECISIONS, write the 5-minute walkthrough
---

We are stopping feature work. Do these in order and do not add features:
1. Run the full suite and the end-to-end command; show the result.
2. `python scripts/clock.py done stop`.
3. Update README.md: what it does, how to run it, the result, known gaps.
4. Tidy DECISIONS.md to the three decisions that matter most, each with the
   alternative we rejected and why.
5. Write WALKTHROUGH.md: a 5-minute spoken script - the problem in one line,
   the live demo command and what to point at, `git log --oneline` as the
   story of the day, the three decisions, what it gets wrong, what I would do
   next with a week.
Commit with "demo prep". $ARGUMENTS
