# Build day: six steps, one command each

Keep this open. Type the command, read what comes back, say the line.
Detail lives in RUNBOOK.md; you should not need it on the day.

| step | when | type | then say / do |
|---|---|---|---|
| **0 Start** | prompt given | `python scripts/clock.py start --demo 16:30` · paste the prompt into `PROMPT.md` · `claude` | "Let me write that down exactly." |
| **1 Ask** | first 5 min | `/questions` | **Ask its first three questions out loud.** Type the answers back in one line each. |
| **2 Plan** | min 10-20 | `/make-plan` | Edit it out loud: cut, reorder, add. Then type `save`. |
| **3 Done-tests** | min 20-30 | `/make-tests` | Cut or add, type `go`. **Say the minute-30 line** it gives you. |
| **4 Build** | until the demo | `/team-plan` once, then `/dispatch 1` → `/integrate`, next wave... (small or solo work: `/next`) | **Read every diff.** Narrate: "I asked for X, it proposes Y, I'm changing Z because..." |
| **↻ Check in** | every 30 min | `/checkin` | **Say the four lines out loud**: works, next, deciding, risk. STATUS.md updates itself. |
| **5 Slice** | ~ midday | `python scripts/clock.py done slice` | **Demo the ugly end-to-end version to the room.** |
| **6 Demo prep** | 30 min before | `/demo-prep` | Rehearse WALKTHROUGH.md once, out loud. |

## If something goes wrong

- Agent heading the wrong way: `Esc`, redirect in one sentence.
- A locked test looks wrong: tell the person who owns the spec. Never edit around it.
- Behind the clock: say it at the next check-in, cut from the plan's cut list.
- Practice runs only: `python scripts/clock.py start --budget 180`, and `python scripts/clock.py report` at the end.
