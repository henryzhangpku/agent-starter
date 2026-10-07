"""How to run each coding agent headless, in one place.

Used by loop.py and fanout.py. Built-ins:

  claude  claude -p <prompt> --permission-mode acceptEdits --permission-prompts none
          --max-turns N --allowedTools <edit tools, pytest, read/commit git>
  codex   codex exec --full-auto <prompt>             (workspace-write sandbox)
  gemini  gemini -p <prompt> --approval-mode auto_edit

Override or add agents in .claude/agent_cli.json, e.g.
  {"gemini": ["gemini", "-p", "{prompt}", "--approval-mode", "auto_edit", "-m", "gemini-2.5-pro"]}
where "{prompt}" is replaced by the prompt text. Check your CLI's flags on the
day; vendors change them.

Only Claude Code runs this kit's hooks (guard, tests, clock). Other agents get
the same working agreement through AGENTS.md, but the guard is not enforced
for them; the scripts' own test runs and comparison are the check.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_ALLOWED = [
    "Read", "Edit", "Write", "Grep", "Glob",
    "Bash(python -m pytest *)", "Bash(python -m pytest)",
    "Bash(git status *)", "Bash(git status)", "Bash(git diff *)", "Bash(git diff)",
    "Bash(git log *)", "Bash(git add *)", "Bash(git commit *)",
]


def overrides() -> dict:
    try:
        return json.loads((ROOT / ".claude" / "agent_cli.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def known_agents() -> list[str]:
    return sorted({"claude", "codex", "gemini", *overrides()})


def command(agent: str, prompt: str, max_turns: int = 40, model: str | None = None,
            exe: str | None = None) -> list[str]:
    """The argv to run `agent` headless on `prompt` in the current directory."""
    custom = overrides().get(agent)
    if custom:
        return [prompt if part == "{prompt}" else part.replace("{prompt}", prompt) for part in custom]
    if agent == "claude":
        cmd = [exe or shutil.which("claude") or "claude", "-p", prompt,
               "--permission-mode", "acceptEdits", "--permission-prompts", "none",
               "--max-turns", str(max_turns), "--allowedTools", *CLAUDE_ALLOWED]
        return cmd + (["--model", model] if model else [])
    if agent == "codex":
        cmd = [exe or shutil.which("codex") or "codex", "exec", "--full-auto"]
        return cmd + (["-m", model] if model else []) + [prompt]
    if agent == "gemini":
        cmd = [exe or shutil.which("gemini") or "gemini", "-p", prompt, "--approval-mode", "auto_edit"]
        return cmd + (["-m", model] if model else [])
    raise ValueError(f"unknown agent '{agent}'; known: {', '.join(known_agents())} "
                     "(add others in .claude/agent_cli.json)")


def printable(cmd: list[str], prompt: str) -> str:
    shown = [("<prompt>" if c == prompt else c) for c in cmd]
    return " ".join(f'"{c}"' if " " in c else c for c in shown)
