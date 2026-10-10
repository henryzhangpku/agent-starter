# Working agreement for coding agents in this repository

Read by Claude Code at the start of every session (and useful to any coding
agent or human contributor). The hooks in `.claude/settings.json` enforce the
parts that can be enforced mechanically; `.claude/guard.json` says which paths.

## How to work

1. **Plan first.** Before editing, name the step from `PLAN.md`, the files you
   will touch, and the test that proves it. Wait for a go on anything that
   changes behaviour.
2. **Small steps.** One plan step per change. The PostToolUse hook runs the
   tests after every edit (the whole suite while it is fast, the edited
   file's own tests once it is slow) and reports failures; fix them before
   moving on. The full suite always runs at `/integrate` and `/ship`.
3. **Tests before code.** Write or extend the test, watch it fail, make it pass.
4. **Never weaken a test.** Acceptance tests are blocked from editing by
   `.claude/hooks/guard.py`, through the edit tools and through the shell
   alike. If one is wrong, stop and say so; do not edit around it, skip it,
   mark it expected-to-fail, or reach for `sed`/`>`/a script to change it.
5. **The model extracts or proposes, code decides.** Scores, thresholds, money,
   identity and compliance checks are deterministic, tested code that fails
   closed. A model may fill a typed schema; it never makes the decision.
6. **One place calls a model.** Network calls to a model live in one module
   (name it below). Everything else is plain, testable code.
7. **Touch only the files the step names.** No drive-by refactors.
8. **Ask before adding a dependency.** Standard library and pytest first.
9. **Secrets** come from the environment. Never print, log, commit or put them
   on a command line.
10. **Honest results.** Report what the tests and metrics say, including
    regressions. If unsure about a requirement or data shape, ask.
11. **One task per session.** When the `[context]` line appears, finish the
    current step, write `NOTES.md` (done, in progress, open questions,
    gotchas), commit, and tell the human to start a fresh session. A fresh
    session that reads `PLAN.md` and `NOTES.md` beats a long one that re-reads
    everything on every turn.

## Project facts (`/scaffold` fills these in; correct them if wrong)

- The human follows `COMMANDS.md` (detail: `.claude/kit/RUNBOOK.md`). Problem: `PROMPT.md`. Plan: `PLAN.md`. State between sessions: `NOTES.md`.
  Decisions: `DECISIONS.md`.
- Data: `<path and format>`; inputs are read-only.
- The only module that calls a model: `<path>`.
- Data contract between parts: `<file and fields>`.
- Run tests: `python -m pytest -q`
- Review: after each step, the `reviewer` subagent checks the diff before commit.
