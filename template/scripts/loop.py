"""A bounded Ralph loop: fresh agent sessions work through the plan one item at a time.

  python scripts/loop.py --iterations 6 --minutes 30
  python scripts/loop.py --dry-run          # print the command, run nothing

Each pass starts a NEW headless Claude Code session (`claude -p`) with the same
prompt (LOOP_PROMPT.md): read the state files, take the next unchecked item,
make its tests pass, commit, update NOTES.md. Memory lives in files, so
context never rots. The guard and test hooks still apply to every edit.

Stops when: every plan item is checked and the tests pass; or N passes; or M
minutes; or two passes in a row make no progress (no new commit and no item
ticked). Every pass is logged to LOOP.md for review.

Safety: edits are auto-accepted, shell is limited to pytest and read/commit git
commands, permission prompts are denied rather than asked, permissions are
never skipped. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT_FILE = ROOT / "LOOP_PROMPT.md"
LOG = ROOT / "LOOP.md"
ALLOWED = [
    "Read", "Edit", "Write", "Grep", "Glob",
    "Bash(python -m pytest *)", "Bash(python -m pytest)",
    "Bash(git status *)", "Bash(git status)", "Bash(git diff *)", "Bash(git diff)",
    "Bash(git log *)", "Bash(git add *)", "Bash(git commit *)",
]


def open_items() -> int:
    """Unchecked plan items: '- [ ]' in PLAN.md plus 'todo'/'in progress' rows in TASKS.md."""
    n = 0
    plan = ROOT / "PLAN.md"
    if plan.exists():
        n += len(re.findall(r"^\s*- \[ \]", plan.read_text(encoding="utf-8"), re.M))
    tasks = ROOT / "TASKS.md"
    if tasks.exists():
        for line in tasks.read_text(encoding="utf-8").splitlines():
            cells = [c.strip().lower() for c in line.split("|")]
            if len(cells) > 3 and cells[1].startswith("t") and cells[-2] in ("todo", "in progress"):
                n += 1
    return n


def head() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def tests_pass() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def decide(open_now: int, green: bool, progressed: bool, stalls: int, i: int, max_i: int,
           elapsed_min: float, max_min: float) -> str | None:
    """Return a stop reason, or None to keep going."""
    if open_now == 0 and green:
        return "done: every plan item checked and tests pass"
    if stalls >= 2:
        return "stalled: two passes in a row without progress"
    if i >= max_i:
        return f"limit: {max_i} passes"
    if elapsed_min >= max_min:
        return f"limit: {max_min:g} minutes"
    return None


def command(claude: str, prompt: str, max_turns: int, model: str | None) -> list[str]:
    cmd = [claude, "-p", prompt, "--permission-mode", "acceptEdits", "--permission-prompts", "none",
           "--max-turns", str(max_turns), "--allowedTools", *ALLOWED]
    if model:
        cmd += ["--model", model]
    return cmd


def log(row: str) -> None:
    if not LOG.exists():
        LOG.write_text("# Loop log\n\n| pass | time | item count before -> after | new commit | tests | note |\n"
                       "|---|---|---|---|---|---|\n", encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(row + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--iterations", type=int, default=6)
    p.add_argument("--minutes", type=float, default=30)
    p.add_argument("--max-turns", type=int, default=40, help="agent turns per pass")
    p.add_argument("--model", default=None)
    p.add_argument("--claude", default=shutil.which("claude") or "claude")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    if not PROMPT_FILE.exists():
        print("LOOP_PROMPT.md is missing; it ships with the kit.")
        return 1
    prompt = PROMPT_FILE.read_text(encoding="utf-8")
    if a.dry_run:
        print(" ".join(f'"{c}"' if " " in c else c for c in command(a.claude, "<LOOP_PROMPT.md>", a.max_turns, a.model)))
        return 0

    t0, stalls, i = time.monotonic(), 0, 0
    while True:
        before_items, before_head = open_items(), head()
        reason = decide(before_items, tests_pass(), True, stalls, i, a.iterations,
                        (time.monotonic() - t0) / 60, a.minutes)
        if reason:
            break
        i += 1
        print(f"[loop] pass {i}: {before_items} open item(s)")
        r = subprocess.run(command(a.claude, prompt, a.max_turns, a.model), cwd=ROOT,
                           capture_output=True, text=True)
        after_items, after_head, green = open_items(), head(), tests_pass()
        progressed = after_head != before_head or after_items < before_items
        stalls = 0 if progressed else stalls + 1
        note = "ok" if r.returncode == 0 else f"agent exit {r.returncode}"
        log(f"| {i} | {datetime.now():%H:%M} | {before_items} -> {after_items} | "
            f"{'yes' if after_head != before_head else 'no'} | {'pass' if green else 'FAIL'} | {note} |")
        print(f"[loop] pass {i}: {after_items} open, tests {'pass' if green else 'FAIL'}, "
              f"{'progress' if progressed else 'no progress'}")
    print(f"[loop] stopped after {i} pass(es): {reason}. Review: git log, LOOP.md, NOTES.md")
    log(f"| - | {datetime.now():%H:%M} | stop | | | {reason} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
