---
description: Step 6 - stop building; run everything, tidy README and DECISIONS, write the 5-minute walkthrough
---

We are stopping feature work. Do these in order and do not add features:
1. Run the full suite and the end-to-end command; show the result. Start the
   demo page and check it loads and works on three real inputs; the live
   demo is the page, not the terminal. Refresh its "How we spent the day" timeline from
   the clock and git log, credit people by name, and check it against the
   MVP demo bar in make-plan.md and fix any gap before writing the walkthrough.
2. `python .claude/scripts/clock.py done stop`.
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
   only template text). Leave `.claude/` and `.claude/scripts/` (the tooling); README
   says in one line that they are the agent-starter tooling. Do not rewrite
   history.
4b. Write `docs/TESTS.md`: a table of each test file, the behaviours it
   proves, how many tests, and which risk it guards (the hard rules first);
   name any part of the product with no test. Keep it to one screen.
5. Update README.md: what it does, how to run it, the result, known gaps.
6. Tidy DECISIONS.md to the three decisions that matter most, each with the
   alternative we rejected and why.
6b. Build **the internal pitch**: `/pitch` on the same server, one HTML file,
   no libraries, arrow keys and click to advance, readable from the back of a
   room, same look as the demo page. A short internal pitch, not a fundraise:
   nine slides, one idea each, real numbers only:
   1. The problem: their prompt in one line, and who feels it.
   2. What we heard: the questions I asked and the answers that shaped it.
   3. The solution: what it does and how, in one picture or flow.
   4. Live demo: a button that opens the demo page on the guided scenes.
   5. Results: the headline numbers against the baseline, the weakness beside them.
   6. How we spent the day: the timeline, MVP time, feedback rounds, the
      change and its trade-off, thanks by name.
   7. Gaps: what it gets wrong today, and how we know.
   8. Roadmap, grounded in their system: Now (today's MVP), Next week (close
      the gaps, their real data through the loader, wire the API into their
      service), Next month (scale, monitoring, the features the team asked
      for); what each needs from them. Concrete, small, no fundraising talk.
   9. How I work: three lines (ask first, ship small with tests, decide with
      the team), then "Questions?".
7. Write WALKTHROUGH.md: a 5-minute spoken script that follows the pitch
   slide by slide (slide 4 switches to the live demo and back), in my voice (.claude/kit/VOICE.md), the case that I
   should be hired after a day in their office:
   - 0:00 Mission: their prompt in one line, and what I asked first and why.
   - 0:45 Solution: what we built, how, and the one decision that mattered most.
   - 1:30 How we spent the day: the timeline; MVP time, the feedback rounds
     and whose they were, the change we absorbed and its trade-off; thank
     people by name.
   - 2:30 The product, live: the three scenes (everyday, refused on purpose,
     hard case), then invite someone to try their own input.
   - 4:00 Honest gaps and the roadmap: what it gets wrong, what a week adds.
   - 4:40 Close: one sentence on how I like to work with a team, then stop and
     take questions.
   Add, for each of the three core functions, a two-sentence plain-English
   explanation I can say if asked about the code.
8. Write `docs/QA.md`: the ten questions the room is most likely to ask
   after the demo, each with a short answer in my voice. Cover:
   - **Why X, not Y**: each key decision in DECISIONS.md, the alternative
     we rejected and the reason (time, risk, the answer someone gave us).
   - **Why didn't you ask Z**: from TEAM.md, who we talked to, who we did
     not, why (time, scope, what we assumed instead), and what we would ask
     them now.
   - **What if we added feature xyz**: the top three cut-list or roadmap
     items, each with rough cost, what it would touch, and the trade-off;
     and the line "Want me to start it now? I can show you the impact in two
     minutes" (then `/step <their feature>` runs /change live).
   - **Why tech abc, not xyz**: every technology choice we made (language,
     standard-library server vs a framework, rules vs a model, file store vs
     a database, the test approach), the obvious alternative, and the
     reason in one line (their constraints, the day's time, fewer moving
     parts), plus when we would switch ("at real traffic, FastAPI and
     Postgres; here's where they plug in").
   - Where it breaks, how it scales, swapping in their real data, how we
     know it's right (tests, scorer, the hand-checked sample).
   Each answer: agree with what's fair, give the reason, say what I'd do next.
   Never defensive, never invented.
Finally: run the suite three times (no flakes), check every number in
README and WALKTHROUGH against the measured output (same definitions as the
problem statement; the main weakness in the same sentence as the headline),
commit with "demo prep", and confirm `git status --porcelain` is empty.
$ARGUMENTS
