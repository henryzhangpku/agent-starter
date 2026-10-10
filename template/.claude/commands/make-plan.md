---
description: Step 2 - propose the plan from PROMPT.md and the answers; save PLAN.md after I agree
---

Read PROMPT.md, TEAM.md (answers), CLAUDE.md, and any code, tests and data
already here. If there is no data, step 1 of the plan is a small synthetic
dataset with the hard cases the answers mention, plus a held-out slice. Propose a plan for this build, without writing any code:
the thinnest end-to-end slice first, then improvements in priority order.
For each step: what it produces and the test that proves it. Always include,
right after the thinnest slice, the **integration surface and the demo**,
in three layers so the team could plug it into their system:
(1) the core stays a plain library (pure functions, no I/O inside the logic);
(2) a thin **JSON HTTP API** over it (standard library `http.server` unless
a framework is allowed; `--port` flag, request-scoped state, read the body
before any error response), with the endpoints the team's system would call,
request and response shapes written in CONTRACTS.md, errors as JSON with a
status code, and an `/health` endpoint;
(3) one **demo page** (one HTML file, inline CSS and JS, no build step)
served by the same server that calls **only the API**, never the internals,
so what the room sees is exactly what an integrating system would get.
`python -m <package>.serve` starts both. A script that prints JSON is not a
demo. Then the cut
list (what we drop if short on time), the risks, and the three things the
demo will show. Before any threshold or rule is tuned, split the data into a working set
and a held-out set (or say plainly there is none and never claim one). The
output files must follow the exact shapes the team gave (PROMPT.md answers);
if a shape was not given, ask. Size it to the day: the fewest modules and the least code that meet the
answers; a senior engineer should find nothing to delete. Keep it to one screen.

Stop and wait. I will edit it out loud. When I say "save", write it to
PLAN.md in its existing structure (a checkbox and a test name per step, the
cut list, the risks, the check-in table), add the first decisions to
DECISIONS.md, and commit with the message "plan". $ARGUMENTS
