---
description: The whole build day in one command - work out where we are, do the next step, stop at each human gate
---

You drive the build day; I make the calls and do the talking. Each time I
type /step, work out where we are from the files, do the next step, and stop
at the gate. Never skip a gate, never do two steps past a gate. If you need
anything from me (a fact, a file, a decision), ask one short question and
wait. $ARGUMENTS is extra input from me (notes, answers, edits).

**/step is my only reply, at every gate.** A bare `/step` at a gate means
"accept your recommendation and continue" (save the plan, approve the list,
commit the reviewed change). `/step <text>` means apply my edits or answers
first, then continue. Never ask me to type "go" or "save" separately; the
sub-commands' "wait for go/save" gates are satisfied by my next /step.

**Where are we?** Check, in this order, and act on the first that is not done:

1. **Capture.** PROMPT.md still has the template line under "Word for word"
   and $ARGUMENTS is empty: ask me to paste my notes of what was said, and
   stop. With notes: write PROMPT.md as /capture does (.claude/commands/capture.md).
   **Gate:** show me the three assumptions to read back out loud, and tell me
   to start the clock with the demo time we agree:
   `! python .claude/scripts/clock.py start --demo HH:MM` (practice: `--budget 180`).
2. **Ask.** TEAM.md has no "Questions to ask" section: do /questions
   (.claude/commands/questions.md). **Gate:** give me the three questions to
   ask out loud, word for word, and wait for the answers. When I give answers,
   record them in PROMPT.md and TEAM.md.
3. **Plan.** PLAN.md is still the template: do /make-plan. **Gate:** I edit it
   out loud; save only when I say "save", then `python .claude/scripts/clock.py done plan`.
3b. **Skeleton.** PLAN.md is saved but there is no product package or entry
   point yet: do /scaffold (.claude/commands/scaffold.md). It also fills the
   project facts in CLAUDE.md and the guard paths. **Gate:** wait for my
   "go" on the proposed layout.
4. **Done-tests.** tests/test_acceptance.py is still the placeholder (or
   missing): do /make-tests. **Gate:** wait for my "go" on the list; after
   writing, locking and committing, `python .claude/scripts/clock.py done tests`, and
   give me the minute-30 line to say.
5. **Split.** No TASKS.md tasks yet and the plan has three or more independent
   steps: do /team-plan. **Gate:** I approve the split out loud. If the work
   doesn't split, say so and use the /next loop instead.
6. **Build.** Run the next wave (/dispatch N) or the next /next step, then
   /integrate a finished wave. **Gate:** show me each diff summary to read
   and give me one sentence to narrate ("I asked for X, it did Y, I'm
   changing Z because..."); commit only after my "go". When every input gets
   an output end to end for the first time: `python .claude/scripts/clock.py done slice`
   and tell me to demo it to the room now.
6b. **Iterate: MVP, feedback, next round.** Every PLAN.md step is ticked and
   more than 30 minutes remain. Finishing early is good: it buys time for
   people. Round 1 is always the demo: bring the page to the MVP demo bar in
   make-plan.md (mission & solution section, three guided scenes, try your
   own, why, gaps, product look) before anyone sees it. Then do /show and give me the line to invite the team to look
   and react. **Gate:** I bring back what they said (`/step <their
   feedback>`), or a bare `/step` to improve on our own. Then turn the
   feedback, or else the weakest measured number, into the next PLAN.md
   step with a test, build it, and say the round in one line (what, why,
   number before and after). Repeat until 30 minutes before the demo.
7. **Demo prep.** 30 minutes or less before the demo (check
   `python .claude/scripts/clock.py status`): stop feature work and do /demo-prep.
   **Gate:** tell me to rehearse WALKTHROUGH.md out loud once.

**If $ARGUMENTS is a new or changed requirement from the team** (not an
answer to your question), handle it with /change (.claude/commands/change.md)
before continuing the step flow.

**Long session?** When the `[context]` line appears, finish the current
step, write NOTES.md, commit, and make the ⏎ line exactly:
`/clear, then /step = fresh session, picks up from the files`. Never wait on
the clock for this; never ask anything else at the same time.

**Every time,** before anything else: run `python .claude/scripts/clock.py status`.
If a check-in is due, do /checkin first (it updates STATUS.md) and give me
the four lines to say out loud, then continue.

**Start every reply with the map**, two short lines in a code block, so I
always know the phase, where we are and how far the finish is:

```
ITERATE · MVP done 11:42 · round 2: their feedback on the demo page
●●●●●●●◐  7/8 · 13:05 · demo 16:30 (3h25m) · 215 tests, 9/9 acceptance · check-in 13:12
```
Line 1 starts with the **phase**, in capitals, so I can use the time well:
- `SETUP` (capture, ask, plan, skeleton, done-tests, split): talk a lot.
- `BUILD MVP` (until the first full version, the MVP, passes the acceptance
  tests): heads-down time; changes are costly, so weigh them.
- `ITERATE` (MVP done; say when): like a startup after launch: show it to
  the team (the market), take their feedback, ship one small tested round
  at a time. The time for people, demos and changes.
- `DEMO PREP` (last 30 minutes): no new work.
Then the current task. Line 2: eight dots for Capture, Ask, Plan, Skeleton,
Tests, Split, Build, Demo (● done, ◐ current, ○ not started), time, time
left, test counts, next check-in. When a change request arrives, say which
phase it lands in and what that means for the clock.

**Token budget.** If `.claude/guard.json` has `"budget": "lean"` or I say
tokens are limited: no parallel subagents (use /next, not /dispatch), the
reviewer once per finished slice instead of per step, short replies, and
report the session's spend at each check-in (`/cost` if available). Say in
the map line which mode we are in.

**Fewer stops.** Stop only at the gates above, for a decision only I can
make, or for a blocker. Inside Build, a bare /step runs a whole wave end to
end: implement, review, apply the reviewers' recommended non-blocking fixes
(with a test), commit, and move on. Mention what you fixed in one line; do
not stop to ask about it. Keep replies to one screen.

**End every reply with this block, always.** Four short lines, plain words,
no jargon, each under 90 characters, so I can read it in two seconds:

```
📍 Step 7 of 8 · Build · last task: check our answers
🗣 "Our answer key is done. Could you check ten rows for me?"
⏎ /step = commit it   ·   /step <their corrections> = fix rows first
⏭ 11:42 check-in, then the final report
```
- 📍 where we are: step n of 8, its name, the current task in a few words.
- 🗣 what I say to the room: at most 25 words, one or two sentences, in my
  voice as written in `.claude/kit/VOICE.md`. No file names, no counts unless they matter.
- ⏎ what I type: bare `/step` and what it does; one alternative only if
  there is a real choice.
- ⏭ what comes next.
