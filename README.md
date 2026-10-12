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

A teammate brings a problem (a spike, a hackathon, a pairing day); you have a
few hours to build it with an agent while they watch and weigh in. Bootstrap an empty folder, start `claude`, and type
**`/step`** again and again. It walks the day in order (capture the prompt,
ask the questions that matter, plan, failing acceptance tests, split into
parallel tasks, build, demo prep), checks in every 30 minutes, stops at each
point where a human should decide or speak, and asks when it needs input.
Every reply ends with what to say to the room and what happens next.
One page: [`template/COMMANDS.md`](template/COMMANDS.md).

**Starting a build day.** A brand-new problem: `mkdir -p ~/repo/<name> && cd ~/repo/<name>`,
run the bootstrap line above, copy in whatever you were handed (read-only inputs in `data/`),
`git init -q && git add -A && git commit -qm start && claude`, then `/step`. Their existing
repo: clone it, branch, run the bootstrap line, commit, `claude`, then `/onboard` and `/step`.

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
| `.claude/skills/` | loaded on demand when a problem mixes them in: **sql-and-schema** (read a handed-over database, schema, idempotent writes, indexes), **async-concurrency** (task graphs, cancellation, timeouts, limits), **reliability** (retries, idempotency, Docker, health checks, Kubernetes on paper), **team-repo** (working in their repo with teammates) |
| `PROMPT.md`, `PLAN.md`, `NOTES.md`, `DECISIONS.md` | the request and answers; the plan with a test per step; state across `/clear`; what was proposed, chosen, and why |
| `/next` | take the next plan step, plan first |

**Build day (opt-in: silent until you start the clock)**

| file | job |
|---|---|
| `.claude/kit/CARD.md` | the whole day on one page: what to do and what to say at each moment; keep it open |
| `.claude/kit/RUNBOOK.md` | the build day step by step, with modes for a new problem, an existing codebase, team mode and shipping; time boxes, copy-paste prompts, the commit that closes each phase |
| `.claude/scripts/clock.py` + a UserPromptSubmit hook | **the build-day clock:** `/step demo 16:30` starts it (the agent runs `clock.py`; you never type a script); every prompt then carries time-to-demo, and the agent warns you when a check-in or milestone (plan, tests, slice, stop, README, demo) is due or overdue. Check-ins are logged to `CHECKINS.md`. Says nothing until started |
| `/checkin`, `/questions` | status in four lines, logged with the clock; who to ask what, from the prompt |

**Team mode: agents as an engineering team**

| file | job |
|---|---|
| `.claude/agents/architect.md` | splits the plan into tasks with **disjoint file ownership**, fixes shared contracts first, groups tasks into waves |
| `.claude/agents/implementer.md` | one task, only its paths, against the contracts, until its tests pass |
| `.claude/agents/test-engineer.md` | tests from the spec **without reading the implementation**, run in parallel with the implementer |
| `.claude/agents/safety-reviewer.md` | failure paths, secrets, money and identity decisions, data handling |
| `/team-plan`, `/dispatch`, `/integrate` | split; run a wave of subagents in parallel; full test run, ownership check, reviews, one commit per task |
| `.claude/scripts/fanout.py`, `.claude/kit/FANOUT_PROMPT.md` | **best-of-N:** one task to several agents (same or different models) in separate worktrees, in parallel; each attempt's tests, diff size and out-of-scope edits ranked in `COMPARE.md`; you read the top diffs and merge one; `--cleanup` removes them |
| `AGENTS.md`, `.claude/scripts/agent_cli.py` | **agent-agnostic:** Codex, Gemini, Cursor and others read AGENTS.md (it points to CLAUDE.md); `loop.py` and `fanout.py` take `--agent claude|codex|gemini` or any CLI you define in `.claude/agent_cli.json`. Hooks only bind Claude Code; for other agents the scripts' test runs and diffs are the check |
| `.claude/scripts/lane.sh`, `lane.ps1` | a separate worktree and branch per task for long tasks, with the guard enforcing the task's paths |
| `TASKS.md`, `CONTRACTS.md` | the task board; every shared interface, written before parallel work |

**Existing codebases and shipping with a team**

| file | job |
|---|---|
| `.claude/agents/explorer.md`, `/onboard` | read-only map: run, test, ship, conventions, where the change goes, owners, questions to ask |
| `/publish` | open-source a finished build: secret and name checks, README with measured results, licence, optional demo page with link preview, a post draft; never pushes or posts |
| `/ship` | the team's own checks, rollout behind a flag, rollback, observability, a PR description; never merges or deploys itself |
| `/questions` | from the prompt: who to reach out to, up to three specific questions each, when to ask, what to offer back; the first three questions to say out loud |
| `.claude/scripts/loop.py`, `.claude/kit/LOOP_PROMPT.md` | a bounded Ralph loop: fresh headless sessions take one plan item per pass, keep tests green, commit, log to LOOP.md; stops when done, stalled twice, or at the time/pass limit; edits auto-accepted, shell limited, permissions never skipped |
| `TEAM.md` | who owns what, questions asked and answers, handoffs to people, credit |
| `.claude/kit/LANE.md` | a brief for a second agent or a person owning a slice |

## What `/step` does, step by step

| step | what happens | where a human decides |
|---|---|---|
| 1 Capture | the prompt into `PROMPT.md`, plus three assumptions to read back | correct the assumptions; agree the demo time |
| 2 Ask | who to ask what; rounds of at most three questions that change the design, phrased "I'm assuming X, correct me" | ask them, record the answers and who gave them |
| 3 Plan | opens with **the problem underneath** (the problem class, two or three approaches, the pick and why), then the thinnest slice first, a test per step | edit the plan out loud, then "save" |
| 4 Skeleton | package, contract, entry point, project facts, guard paths | |
| 5 Done-tests | acceptance tests from the answers, failing, then **locked**: the agent can never weaken them | if one turns out wrong, the human changes it (one `!` line the agent prepares) |
| 6 Split | contracts first, then tasks with disjoint files, in waves | approve the split |
| 7 Build, then iterate | a wave per `/step`, reviewed and committed; at the MVP, show it, take feedback from named people, ship one tested round at a time; `/change` absorbs a new requirement | demo the slice; bring back what the room said |
| 8 Demo prep | the end-of-day report below, gated by `check_demo.py` | rehearse once |

The skills in `.claude/skills/` (SQL, async, reliability, working in a team repo) load
whenever the problem mixes them in.

## What you have at the end of the day

A running product and the case for it, all served by the build itself:
- **an internal pitch** (`/pitch`): the problem, what we heard, the problem underneath and
  the solution, a live demo, results next to the weakness, how the day was spent, gaps,
  roadmap;
- **the team view** (the demo page with guided scenes, try-your-own and why) and **the
  customer view** (`?view=customer`);
- **the API** with `/openapi.json` and Swagger at `/docs`, a `/healthz`, a Dockerfile;
- **the docs**, rendered: architecture (runtime and component diagrams, top-down and
  readable, latency against the budget, the schema if anything is stored), how to plug it
  into the team's agent, likely questions with answers, and a test map;
- a clean repo root and everything committed.

`.claude/scripts/check_demo.py` checks all of it against the live server and fails on
anything missing, unreadable diagrams, a dark-by-default page or raw markdown links, so
demo prep cannot finish on memory. The look comes from `.claude/kit/LOOK.md`, `look.css` and
`diagrams.js`: calm and light by default; set it once from the team's own product feel.

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
