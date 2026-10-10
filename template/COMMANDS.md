# Build day: one input, one command

The only input is what the prompt setter says. Then type **`/step`**, again
and again. Each time it works out where you are, does the next step, and
stops at a gate where you decide or talk. If it needs something from you, it
asks. Every reply ends with the same four short lines: 📍 where you are, 🗣 what to say, ⏎ what to type, ⏭ what comes next.
**`/step` is your only reply:** bare `/step` accepts its recommendation;
`/step <your words>` gives answers, edits or a different decision.

**Before they speak** (empty folder):

    curl -fsSL https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.sh | bash
    git init -q && git add -A && git commit -qm "start" && claude

## What /step walks you through

| # | step | the gate: you |
|---|---|---|
| 1 | **Capture**: your notes of what was said become PROMPT.md | read back three assumptions; start the clock |
| 2 | **Ask**: the questions that matter | ask three out loud, type the answers |
| 3 | **Plan**: thinnest slice first, cut list, risks | edit out loud; `/step` saves (or `/step <edits>`) |
| 3b | **Skeleton**: package, data contract, one run command, CLAUDE.md facts, guard paths | `/step` approves (or `/step <changes>`) |
| 4 | **Done-tests**: failing acceptance tests, locked | `/step` approves; say the minute-30 line |
| 5 | **Split**: contracts and parallel tasks | approve the split out loud |
| 6 | **Build**: waves of parallel agents, or one step at a time | read the summaries, narrate; `/step` commits; demo the first end-to-end slice |
| 6b | **Improve**: plan done early? measure, fix the weakest number, repeat until 30 min before | nothing; it says each round in one line |
| 7 | **Demo prep**: README, decisions, walkthrough | rehearse once out loud |
| ↻ | **Check-in**, automatically every 30 minutes | say the four lines; STATUS.md updates for anyone who looks |

## The team changes something mid-build

`/step <the change, in their words>` (or `/change ...`): it restates it, shows
the impact and what moves out to keep the demo time, waits for you, then
changes tests first and builds it. You say the trade-off back to them.

## See what's built, any time

`/show` runs the product and shows three real examples and the parts in plain
English. It changes nothing; the next `/step` carries on.

## You can still call any step directly

`/capture` `/questions` `/make-plan` `/scaffold` `/make-tests` `/team-plan` `/dispatch N`
`/integrate` `/next` `/checkin` `/demo-prep` · handed existing code: `/onboard` first ·
newer kit on GitHub: `/update-kit` (refreshes commands and hooks, never your files).

## If something goes wrong

- Agent heading the wrong way: `Esc`, redirect in one sentence.
- A locked test looks wrong: tell the person who owns the spec. Never edit around it.
- Behind the clock: say it at the next check-in, cut from the plan's cut list.
- It says the session is long: type `/clear`, then `/step`. Nothing is lost; it picks up from PLAN.md and NOTES.md.
