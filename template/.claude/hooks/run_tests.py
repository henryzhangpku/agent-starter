"""PostToolUse hook: run the tests after an edit and report the tail.

Small projects get the whole suite after every edit, which is the point: the
agent sees any breakage at once. A real repository's suite can take minutes,
and waiting minutes on every one-line change is how a kit gets switched off.
So the hook times the full suite and, once it is slower than FAST_SECONDS,
runs only the tests that belong to the file just edited:

  - an edited test file runs itself;
  - an edited module `src/foo/bar.py` runs `test_bar*.py` anywhere under tests/
    (and `tests/foo/` if that folder exists);
  - nothing found: one line saying so; /integrate and /ship run everything.

Edits to prose (.md, .txt) run nothing. Set "test_scope" in .claude/guard.json
to "all" to always run the whole suite, or "changed" to always scope.

Uses the repository's .venv when it exists, otherwise the interpreter running
this script. Quiet on success (one line). On failure exits 2 with the last
lines of pytest output on stderr, so the agent sees the failure immediately.
If pytest is not installed yet, says so once and does not block.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAIL = 15
FAST_SECONDS = 20
TIMING = ROOT / ".claude" / "test_timing.json"
PROSE = {".md", ".txt", ".rst"}


def python() -> str:
    for cand in (ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"):
        if cand.exists():
            return str(cand)
    return sys.executable


def scope_setting() -> str:
    try:
        return json.loads((ROOT / ".claude" / "guard.json").read_text(encoding="utf-8")).get("test_scope", "auto")
    except (OSError, ValueError):
        return "auto"


def full_suite_seconds() -> float | None:
    try:
        return float(json.loads(TIMING.read_text(encoding="utf-8"))["full_seconds"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def record_full(seconds: float) -> None:
    try:
        TIMING.write_text(json.dumps({"full_seconds": round(seconds, 1)}), encoding="utf-8")
    except OSError:
        pass


def tests_for(edited: Path) -> list[Path]:
    """The test files that belong to an edited file (see the module docstring)."""
    tests_dir = ROOT / "tests"
    if not tests_dir.is_dir():
        return []
    if edited.name.startswith("test_") and edited.suffix == ".py":
        return [edited] if edited.exists() else []
    found = sorted(tests_dir.rglob(f"test_{edited.stem}*.py"))
    pkg = tests_dir / edited.parent.name
    if pkg.is_dir() and pkg != tests_dir:
        found += [p for p in sorted(pkg.rglob("test_*.py")) if p not in found]
    return found


def edited_path(payload: dict) -> Path | None:
    ti = payload.get("tool_input") or {}
    p = ti.get("file_path") or ti.get("notebook_path")
    if not p:
        return None
    path = Path(p)
    return path if path.is_absolute() else ROOT / path


def other_command() -> str | None:
    """The project's own test command when it is not plain pytest: guard.json "test_command",
    else detected from the repo (Node, Go, Rust, Java). None means pytest."""
    try:
        cmd = json.loads((ROOT / ".claude" / "guard.json").read_text(encoding="utf-8")).get("test_command")
    except (OSError, ValueError):
        cmd = None
    if cmd:
        return cmd
    for marker, detected in (("package.json", "npm test --silent"), ("go.mod", "go test ./..."),
                             ("Cargo.toml", "cargo test -q"), ("pom.xml", "mvn -q test"),
                             ("build.gradle", "gradle test -q")):
        if (ROOT / marker).exists() and not any(ROOT.glob("tests/test_*.py")):
            return detected
    return None


def run(args: list[str]) -> tuple[subprocess.CompletedProcess, float]:
    cmd = other_command()
    if cmd:
        t0 = time.monotonic()
        proc = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=300)
        return proc, time.monotonic() - t0
    t0 = time.monotonic()
    proc = subprocess.run(
        [python(), "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider", *args],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    return proc, time.monotonic() - t0


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    edited = edited_path(payload)
    if edited is not None and edited.suffix.lower() in PROSE:
        return 0

    setting = scope_setting()
    timed = full_suite_seconds()
    scoped = setting == "changed" or (setting == "auto" and timed is not None and timed > FAST_SECONDS)
    args: list[str] = []
    if scoped and edited is not None and other_command() is None:
        targets = tests_for(edited)
        if not targets:
            rel = edited.relative_to(ROOT).as_posix() if edited.is_relative_to(ROOT) else edited.name
            print(f"run_tests.py: no tests belong to {rel}; the full suite runs at /integrate and /ship")
            return 0
        args = [str(t) for t in targets]

    proc, seconds = run(args)
    if not args:
        record_full(seconds)
    out = (proc.stdout + proc.stderr).strip()
    if "No module named pytest" in out:
        print("run_tests.py: pytest is not installed; skipping (pip install pytest)")
        return 0
    if proc.returncode == 5:  # no tests collected yet
        print("run_tests.py: no tests yet")
        return 0
    tail = "\n".join(out.splitlines()[-TAIL:])
    if proc.returncode == 0:
        last = tail.splitlines()[-1] if tail else "tests passed"
        print(f"{last} ({'scoped to this edit' if args else 'full suite'}, {seconds:.0f}s)")
        return 0
    print(f"Tests failed after this edit:\n{tail}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
