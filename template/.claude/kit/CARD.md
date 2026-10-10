# The card: one page, keep it open all day

**Specify before you generate. Verify independently. Present only what is proven. Talk the whole time.**

| when | do | say |
|---|---|---|
| prompt given | `python .claude/scripts/clock.py start --demo HH:MM`; type the prompt into PROMPT.md word for word | "Let me write that down exactly." |
| minute 2 | `/questions`; ask the first three out loud; answers into PROMPT.md | "Who uses this? What does done look like by 4:30? Which mistake costs more?" |
| minute 5 | project facts in CLAUDE.md; paths in `.claude/guard.json` | "Telling the agent the rules before it writes anything." |
| minute 10 | plan mode (`Shift+Tab`), then edit the plan out loud; save PLAN.md | "Cutting X, doing Y first, adding Z. Does that match your priority?" |
| minute 20 | `/team-plan` only if the work splits; contracts first | "Contracts first, then three tasks in parallel. Want to take one?" |
| minute 25 | dictate 5-10 acceptance tests; show they fail; commit; `python .claude/scripts/lock_tests.py tests/test_acceptance.py` | "Here are the N tests that define done." |
| every step | `/next` -> read plan -> go -> read diff -> commit | the prompt before you type it; why you reject a diff |
| every 30 min | `/checkin` (clock reminds you) | works / next / deciding / risk, to the person who set the prompt |
| ~2h in | thin slice runs end to end | "First version runs end to end. Two minutes to see it?" |
| each wave | `/dispatch`, `/integrate`, reviewer + safety-reviewer | "Independent tests and a fresh reviewer, because an agent grading itself passes itself." |
| a long, well-specified backlog | `python .claude/scripts/loop.py --iterations 4 --minutes 15` (bounded, visible) | "A bounded loop on these three tasks; every pass must keep tests green." |
| 60 min before demo | stop features; full run; held-out set once; `/publish`-style README | "Stopping features now so what we show is solid." |
| demo | run it; `git log`; three decisions; gaps; next | credit teammates by name |

**Stuck?** Two failed attempts -> smaller step, clearer spec, or take the keyboard.
**Bug?** Failing test first, then the fix. **Model output?** Untrusted input; validate it.
**Never:** weaken a test, auto-accept everything, skip permissions, paste code from outside the room.
