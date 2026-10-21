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

Other languages run their own command (guard.json "test_command" wins). Java:
Maven or Gradle when there is a build file (the wrapper if present); with no
build file, plain javac: compile every .java file into .claude/build/java,
then run each class named *Test or Test* with `java -ea` (its main throws or
exits non-zero on failure). No test classes yet: compiling cleanly passes.

Uses the repository's .venv when it exists, otherwise the interpreter running
this script. Quiet on success (one line). On failure exits 2 with the last
lines of pytest output on stderr, so the agent sees the failure immediately.
If pytest is not installed yet, says so once and does not block.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAIL = 15
FAST_SECONDS = 20
TIMING = ROOT / ".claude" / "test_timing.json"
PROSE = {".md", ".txt", ".rst"}
PLAIN_JAVA = "plain-java"
SKIP_DIRS = {".claude", ".git", ".venv", "node_modules", "target", "build", "out", ".fanout"}


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
    if python_tests():
        return None
    mvn = "./mvnw -q test" if (ROOT / "mvnw").exists() else "mvn -q test"
    gradle = "./gradlew test -q" if (ROOT / "gradlew").exists() else "gradle test -q"
    for marker, detected in (("package.json", "npm test --silent"), ("go.mod", "go test ./..."),
                             ("Cargo.toml", "cargo test -q"), ("pom.xml", mvn),
                             ("build.gradle", gradle), ("build.gradle.kts", gradle)):
        if (ROOT / marker).exists():
            return detected
    if java_sources():
        return PLAIN_JAVA
    return None


def python_tests() -> list[Path]:
    """Real pytest files; the kit's untouched placeholder acceptance test does not count,
    or a fresh Java/Node/Go project would be run as pytest."""
    return [p for p in ROOT.glob("tests/test_*.py")
            if "def test_replace_me_with_real_acceptance_tests" not in p.read_text(encoding="utf-8", errors="replace")]


def java_sources() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.java")
                  if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts[:-1]))


def java_class(src: Path) -> str:
    m = re.search(r"^\s*package\s+([\w.]+)\s*;", src.read_text(encoding="utf-8", errors="replace"), re.M)
    return f"{m.group(1)}.{src.stem}" if m else src.stem


def quiet_jvm(text: str) -> str:
    """Drop the JVM's 'Picked up JAVA_TOOL_OPTIONS' banner, which is noise to the agent."""
    return "\n".join(l for l in text.splitlines() if not l.startswith("Picked up JAVA_TOOL_OPTIONS"))


def run_plain_java() -> subprocess.CompletedProcess:
    """javac everything, then run the *Test / Test* classes; stops at the first failure."""
    sources = java_sources()
    out_dir = ROOT / ".claude" / "build" / "java"
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    args = ["javac", "-d", str(out_dir), *map(str, sources)]
    try:
        comp = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 0, "run_tests.py: javac not found; skipping (install a JDK)", "")
    if comp.returncode != 0:
        return subprocess.CompletedProcess(args, comp.returncode, "", quiet_jvm(comp.stdout + comp.stderr))
    tests = [s for s in sources if s.stem.endswith("Test") or s.stem.startswith("Test")]
    if not tests:
        return subprocess.CompletedProcess(args, 0, f"compiled {len(sources)} Java file(s); no *Test classes yet", "")
    lines = []
    for t in tests:
        run_args = ["java", "-ea", "-cp", str(out_dir), java_class(t)]
        try:
            p = subprocess.run(run_args, cwd=ROOT, capture_output=True, text=True, timeout=120,
                               stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(run_args, 1, "", f"{t.name}: timed out after 120 s (a deadlock or a wait on stdin?)")
        out = quiet_jvm(p.stdout + p.stderr).strip()
        if p.returncode != 0:
            return subprocess.CompletedProcess(run_args, p.returncode, "\n".join(lines), f"{t.name} FAILED\n{out}")
        lines.append(f"{t.name} ok" + (f"\n{out}" if out else ""))
    lines.append(f"{len(tests)} Java test class(es) passed")
    return subprocess.CompletedProcess(args, 0, "\n".join(lines), "")


def run(args: list[str]) -> tuple[subprocess.CompletedProcess, float]:
    cmd = other_command()
    if cmd == PLAIN_JAVA:
        t0 = time.monotonic()
        return run_plain_java(), time.monotonic() - t0
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
