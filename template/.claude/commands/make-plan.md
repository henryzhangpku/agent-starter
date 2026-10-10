---
description: Step 2 - propose the plan from PROMPT.md and the answers; save PLAN.md after I agree
---

Read PROMPT.md, TEAM.md (answers), CLAUDE.md, and any code, tests and data
already here. If there is no data, step 1 of the plan is a small synthetic
dataset with the hard cases the answers mention, plus a held-out slice. Propose a plan for this build, without writing any code:
the thinnest end-to-end slice first, then improvements in priority order.
For each step: what it produces and the test that proves it. Then the cut
list (what we drop if short on time), the risks, and the three things the
demo will show. Keep it to one screen.

Stop and wait. I will edit it out loud. When I say "save", write it to
PLAN.md in its existing structure (a checkbox and a test name per step, the
cut list, the risks, the check-in table), add the first decisions to
DECISIONS.md, and commit with the message "plan". $ARGUMENTS
