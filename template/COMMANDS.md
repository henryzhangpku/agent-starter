# Build day: one input, six commands

The only input is what the prompt setter says. Everything else comes from
these commands, in this order. Keep this page open. RUNBOOK.md has the
detail; you should not need it on the day.

**Before they speak** (empty folder, already logged in to `claude`):

    curl -fsSL https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.sh | bash
    git init && git add -A && git commit -m "start" && claude

| step | when | type | you say / do |
|---|---|---|---|
| **1 Capture** | while they talk | jot notes, then `/capture <your notes>` | "Let me write that down exactly." Then **read back its three assumptions out loud**. |
| ⏱ | right after | `! python scripts/clock.py start --demo 16:30` | Agree the demo time out loud. |
| **2 Ask** | min 5 | `/questions` | **Ask its first three questions out loud.** Type each answer back in one line. |
| **3 Plan** | min 10-20 | `/make-plan` | Edit it out loud: cut, reorder, add. Type `save`. |
| **4 Done-tests** | min 20-30 | `/make-tests` | Cut or add, type `go`. **Say the minute-30 line** it gives you. |
| **5 Build** | until 30 min before the demo | `/team-plan` once, then `/dispatch 1` → `/integrate`, next wave (small steps: `/next`) | **Read every diff.** Narrate: "I asked for X, it proposes Y, I'm changing Z because..." |
| **↻ Check in** | every 30 min | `/checkin` | **Say the four lines**: works, next, deciding, risk. STATUS.md updates itself for anyone who looks. |
| ★ Slice | ~ midday | `! python scripts/clock.py done slice` | **Demo the rough end-to-end version to the room.** |
| **6 Demo prep** | 30 min before | `/demo-prep` | Rehearse WALKTHROUGH.md once, out loud. |

Handed existing code instead of an empty folder? Run `/onboard` before step 2.

## If something goes wrong

- Agent heading the wrong way: `Esc`, redirect in one sentence.
- A locked test looks wrong: tell the person who owns the spec. Never edit around it.
- Behind the clock: say it at the next check-in, cut from the plan's cut list.
- Practice runs: `--budget 180` instead of `--demo 16:30`; `clock.py report` at the end.
