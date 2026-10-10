"""PreToolUse guard: refuse agent edits to protected paths, by edit tool or by shell.

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
import re
import shlex
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


# ---------------------------------------------------------------------------
# Shell commands. The edit tools are not the only way to change a file: an
# agent blocked from Edit will reach for `sed -i`, `>`, `cp` or a one-line
# Python script, and a guard that only watches Edit/Write promises more than
# it enforces. This is a best-effort check, deliberately biased to refuse:
#   - an explicit write target (redirect, tee, sed -i / perl -i, cp/mv/install
#     destination, touch/truncate/rm) is judged exactly like an edit, lane
#     ownership included;
#   - any OTHER mention of a protected path or locked test, in a command that
#     can write (a scripting one-liner, git checkout/restore, PowerShell
#     Set-Content...), is refused, because what it writes cannot be parsed.
# Reading a protected path (cat, grep, pytest, diff) is always allowed.
# ---------------------------------------------------------------------------

_REDIRECT = re.compile(r"(?:^|[^<>&0-9])(?:[12]|&)?>>?\s*([^\s;&|<>()]+)")
_WRITE_VERBS = {"tee", "cp", "mv", "install", "ln", "rm", "rmdir", "touch", "truncate", "dd", "chmod", "chown", "unlink", "shred"}
_DEST_LAST = {"cp", "mv", "install", "ln"}
_INPLACE = {"sed", "perl", "ruby"}
_ANY_WRITE = re.compile(
    r"(?:(?:^|[;&|(\s])(?:python3?|py|node|deno|bun|ruby|perl|php|powershell|pwsh)(?:\.exe)?\s.*(?:open\s*\(|write|unlink|remove|rename|replace)"
    r"|\bgit\s+(?:checkout|restore|rm|mv|apply|stash|reset|clean)\b"
    r"|\b(?:Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|New-Item|Clear-Content)\b"
    r"|\bsed\b.*\s-i|\bperl\b.*\s-[a-zA-Z]*i)",
    re.IGNORECASE | re.DOTALL,
)


def _words(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=True)
    except ValueError:  # unbalanced quotes: fall back to whitespace
        return segment.split()


def write_targets(command: str, cwd: Path | None = None) -> list[str]:
    """Paths a shell command explicitly writes to (best effort), made absolute against the
    directory each segment runs in, so `cd pkg && echo x > ../data/f` is caught."""
    here = cwd or ROOT
    targets: list[str] = []

    def add(path: str) -> None:
        if path in ("/dev/null", "nul", "NUL"):
            return
        p = Path(path)
        targets.append(str(p if p.is_absolute() else here / p))

    for segment in re.split(r"[;&|\n]+", command):
        for m in _REDIRECT.finditer(segment):
            add(m.group(1))
        words = _words(segment.strip())
        while words and ("=" in words[0] and not words[0].startswith("-")):
            words = words[1:]  # VAR=value prefixes
        if not words:
            continue
        verb = Path(words[0]).name
        args = [w for w in words[1:] if not w.startswith("-")]
        if verb in ("cd", "pushd", "Set-Location", "sl"):
            dest = Path(args[0]) if args else ROOT
            here = (dest if dest.is_absolute() else here / dest).resolve()
        elif verb in _DEST_LAST and args:
            add(args[-1])
        elif verb in _WRITE_VERBS:
            for a in args:
                add(a)
        elif verb in _INPLACE and any(w.startswith("-i") or (w.startswith("-") and "i" in w[1:] and verb != "sed") for w in words[1:]):
            for a in (args[1:] if verb == "sed" else args):
                add(a)
    return targets


def _mentions(command: str, cfg: dict) -> list[str]:
    """Protected paths and locked tests the command names anywhere."""
    text = command.replace("\\", "/")
    names = list(cfg["protected_files"]) + list(cfg["acceptance_tests"]) + list(cfg["protected_prefixes"])
    return [n for n in names if n and n not in cfg["allowed_files"] and n.rstrip("/") in text]


def bash_verdict(command: str, cfg: dict, lane: dict | None = None, cwd: Path | None = None) -> str | None:
    for target in write_targets(command, cwd):
        reason = verdict(target, cfg, lane)
        if reason:
            return f"this shell command writes {reason}"
    hit = _mentions(command, cfg)
    if hit and _ANY_WRITE.search(command):
        return (f"this shell command can write and names {', '.join(hit)}, which the agent must not change. "
                "Reading it is fine (cat, grep, pytest); changing it is the human's call.")
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print("guard.py: payload was not JSON; allowing", file=sys.stderr)
        return 1
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command")
    if isinstance(command, str) and command.strip():
        cwd = Path(payload["cwd"]) if payload.get("cwd") else None
        reason = bash_verdict(command, load_config(), load_lane(), cwd)
    else:
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
