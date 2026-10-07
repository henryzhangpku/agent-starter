"""PreToolUse guard: refuse agent edits to protected paths.

Reads the hook payload (JSON) from stdin. Paths come from .claude/guard.json:
  protected_prefixes  directories the agent must never edit (input data, audit logs)
  protected_files     single files the agent must never edit
  acceptance_tests    tests the agent is judged by and must not weaken
  allowed_files       exceptions inside the protected sets

Exit codes follow the hook contract: 0 allows; 2 blocks and stderr is shown to
the agent. Missing or unreadable config fails closed on the acceptance tests
default. Standard library only, so it runs on any fresh machine.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
DEFAULTS = {
    "protected_prefixes": ["data/"],
    "protected_files": [],
    "acceptance_tests": ["tests/test_acceptance.py"],
    "allowed_files": [],
}


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    path = ROOT / ".claude" / "guard.json"
    try:
        cfg.update(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass
    return cfg


def relative(path_str: str) -> str | None:
    p = Path(path_str)
    if not p.is_absolute():
        p = ROOT / p
    try:
        rel = p.resolve().relative_to(ROOT)
    except ValueError:
        return None
    return PurePosixPath(rel.as_posix()).as_posix()


def verdict(path_str: str, cfg: dict) -> str | None:
    rel = relative(path_str)
    if rel is None or rel in cfg["allowed_files"]:
        return None
    if rel in cfg["acceptance_tests"]:
        return (f"{rel} is an acceptance test. Never weaken a test to make code pass. "
                "If you think it is wrong, stop and ask the human.")
    if rel in cfg["protected_files"] or any(rel.startswith(p) for p in cfg["protected_prefixes"]):
        return (f"{rel} is protected input or an audit record. Fix the code, not the inputs. "
                "Ask the human if it really needs to change.")
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print("guard.py: payload was not JSON; allowing", file=sys.stderr)
        return 1
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return 0
    reason = verdict(path, load_config())
    if reason:
        print(f"BLOCKED by .claude/hooks/guard.py: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
