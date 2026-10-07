"""PreToolUse guard: refuse agent edits to protected paths.

Reads the hook payload (JSON) from stdin. Paths come from .claude/guard.json:
  protected_prefixes  directories the agent must never edit (input data, audit logs)
  protected_files     single files the agent must never edit
  acceptance_tests    tests the agent is judged by and must not weaken
  allowed_files       exceptions inside the protected sets

Team mode: if .claude/lane.json exists (written by scripts/lane.sh in a lane
worktree), edits are also limited to the lane's "owns" paths plus
tests/<task>/, so parallel agents cannot step on each other's files.

Exit codes follow the hook contract: 0 allows; 2 blocks and stderr is shown to
the agent. Acceptance tests start unlocked so the agent can write them in
Phase 4; `python scripts/lock_tests.py <path>` locks them once committed. Standard library only, so it runs on any fresh machine.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
DEFAULTS = {
    "protected_prefixes": ["data/"],
    "protected_files": [],
    "acceptance_tests": [],
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


def load_lane() -> dict | None:
    path = ROOT / ".claude" / "lane.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"task": "?", "owns": []}  # unreadable lane file: fail closed


def lane_verdict(rel: str, lane: dict) -> str | None:
    owns = list(lane.get("owns", [])) + [f"tests/{lane.get('task', '?')}/", "NOTES.md"]
    for p in owns:
        if rel == p.rstrip("/") or rel.startswith(p if p.endswith("/") else p + "/") or rel == p:
            return None
    return (f"{rel} is outside lane {lane.get('task', '?')}'s ownership ({', '.join(lane.get('owns', []))}). "
            "Stop and ask the orchestrator to change the contract or reassign the path.")


def verdict(path_str: str, cfg: dict, lane: dict | None = None) -> str | None:
    rel = relative(path_str)
    if rel is None or rel in cfg["allowed_files"]:
        return None
    if rel in cfg["acceptance_tests"]:
        return (f"{rel} is an acceptance test. Never weaken a test to make code pass. "
                "If you think it is wrong, stop and ask the human.")
    if rel in cfg["protected_files"] or any(rel.startswith(p) for p in cfg["protected_prefixes"]):
        return (f"{rel} is protected input or an audit record. Fix the code, not the inputs. "
                "Ask the human if it really needs to change.")
    if lane is not None:
        return lane_verdict(rel, lane)
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
    reason = verdict(path, load_config(), load_lane())
    if reason:
        print(f"BLOCKED by .claude/hooks/guard.py: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
