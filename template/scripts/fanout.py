"""Fan one task out to several agents, then compare the results on evidence.

  python scripts/fanout.py T3 --agents claude,claude,codex
  python scripts/fanout.py --prompt-file IDEA.md --agents claude,gemini --minutes 20
  python scripts/fanout.py T3 --agents claude,codex --dry-run

Each attempt gets its own git worktree and branch (../fan-<name>-<i>, branch
fan/<name>/<i>) from the current HEAD, and its own headless agent session with
the same prompt (FANOUT_PROMPT.md, plus the task id or prompt file). If the
task row in TASKS.md lists owned paths, Claude attempts get a lane.json so the
guard keeps them inside those paths. All attempts run in parallel, each with a
time limit.

Afterwards, in every worktree: uncommitted work is committed (so all attempts
compare the same way), the test suite runs, and the diff against the base is
measured (files, lines added/removed, and any path outside the task's
ownership). COMPARE.md ranks them: all tests passing first, then fewer
failures, no out-of-scope edits, smaller diff. You read the top two diffs and
merge one:

  git merge --no-ff fan/T3/2
  python scripts/fanout.py --cleanup T3      # remove all fan-T3-* worktrees and branches

The ranking is evidence for your decision, not the decision. Same-model
attempts differ more than you'd expect; different models differ more still.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent_cli  # noqa: E402

ROOT = HERE.parent
PROMPT_FILE = ROOT / ".claude" / "kit" / "FANOUT_PROMPT.md"
COMPARE = ROOT / "COMPARE.md"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def task_owns(task: str) -> list[str]:
    """Owned paths of a task row in TASKS.md (the `owns` column), or []."""
    f = ROOT / "TASKS.md"
    if not f.exists():
        return []
    header = None
    for line in f.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None and "owns" in [c.lower() for c in cells]:
            header = [c.lower() for c in cells]
            continue
        if header and cells and cells[0] == task and len(cells) == len(header):
            raw = cells[header.index("owns")]
            return [p.strip(" `") for p in re.split(r"[,\s]+", raw) if p.strip(" `")]
    return []


def parse_pytest(out: str) -> tuple[int, int]:
    """(passed, failed+errors) from pytest's summary line."""
    passed = sum(int(n) for n in re.findall(r"(\d+) passed", out))
    bad = sum(int(n) for n in re.findall(r"(\d+) (?:failed|error)", out))
    return passed, bad


def outside(paths: list[str], owns: list[str]) -> list[str]:
    if not owns:
        return []
    allowed = owns + ["NOTES.md"]

    def ok(p: str) -> bool:
        return any(p == a.rstrip("/") or p.startswith(a if a.endswith("/") else a + "/") for a in allowed) \
            or p.startswith("tests/")
    return [p for p in paths if not ok(p)]


def rank_key(r: dict) -> tuple:
    green = r["failed"] == 0 and r["passed"] > 0
    return (0 if green else 1, r["failed"], len(r["outside"]), r["added"] + r["removed"])


def measure(wt: Path, base: str, owns: list[str]) -> dict:
    if git("status", "--porcelain", cwd=wt):
        git("add", "-A", cwd=wt)
        git("commit", "-qm", "fanout: attempt result", cwd=wt)
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=wt,
                          capture_output=True, text=True, timeout=600)
    passed, failed = parse_pytest(proc.stdout + proc.stderr)
    if proc.returncode not in (0, 5) and failed == 0:
        failed = 1  # collection error or crash
    files = [p for p in git("diff", "--name-only", f"{base}..HEAD", cwd=wt).splitlines() if p]
    added = removed = 0
    for line in git("diff", "--numstat", f"{base}..HEAD", cwd=wt).splitlines():
        a, r, *_ = line.split("\t")
        added += int(a) if a.isdigit() else 0
        removed += int(r) if r.isdigit() else 0
    return {"passed": passed, "failed": failed, "files": files, "added": added, "removed": removed,
            "outside": outside(files, owns), "commits": len(git("rev-list", f"{base}..HEAD", cwd=wt).splitlines())}


def write_compare(name: str, base: str, results: list[dict]) -> None:
    rows = sorted(results, key=rank_key)
    lines = [f"# Fan-out: {name}", "", f"{datetime.now():%Y-%m-%d %H:%M}, base `{base[:10]}`. "
             "Ranked by: all tests pass, fewer failures, no out-of-scope edits, smaller diff.", "",
             "| rank | branch | agent | tests | out of scope | files | +/- | commits | finished |",
             "|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(rows, 1):
        tests = f"{r['passed']} pass" + (f", {r['failed']} fail" if r["failed"] else "")
        lines.append(f"| {n} | `{r['branch']}` | {r['agent']} | {tests} | {', '.join(r['outside']) or '-'} | "
                     f"{len(r['files'])} | +{r['added']}/-{r['removed']} | {r['commits']} | {r['status']} |")
    best = rows[0]["branch"] if rows else ""
    lines += ["", "Next: read the top two diffs (`git diff " + base[:10] + ".." + best + "`), then",
              f"`git merge --no-ff {best}` and `python scripts/fanout.py --cleanup {name}`.", ""]
    COMPARE.write_text("\n".join(lines), encoding="utf-8")


def cleanup(name: str) -> int:
    for line in git("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree ") and Path(line[9:]).name.startswith(f"fan-{name}-"):
            git("worktree", "remove", "--force", line[9:])
    for b in git("branch", "--list", f"fan/{name}/*").split():
        if b.startswith("fan/"):
            git("branch", "-D", b)
    print(f"removed fan-{name}-* worktrees and fan/{name}/* branches")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("task", nargs="?", help="task id from TASKS.md (or use --prompt-file)")
    p.add_argument("--prompt-file", help="a file with the task description instead of a TASKS.md id")
    p.add_argument("--agents", default="claude,claude", help="comma list, one attempt each, e.g. claude,claude,codex")
    p.add_argument("--minutes", type=float, default=20, help="time limit per attempt")
    p.add_argument("--max-turns", type=int, default=60)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--cleanup", metavar="NAME", help="remove the worktrees and branches of a fan-out")
    a = p.parse_args()

    if a.cleanup:
        return cleanup(a.cleanup)
    if not a.task and not a.prompt_file:
        p.error("give a task id or --prompt-file")
    name = a.task or Path(a.prompt_file).stem
    agents = [x.strip() for x in a.agents.split(",") if x.strip()]
    base_prompt = PROMPT_FILE.read_text(encoding="utf-8") if PROMPT_FILE.exists() else ""
    if a.task:
        prompt = base_prompt + f"\n\nYour task: {a.task} in TASKS.md."
    else:
        prompt = base_prompt + "\n\nYour task:\n" + Path(a.prompt_file).read_text(encoding="utf-8")
    owns = task_owns(a.task) if a.task else []

    if a.dry_run:
        print(f"fan-out '{name}' from HEAD; owned paths: {owns or '(none)'}")
        for i, ag in enumerate(agents, 1):
            print(f"  {i}. {ag}: ../fan-{name}-{i} (fan/{name}/{i}): "
                  f"{agent_cli.printable(agent_cli.command(ag, prompt, a.max_turns), prompt)}")
        return 0

    base = git("rev-parse", "HEAD")
    procs = []
    for i, ag in enumerate(agents, 1):
        wt = ROOT.parent / f"fan-{name}-{i}"
        branch = f"fan/{name}/{i}"
        git("worktree", "add", str(wt), "-b", branch, base)
        if owns and ag == "claude" and (wt / ".claude").is_dir():
            (wt / ".claude" / "lane.json").write_text(json.dumps({"task": name, "owns": owns}), encoding="utf-8")
            excl = Path(git("rev-parse", "--git-path", "info/exclude", cwd=wt))
            excl = excl if excl.is_absolute() else wt / excl
            excl.parent.mkdir(parents=True, exist_ok=True)
            with open(excl, "a", encoding="utf-8") as f:
                f.write("\n.claude/lane.json\n")
        cmd = agent_cli.command(ag, prompt, a.max_turns)
        logdir = ROOT / ".fanout"                       # logs live outside the attempt, so not in its diff
        logdir.mkdir(exist_ok=True)
        log = open(logdir / f"{name}-{i}.log", "w", encoding="utf-8")
        procs.append({"agent": ag, "branch": branch, "wt": wt, "log": log, "t0": time.monotonic(),
                      "proc": subprocess.Popen(cmd, cwd=wt, stdout=log, stderr=subprocess.STDOUT)})
        print(f"[fanout] started {ag} in {wt.name}")

    deadline = time.monotonic() + a.minutes * 60
    for r in procs:
        try:
            r["proc"].wait(timeout=max(1, deadline - time.monotonic()))
            r["status"] = f"exit {r['proc'].returncode}, {int((time.monotonic() - r['t0']) / 60)} min"
        except subprocess.TimeoutExpired:
            r["proc"].kill()
            r["status"] = "timed out"
        r["log"].close()

    results = []
    for r in procs:
        m = measure(r["wt"], base, owns)
        results.append({"agent": r["agent"], "branch": r["branch"], "status": r["status"], **m})
        print(f"[fanout] {r['branch']}: {m['passed']} pass, {m['failed']} fail, +{m['added']}/-{m['removed']}")
    write_compare(name, base, results)
    print(f"[fanout] wrote COMPARE.md; best by evidence: {sorted(results, key=rank_key)[0]['branch']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
