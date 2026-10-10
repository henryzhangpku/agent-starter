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
   `! python scripts/clock.py start --demo HH:MM` (practice: `--budget 180`).
2. **Ask.** TEAM.md has no "Questions to ask" section: do /questions
   (.claude/commands/questions.md). **Gate:** give me the three questions to
   ask out loud, word for word, and wait for the answers. When I give answers,
   record them in PROMPT.md and TEAM.md.
3. **Plan.** PLAN.md is still the template: do /make-plan. **Gate:** I edit it
   out loud; save only when I say "save", then `python scripts/clock.py done plan`.
3b. **Skeleton.** PLAN.md is saved but there is no product package or entry
   point yet: do /scaffold (.claude/commands/scaffold.md). It also fills the
   project facts in CLAUDE.md and the guard paths. **Gate:** wait for my
   "go" on the proposed layout.
4. **Done-tests.** tests/test_acceptance.py is still the placeholder (or
   missing): do /make-tests. **Gate:** wait for my "go" on the list; after
   writing, locking and committing, `python scripts/clock.py done tests`, and
   give me the minute-30 line to say.
5. **Split.** No TASKS.md tasks yet and the plan has three or more independent
   steps: do /team-plan. **Gate:** I approve the split out loud. If the work
   doesn't split, say so and use the /next loop instead.
6. **Build.** Run the next wave (/dispatch N) or the next /next step, then
   /integrate a finished wave. **Gate:** show me each diff summary to read
   and give me one sentence to narrate ("I asked for X, it did Y, I'm
   changing Z because..."); commit only after my "go". When every input gets
   an output end to end for the first time: `python scripts/clock.py done slice`
   and tell me to demo it to the room now.
6b. **Improve.** Every PLAN.md step is ticked but more than 30 minutes remain
   before the demo: do not start demo prep early. Run the product, measure it
   (the scorer, our own answer key, the "where it would hurt us" list), name
   the weakest number or the most costly failure, add it to PLAN.md as the
   next step with a test, and build it through the normal loop. Repeat until
   30 minutes before the demo. Say each round in one line: what was weakest,
   what we changed, the number before and after.
7. **Demo prep.** 30 minutes or less before the demo (check
   `python scripts/clock.py status`): stop feature work and do /demo-prep.
   **Gate:** tell me to rehearse WALKTHROUGH.md out loud once.

**If $ARGUMENTS is a new or changed requirement from the team** (not an
answer to your question), handle it with /change (.claude/commands/change.md)
before continuing the step flow.

**Every time,** before anything else: run `python scripts/clock.py status`.
If a check-in is due, do /checkin first (it updates STATUS.md) and give me
the four lines to say out loud, then continue.

**Start every reply with the map**, two short lines in a code block, so I
always know where we are and how far the finish is:

```
●●●●●●◐○  6/8 Build · plan step 6 of 6 (spot-check)
11:22 · demo 12:20 (58m) · 215 tests, 9/9 acceptance · check-in 11:42
```
Eight dots for Capture, Ask, Plan, Skeleton, Tests, Split, Build, Demo:
● done, ◐ current, ○ not started. Line 1 names the current step and its
sub-progress; line 2 is time, time left, test counts, next check-in.

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
- 🗣 what I say to the room: at most 25 words, one or two sentences, said
  the way a person talks. No file names, no counts unless they matter.
- ⏎ what I type: bare `/step` and what it does; one alternative only if
  there is a real choice.
- ⏭ what comes next.
