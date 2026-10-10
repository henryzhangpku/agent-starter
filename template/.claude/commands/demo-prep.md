---
description: Step 6 - stop building; run everything, tidy README and DECISIONS, write the 5-minute walkthrough
---

We are stopping feature work. Do these in order and do not add features:
1. Run the full suite and the end-to-end command; show the result. Start the
   demo page and check it loads and works on three real inputs; the live
   demo is the page, not the terminal. Refresh its "How we spent the day" timeline from
   the clock and git log, credit people by name, and check it against the
   MVP demo bar in make-plan.md and fix any gap before writing the walkthrough.
2. `python scripts/clock.py done stop`.
3. **Senior-engineer pass on the code** (the team will open the repo):
   use the reviewer on the whole product package, not a diff, for
   simplicity only. Apply the safe simplifications: delete dead code and
   unused helpers, merge one-caller abstractions, cut duplicate or
   implementation-detail tests, clear names. Behaviour must not change: the
   acceptance tests stay green. Report lines and tests before and after.
4. **Clean the repo** so it reads like an engineer's project, not a kit.
   The root keeps only README.md, WALKTHROUGH.md, DECISIONS.md and CLAUDE.md
   (plus code, tests, data). `git mv` PROMPT.md, PLAN.md and CONTRACTS.md
   into `docs/`, and TEAM.md, TASKS.md, NOTES.md, STATUS.md, CHECKINS.md,
   COMMANDS.md and AGENTS.md into `docs/process/` (delete any that still hold
   only template text). Leave `.claude/` and `scripts/` (the tooling); README
   says in one line that they are the agent-starter tooling. Do not rewrite
   history.
4b. Write `docs/TESTS.md`: a table of each test file, the behaviours it
   proves, how many tests, and which risk it guards (the hard rules first);
   name any part of the product with no test. Keep it to one screen.
5. Update README.md: what it does, how to run it, the result, known gaps.
6. Tidy DECISIONS.md to the three decisions that matter most, each with the
   alternative we rejected and why.
7. Write WALKTHROUGH.md: a 5-minute spoken script - the problem in one line,
   the live demo command and what to point at, `git log --oneline` as the
   story of the day, the three decisions, what it gets wrong, what I would do
   next with a week. Add, for each of the three core functions, a
   two-sentence plain-English explanation I can say if asked about the code.
Finally: run the suite three times (no flakes), check every number in
README and WALKTHROUGH against the measured output (same definitions as the
problem statement; the main weakness in the same sentence as the headline),
commit with "demo prep", and confirm `git status --porcelain` is empty.
$ARGUMENTS
