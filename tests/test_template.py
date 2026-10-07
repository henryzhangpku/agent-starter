"""Checks that the template's guard hook and settings work on a copy of the template."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parents[1] / "template"


@pytest.fixture()
def project(tmp_path):
    dst = tmp_path / "proj"
    shutil.copytree(TEMPLATE, dst)
    return dst


def guard(project, file_path):
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(file_path)}})
    return subprocess.run([sys.executable, str(project / ".claude/hooks/guard.py")],
                          input=payload, capture_output=True, text=True)


def test_guard_blocks_protected_and_acceptance(project):
    for target in ("data/calls.jsonl", "tests/test_acceptance.py", project / "data" / "x.csv"):
        r = guard(project, target if isinstance(target, Path) else project / target)
        assert r.returncode == 2, target
        assert "BLOCKED" in r.stderr


def test_guard_allows_code_and_outside_paths(project, tmp_path):
    assert guard(project, project / "src" / "app.py").returncode == 0
    assert guard(project, project / "tests" / "test_review.py").returncode == 0
    assert guard(project, tmp_path / "elsewhere.py").returncode == 0


def test_guard_config_allowlist(project):
    cfg = json.loads((project / ".claude/guard.json").read_text())
    cfg["allowed_files"] = ["data/README.md"]
    (project / ".claude/guard.json").write_text(json.dumps(cfg))
    assert guard(project, project / "data" / "README.md").returncode == 0
    assert guard(project, project / "data" / "other.csv").returncode == 2


def test_guard_allows_payload_without_path(project):
    r = subprocess.run([sys.executable, str(project / ".claude/hooks/guard.py")],
                       input=json.dumps({"tool_input": {}}), capture_output=True, text=True)
    assert r.returncode == 0


def test_settings_is_valid_json_and_wires_both_hooks(project):
    s = json.loads((project / ".claude/settings.json").read_text())
    assert "guard.py" in s["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert "run_tests.py" in s["hooks"]["PostToolUse"][0]["hooks"][0]["command"]


def test_agent_and_commands_have_frontmatter(project):
    for f in [project / ".claude/agents/reviewer.md", *sorted((project / ".claude/commands").glob("*.md"))]:
        assert f.read_text(encoding="utf-8").startswith("---\n"), f


def test_guard_lane_ownership(project):
    (project / ".claude/lane.json").write_text(json.dumps({"task": "T3", "owns": ["src/report/", "src/cli.py"]}))
    assert guard(project, project / "src/report/html.py").returncode == 0
    assert guard(project, project / "src/cli.py").returncode == 0
    assert guard(project, project / "tests/T3/test_html.py").returncode == 0
    assert guard(project, project / "NOTES.md").returncode == 0
    r = guard(project, project / "src/scoring.py")
    assert r.returncode == 2 and "outside lane T3" in r.stderr
    assert guard(project, project / "src/reporting.py").returncode == 2   # prefix must be a directory boundary


def test_guard_unreadable_lane_fails_closed(project):
    (project / ".claude/lane.json").write_text("{not json")
    assert guard(project, project / "src/anything.py").returncode == 2


def _bash():
    """Git Bash on Windows (WSL's bash would create WSL paths the Windows git can't read)."""
    if sys.platform == "win32":
        for c in ("C:/Program Files/Git/bin/bash.exe", "C:/Program Files (x86)/Git/bin/bash.exe"):
            if Path(c).exists():
                return c
        return None
    return shutil.which("bash")


@pytest.mark.skipif(_bash() is None or shutil.which("git") is None, reason="needs bash and git")
def test_lane_script_creates_worktree_with_ownership(project):
    def run(*cmd, cwd=project):
        return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, check=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init")
    out = run(_bash(), "scripts/lane.sh", "T9", "src/report/").stdout
    lane = project.parent / "lane-T9"
    assert "Lane T9 ready" in out
    cfg = json.loads((lane / ".claude/lane.json").read_text())
    assert cfg == {"task": "T9", "owns": ["src/report/"]}
    status = run("git", "status", "--porcelain", cwd=lane).stdout
    assert "lane.json" not in status                                      # excluded, never committed
    payload = json.dumps({"tool_input": {"file_path": str(lane / "src/other.py")}})
    r = subprocess.run([sys.executable, str(lane / ".claude/hooks/guard.py")], input=payload,
                       capture_output=True, text=True)
    assert r.returncode == 2


def clock(project, *args, stdin=""):
    return subprocess.run([sys.executable, str(project / "scripts/clock.py"), *args], input=stdin,
                          capture_output=True, text=True, cwd=project)


def test_clock_silent_until_started(project):
    r = clock(project, "hook", stdin="{}")
    assert r.returncode == 0 and r.stdout == ""


def test_clock_start_status_hook_and_checkin(project):
    from datetime import datetime, timedelta
    demo = (datetime.now() + timedelta(hours=6)).strftime("%H:%M")
    assert clock(project, "start", "--demo", demo).returncode == 0
    st_path = project / ".claude/clock.json"
    st = json.loads(st_path.read_text())
    # pretend we started 95 minutes ago: plan, tests and three check-ins are overdue
    st["start"] = (datetime.now() - timedelta(minutes=95)).strftime("%Y-%m-%dT%H:%M")
    st_path.write_text(json.dumps(st))
    out = clock(project, "hook", stdin="{}").stdout
    assert "to the demo" in out
    assert out.count("OVERDUE") >= 4
    assert "/checkin" in out
    assert clock(project, "checkin", "works", "slice;", "next", "scoring").returncode == 0
    assert clock(project, "done", "plan").returncode == 0
    assert clock(project, "done", "tests").returncode == 0
    out2 = clock(project, "hook", stdin="{}").stdout
    assert out2.count("OVERDUE") == out.count("OVERDUE") - 3
    assert "works slice" in (project / "CHECKINS.md").read_text()
    assert "[x]" in clock(project, "status").stdout


def test_settings_wires_clock_hook(project):
    s = json.loads((project / ".claude/settings.json").read_text())
    assert "clock.py hook" in s["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]


def test_clock_budget_and_report(project):
    assert clock(project, "start", "--budget", "120").returncode == 0
    assert clock(project, "done", "plan").returncode == 0
    assert clock(project, "done", "green").returncode == 0
    out = clock(project, "report").stdout
    assert "| plan | 20 | 0 | -20 |" in out
    assert "| green |" in out and "elapsed to last milestone" in out


def test_loop_decide_stop_rules(project):
    sys.path.insert(0, str(project / "scripts"))
    import importlib
    loop = importlib.import_module("loop")
    importlib.reload(loop)
    assert loop.decide(0, True, True, 0, 1, 6, 1, 30).startswith("done")
    assert loop.decide(0, False, True, 0, 1, 6, 1, 30) is None          # items done but tests red: keep going
    assert loop.decide(3, True, False, 2, 2, 6, 1, 30).startswith("stalled")
    assert loop.decide(3, True, True, 0, 6, 6, 1, 30).startswith("limit")
    assert loop.decide(3, True, True, 0, 1, 6, 31, 30).startswith("limit")
    assert loop.decide(3, True, True, 1, 1, 6, 1, 30) is None
    sys.path.remove(str(project / "scripts"))


def test_loop_counts_open_items_and_dry_run(project):
    (project / "PLAN.md").write_text("- [x] one\n- [ ] two\n  - [ ] three\n")
    (project / "TASKS.md").write_text("| id | wave | role | goal | owns | depends | done when | status |\n|---|---|---|---|---|---|---|---|\n"
                                       "| T1 | 1 | implementer | a | a/ | - | t | done |\n| T2 | 1 | implementer | b | b/ | - | t | todo |\n")
    r = subprocess.run([sys.executable, str(project / "scripts/loop.py"), "--dry-run", "--claude", "claude"],
                       capture_output=True, text=True, cwd=project)
    assert r.returncode == 0
    assert "--permission-mode acceptEdits" in r.stdout and "--max-turns" in r.stdout
    assert "dangerously" not in r.stdout and "bypassPermissions" not in r.stdout
    sys.path.insert(0, str(project / "scripts"))
    import importlib
    loop = importlib.import_module("loop")
    importlib.reload(loop)
    assert loop.open_items() == 3
    sys.path.remove(str(project / "scripts"))
