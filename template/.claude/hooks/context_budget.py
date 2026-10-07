"""UserPromptSubmit hook: say when a session has grown too long to stay sharp.

Every turn re-reads the whole conversation. Past a point that is slow and
expensive, and the start of the conversation gets less attention than it
deserves. The cure is cheap: write the state to NOTES.md and start a fresh
session, which reads PROMPT.md, PLAN.md and NOTES.md and carries on.

This hook reads the session transcript the harness passes in, finds how much
context the last model call carried (input + cache reads + cache writes), and
past WARN_TOKENS adds one line telling the agent to say so; past
STOP_TOKENS the line asks it to wrap up before doing anything else.
Silent below the threshold. Thresholds can be set in .claude/guard.json as
"context_warn_tokens" / "context_stop_tokens". Standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WARN_TOKENS = 150_000
STOP_TOKENS = 300_000


def thresholds() -> tuple[int, int]:
    try:
        cfg = json.loads((ROOT / ".claude" / "guard.json").read_text(encoding="utf-8"))
        return int(cfg.get("context_warn_tokens", WARN_TOKENS)), int(cfg.get("context_stop_tokens", STOP_TOKENS))
    except (OSError, ValueError, TypeError):
        return WARN_TOKENS, STOP_TOKENS


def context_tokens(transcript: Path, tail_bytes: int = 2_000_000) -> int | None:
    """Context size of the most recent model call in a Claude Code transcript (JSONL)."""
    try:
        with transcript.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - tail_bytes))
            lines = fh.read().decode("utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            usage = (json.loads(line).get("message") or {}).get("usage") or {}
        except ValueError:
            continue
        total = sum(int(usage.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        if total:
            return total
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    path = payload.get("transcript_path")
    if not path:
        return 0
    tokens = context_tokens(Path(path))
    if tokens is None:
        return 0
    warn, stop = thresholds()
    k = f"{tokens // 1000}k"
    if tokens >= stop:
        print(f"[context] This session carries {k} tokens of context. Before anything else, tell the human: "
              "write NOTES.md (done, in progress, open questions, gotchas), commit, and start a fresh session with /clear.")
    elif tokens >= warn:
        print(f"[context] This session carries {k} tokens of context. At the next natural stopping point, "
              "suggest updating NOTES.md and starting a fresh session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
