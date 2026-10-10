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

## A build day in one command

Someone describes a problem; you have a few hours to build it with an agent,
in front of them. Bootstrap an empty folder, start `claude`, and type
**`/step`** again and again. It walks the day in order (capture the prompt,
ask the questions that matter, plan, failing acceptance tests, split into
parallel tasks, build, demo prep), checks in every 30 minutes, stops at each
point where a human should decide or speak, and asks when it needs input.
Every reply ends with what to say to the room and what happens next.
One page: [`template/COMMANDS.md`](template/COMMANDS.md).

## What you get

**Every day, in any repository** (on as soon as it is installed)

| file | job |
|---|---|
| `CLAUDE.md` | the working agreement: plan first, small steps, tests before code, never weaken a test, the model proposes and code decides, one module calls a model, one task per session. Plus project facts you fill in |
| `.claude/settings.json` | wires the hooks below |
| `.claude/hooks/guard.py` | **PreToolUse, edit tools AND shell:** refuses changes to protected inputs and locked acceptance tests, and in a lane anything outside the lane's paths (exit 2, reason shown to the agent). A blocked `Edit` cannot be routed around with `sed -i`, `>`, `cp` or a one-line script. Paths in `.claude/guard.json` |
| `.claude/hooks/run_tests.py` | **PostToolUse:** runs the tests after every edit; the whole suite while it takes under 20 s, only the edited file's tests once it is slower, nothing for prose. Failures go straight back to the agent. `"test_scope": "all"/"changed"` in `guard.json` overrides |
| `.claude/hooks/context_budget.py` | **UserPromptSubmit:** silent until the session's context passes 150k tokens, then tells the agent to suggest `NOTES.md` and a fresh session; at 300k it asks it to wrap up first. Thresholds in `guard.json` |
| `.claude/agents/reviewer.md` | read-only reviewer with a fresh context: an agent grading its own work passes itself |
| `PROMPT.md`, `PLAN.md`, `NOTES.md`, `DECISIONS.md` | the request and answers; the plan with a test per step; state across `/clear`; what was proposed, chosen, and why |
| `/next` | take the next plan step, plan first |

**Build day (opt-in: silent until you start the clock)**

| file | job |
|---|---|
| `.claude/kit/CARD.md` | the whole day on one page: what to do and what to say at each moment; keep it open |
| `.claude/kit/RUNBOOK.md` | the build day step by step, with modes for a new problem, an existing codebase, team mode and shipping; time boxes, copy-paste prompts, the commit that closes each phase |
| `scripts/clock.py` + a UserPromptSubmit hook | **the build-day clock:** `clock.py start --demo 16:30` once; every prompt then carries time-to-demo, and the agent warns you when a check-in or milestone (plan, tests, slice, stop, README, demo) is due or overdue. Check-ins are logged to `CHECKINS.md`. Says nothing until started |
| `/checkin`, `/questions` | status in four lines, logged with the clock; who to ask what, from the prompt |

**Team mode: agents as an engineering team**

| file | job |
|---|---|
| `.claude/agents/architect.md` | splits the plan into tasks with **disjoint file ownership**, fixes shared contracts first, groups tasks into waves |
| `.claude/agents/implementer.md` | one task, only its paths, against the contracts, until its tests pass |
| `.claude/agents/test-engineer.md` | tests from the spec **without reading the implementation**, run in parallel with the implementer |
| `.claude/agents/safety-reviewer.md` | failure paths, secrets, money and identity decisions, data handling |
| `/team-plan`, `/dispatch`, `/integrate` | split; run a wave of subagents in parallel; full test run, ownership check, reviews, one commit per task |
| `scripts/fanout.py`, `.claude/kit/FANOUT_PROMPT.md` | **best-of-N:** one task to several agents (same or different models) in separate worktrees, in parallel; each attempt's tests, diff size and out-of-scope edits ranked in `COMPARE.md`; you read the top diffs and merge one; `--cleanup` removes them |
| `AGENTS.md`, `scripts/agent_cli.py` | **agent-agnostic:** Codex, Gemini, Cursor and others read AGENTS.md (it points to CLAUDE.md); `loop.py` and `fanout.py` take `--agent claude|codex|gemini` or any CLI you define in `.claude/agent_cli.json`. Hooks only bind Claude Code; for other agents the scripts' test runs and diffs are the check |
| `scripts/lane.sh`, `lane.ps1` | a separate worktree and branch per task for long tasks, with the guard enforcing the task's paths |
| `TASKS.md`, `CONTRACTS.md` | the task board; every shared interface, written before parallel work |

**Existing codebases and shipping with a team**

| file | job |
|---|---|
| `.claude/agents/explorer.md`, `/onboard` | read-only map: run, test, ship, conventions, where the change goes, owners, questions to ask |
| `/publish` | open-source a finished build: secret and name checks, README with measured results, licence, optional demo page with link preview, a post draft; never pushes or posts |
| `/ship` | the team's own checks, rollout behind a flag, rollback, observability, a PR description; never merges or deploys itself |
| `/questions` | from the prompt: who to reach out to, up to three specific questions each, when to ask, what to offer back; the first three questions to say out loud |
| `scripts/loop.py`, `.claude/kit/LOOP_PROMPT.md` | a bounded Ralph loop: fresh headless sessions take one plan item per pass, keep tests green, commit, log to LOOP.md; stops when done, stalled twice, or at the time/pass limit; edits auto-accepted, shell limited, permissions never skipped |
| `TEAM.md` | who owns what, questions asked and answers, handoffs to people, credit |
| `.claude/kit/LANE.md` | a brief for a second agent or a person owning a slice |

## The first thirty minutes with it (the full day is in .claude/kit/RUNBOOK.md)

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

A rule is only as good as its coverage. An agent refused at `Edit` will often
reach for the shell next, so the guard reads shell commands too: explicit
write targets (redirects, `tee`, `sed -i`, `cp`/`mv` destinations, `rm`,
`touch`) are judged exactly like an edit, and any command that can write and
names a protected path anywhere (a Python one-liner, `git checkout --`,
`Set-Content`) is refused. Reading protected files stays allowed. It is a
best-effort parser biased to refuse, not a sandbox: for a hard boundary, also
make those paths read-only on disk or deny them in Claude Code's permissions.

## Examples

Builds that use the kit, filled in. See [`examples/`](examples/README.md).

1. [call-eval](https://github.com/henryzhangpku/call-eval): post-call evaluation for voice agents. The kit was extracted from it; its `CLAUDE.md`, hooks, reviewer, `PLAN.md` and `DECISIONS.md` are the filled-in solo loop.

MIT licence.
