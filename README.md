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

**Solo loop**

| file | job |
|---|---|
| `RUNBOOK.md` | **start here:** the build day step by step, with modes for a new problem, an existing codebase, team mode and shipping; time boxes, copy-paste prompts, the commit that closes each phase |
| `CLAUDE.md` | the working agreement: plan first, small steps, tests before code, never weaken a test, the model proposes and code decides, one module calls a model. Plus project facts you fill in |
| `.claude/settings.json` | wires two hooks into every edit |
| `.claude/hooks/guard.py` | **PreToolUse:** refuses edits to protected inputs and acceptance tests, and in a lane, anything outside the lane's paths (exit 2, reason shown to the agent). Paths in `.claude/guard.json` |
| `.claude/hooks/run_tests.py` | **PostToolUse:** runs the tests after every edit; failures go straight back to the agent |
| `.claude/agents/reviewer.md` | read-only reviewer with a fresh context: an agent grading its own work passes itself |
| `scripts/clock.py` + a UserPromptSubmit hook | **the build-day clock:** `clock.py start --demo 16:30` once; every prompt then carries time-to-demo, and the agent warns you when a check-in or milestone (plan, tests, slice, stop, README, demo) is due or overdue. Check-ins are logged to `CHECKINS.md` |
| `/checkin`, `/next` | status in four lines, logged with the clock; take the next plan step, plan first |
| `PROMPT.md`, `PLAN.md`, `NOTES.md`, `DECISIONS.md` | the request and answers; the plan with a test per step; state across `/clear`; what was proposed, chosen, and why |

**Team mode: agents as an engineering team**

| file | job |
|---|---|
| `.claude/agents/architect.md` | splits the plan into tasks with **disjoint file ownership**, fixes shared contracts first, groups tasks into waves |
| `.claude/agents/implementer.md` | one task, only its paths, against the contracts, until its tests pass |
| `.claude/agents/test-engineer.md` | tests from the spec **without reading the implementation**, run in parallel with the implementer |
| `.claude/agents/safety-reviewer.md` | failure paths, secrets, money and identity decisions, data handling |
| `/team-plan`, `/dispatch`, `/integrate` | split; run a wave of subagents in parallel; full test run, ownership check, reviews, one commit per task |
| `scripts/lane.sh`, `lane.ps1` | a separate worktree and branch per task for long tasks, with the guard enforcing the task's paths |
| `TASKS.md`, `CONTRACTS.md` | the task board; every shared interface, written before parallel work |

**Existing codebases and shipping with a team**

| file | job |
|---|---|
| `.claude/agents/explorer.md`, `/onboard` | read-only map: run, test, ship, conventions, where the change goes, owners, questions to ask |
| `/publish` | open-source a finished build: secret and name checks, README with measured results, licence, optional demo page with link preview, a post draft; never pushes or posts |
| `/ship` | the team's own checks, rollout behind a flag, rollback, observability, a PR description; never merges or deploys itself |
| `TEAM.md` | who owns what, questions asked and answers, handoffs to people, credit |
| `LANE.md` | a brief for a second agent or a person owning a slice |

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

## Examples

Builds that use the kit, filled in. See [`examples/`](examples/README.md).

1. [call-eval](https://github.com/henryzhangpku/call-eval): post-call evaluation for voice agents. The kit was extracted from it; its `CLAUDE.md`, hooks, reviewer, `PLAN.md` and `DECISIONS.md` are the filled-in solo loop.

MIT licence.
