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
7. **Demo prep.** 30 minutes or less before the demo (check
   `python scripts/clock.py status`): stop feature work and do /demo-prep.
   **Gate:** tell me to rehearse WALKTHROUGH.md out loud once.

**Every time,** before anything else: run `python scripts/clock.py status`.
If a check-in is due, do /checkin first (it updates STATUS.md) and give me
the four lines to say out loud, then continue.

**End every reply with two lines:**
`Say:` the exact words for me to say to the room now (or "nothing").
`Next:` exactly what a bare `/step` will do (your recommendation), and, if
there is a decision, the choice in one line so I can type `/step <my answer>`
instead.
