# The build day on one page

Keep this open in a second window. Each row: what you do, what you type,
what you get. Times are for a 9:00 start with a 16:30 demo (practice:
a 3-hour budget, so roughly halve the gaps). Full detail: `RUNBOOK.md`.

| # | when | you do | you type | you get |
|---|---|---|---|---|
| 0 | before | setup, log in | `bootstrap.sh` then `claude` (check it is logged in) | agent kit, a working session |
| 1 | 0:00 | start the clock | `python scripts/clock.py start --demo 16:30` (practice: `--budget 180`) | the timeline and check-in times |
| 2 | 0:00 | prompt, word for word | edit `PROMPT.md` | the prompt on file |
| 3 | 0:02 | existing code only | `/onboard` | `ONBOARDING.md`: how to run, test, ship |
| 4 | 0:05 | who to ask, what | `/questions` | `TEAM.md`: roles, questions, the first three |
| 5 | 0:05 | **ask out loud**, type answers | (talk) | answers in `PROMPT.md` / `TEAM.md` |
| 6 | 0:10 | project facts, guard paths | edit `CLAUDE.md`, `.claude/guard.json` | the agent knows the data and the rules |
| 7 | 0:10 | plan | `Shift+Tab` to plan mode, paste the RUNBOOK 3.1 prompt | a proposed plan, no code |
| 8 | 0:15 | **edit the plan out loud**: cut, reorder, add, one question | (talk) then "save as PLAN.md" | `PLAN.md`, commit `plan` |
| 9 | 0:20 | define done | dictate 5-10 acceptance tests into `tests/test_acceptance.py` | failing tests |
| 10 | 0:30 | lock them, **say the minute-30 line** | `python scripts/lock_tests.py tests/test_acceptance.py` | commit `acceptance tests (failing)` |
| 11 | 0:30 | split for parallel agents | `/team-plan` | `CONTRACTS.md` + `TASKS.md` (approve aloud) |
| 12 | 0:40 | shared interfaces first | `/dispatch 0` or `/next` on the contracts task | contracts landed, commit |
| 13 | 0:50 | run a wave | `/dispatch 1` | parallel implementers + test-engineers |
| 14 | after each wave | merge it | `/integrate` | full tests, reviewer, one commit per task |
| 15 | solo steps | one small step | `/next` → read plan → "go" → **read the diff** → commit | one green step |
| 16 | every 30 min | **check in out loud** | `/checkin` | works / next / deciding / risk, logged |
| 17 | milestone | thinnest slice runs end to end | `python scripts/clock.py done slice` | **demo it to the room**, even ugly |
| 18 | 30 min before demo | stop building | `python scripts/clock.py done stop` | full run, held-out set once |
| 19 | 15 min before | tidy | README + `DECISIONS.md` | rehearse the walkthrough |
| 20 | demo | 5 minutes spoken | (talk) | demo, git log, three decisions, gaps, next |
| 21 | after (practice) | your real pace | `python scripts/clock.py report` | minutes per phase |

## When things go wrong

| problem | do |
|---|---|
| agent goes the wrong way | `Esc`, redirect in one sentence; after five minutes, take the keyboard |
| a locked test looks wrong | stop and say so to the person who owns the spec; never edit around it |
| context getting long | `/compact`, or a fresh session that reads `PLAN.md` + `NOTES.md` |
| behind the clock | say it at the next check-in and cut from the plan's cut list |

## Spoken lines

- **Minute 30:** "Here's the plan and the N tests that define done. Thinnest slice first; I'll check in at <time>."
- **Check-in:** "Works: … Next: … Deciding: … Risk: …"
- **Narrating the agent:** "I've asked it for X; it proposes Y; I'm changing Z because …"
