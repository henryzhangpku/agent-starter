"""PostToolUse hook: run the fast test suite after every edit and report the tail.

Uses the repository's .venv when it exists, otherwise the interpreter running
this script. Quiet on success (one line). On failure exits 2 with the last
lines of pytest output on stderr, so the agent sees the failure immediately.
If pytest is not installed yet, says so once and does not block.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAIL = 15


def python() -> str:
    for cand in (ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"):
        if cand.exists():
            return str(cand)
    return sys.executable


def main() -> int:
    sys.stdin.read()
    proc = subprocess.run(
        [python(), "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    out = (proc.stdout + proc.stderr).strip()
    if "No module named pytest" in out:
        print("run_tests.py: pytest is not installed; skipping (pip install pytest)")
        return 0
    if proc.returncode == 5:  # no tests collected yet
        print("run_tests.py: no tests yet")
        return 0
    tail = "\n".join(out.splitlines()[-TAIL:])
    if proc.returncode == 0:
        print(tail.splitlines()[-1] if tail else "tests passed")
        return 0
    print(f"Tests failed after this edit:\n{tail}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
