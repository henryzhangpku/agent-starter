# agent-starter

A small kit for running a coding agent (Claude Code, or any agent that reads a
`CLAUDE.md`) the way you would run an engineer you have just hired: a written
working agreement, guardrails enforced by code rather than by asking nicely, a
reviewer that did not write the code, and a plan and decision log a human can
read afterwards.

One command drops it into any project, on any fresh machine, without
overwriting anything that is already there.

```bash
# macOS / Linux / WSL / Git Bash
curl -fsSL https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.sh | bash
```
```powershell
# Windows PowerShell
irm https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.ps1 | iex
```

Requirements: Python 3 for the hooks (standard library only) and, ideally, pytest.

## What you get

| file | job |
|---|---|
| `RUNBOOK.md` | **start here:** the whole build day, step by step, with time boxes, copy-paste prompts and the commit that closes each phase |
| `CLAUDE.md` | the working agreement: plan first, small steps, tests before code, never weaken a test, the model proposes and code decides, one module calls a model. Plus five project facts you fill in |
| `.claude/settings.json` | wires two hooks into every edit |
| `.claude/hooks/guard.py` | **PreToolUse:** refuses edits to protected inputs and to the acceptance tests (exit 2, with the reason shown to the agent). Paths live in `.claude/guard.json` |
| `.claude/hooks/run_tests.py` | **PostToolUse:** runs the test suite after every edit and puts failures in front of the agent at once |
| `.claude/agents/reviewer.md` | a read-only reviewer subagent with a fresh context: an agent grading its own work passes itself |
| `.claude/commands/checkin.md` | `/checkin`: status in four lines from the plan and a test run |
| `.claude/commands/next.md` | `/next`: take the next unticked plan step, plan first, wait for a go |
| `PROMPT.md` | the request word for word, the answers to your clarifying questions, your assumptions |
| `PLAN.md` | the plan as checkboxes, each step with the test that proves it; cuts, risks, check-ins |
| `NOTES.md` | state for the next context, written before every `/clear` |
| `DECISIONS.md` | what was proposed, what was chosen, why |
| `LANE.md` | the brief for a second agent in its own git worktree |
| `tests/test_acceptance.py` | the placeholder for the tests that define done (protected by the guard) |

## The first thirty minutes with it (the full day is in RUNBOOK.md)

1. **0-5:** write the request into `PROMPT.md`; ask the people, not the tool,
   who uses the output, what data exists, what done means, what costs most.
2. **5-10:** fill the project facts in `CLAUDE.md` and the paths in `.claude/guard.json`.
3. **10-20:** plan mode in the agent; edit its plan out loud; save it as
   `PLAN.md` with a test per step.
4. **20-30:** dictate five to ten acceptance tests into `tests/test_acceptance.py`;
   show they fail; commit. From here the agent builds against your definition of done.

Then `/next`, review, commit, repeat; `/checkin` every half hour.

## Why the guardrails are code

An instruction in a prompt is a request. A hook is a rule. "Never edit the
tests to make them pass" works far better when the edit is physically refused
and the agent is told why. The same goes for input data and audit records.

Worked example: this kit was extracted from [call-eval](https://github.com/henryzhangpku/call-eval);
its `CLAUDE.md`, hooks, reviewer, `PLAN.md` and `DECISIONS.md` are a filled-in version.

MIT licence.
