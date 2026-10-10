---
description: The team changes a requirement mid-build - absorb it gracefully - restate, impact, tests first, re-plan, say it back
---

The team just changed or added a requirement: $ARGUMENTS

Handle it like a calm senior engineer, in this order, and stop at the gate:
1. **Restate** it in one sentence, plus the one question that would change
   how we build it (if any). Record it in PROMPT.md under "Changes" with the time.
2. **Impact**, one screen: which PLAN.md steps, contracts, acceptance tests
   and files it touches; what it breaks or makes obsolete; rough time; what
   we would cut from the plan to fit it in (from the cut list), so the demo
   time holds.
3. **Gate**: show the impact and the trade-off. The next /step from me
   approves (or `/step <adjustment>`).
4. After approval: update PLAN.md and DECISIONS.md (what changed, why, what
   was cut), change CONTRACTS.md first if an interface moves, write or change
   the acceptance test first (unlock only the tests the change really
   alters, with my approval, and relock), then build it through the normal
   loop with review, and commit as "change: <what>".

Give me the 🗣 line to say back to the person who asked: what we'll do, what
it costs, what moves out, when they'll see it.
