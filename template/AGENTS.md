# Instructions for coding agents (Codex, Gemini, Cursor, Copilot and others)

The working agreement for this repository lives in **CLAUDE.md**: read it
first and follow it exactly, including its project facts. The short version:

1. Plan first: name the step, the files, and the test that proves it.
2. Small steps, one at a time; run `python -m pytest -q` after each.
3. Tests before code. Never edit, delete or weaken acceptance tests or
   protected data (paths in `.claude/guard.json`).
4. The model extracts or proposes; deterministic code decides anything about
   money, identity, compliance or scores.
5. Only the module named in CLAUDE.md calls a model.
6. Touch only the files the step needs; ask before adding a dependency.
7. Secrets come from the environment; never print, log or commit them.
8. Report results honestly, including failures.

State lives in files: PROMPT.md (the ask), PLAN.md and TASKS.md (the plan),
CONTRACTS.md (shared interfaces), NOTES.md (where things stand),
DECISIONS.md (why).

Note: Claude Code enforces parts of this with hooks; other agents are not
hooked, so the harness scripts (`.claude/scripts/loop.py`, `.claude/scripts/fanout.py`) check
their work with test runs and diffs instead.
