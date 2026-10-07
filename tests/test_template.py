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


def test_acceptance_tests_writable_until_locked(project):
    assert guard(project, project / "tests/test_acceptance.py").returncode == 0      # Phase 4: agent writes them
    r = subprocess.run([sys.executable, str(project / "scripts/lock_tests.py"), "tests/test_acceptance.py"],
                       capture_output=True, text=True, cwd=project)
    assert r.returncode == 0 and "tests/test_acceptance.py" in r.stdout
    assert guard(project, project / "tests/test_acceptance.py").returncode == 2      # locked afterwards


def test_guard_blocks_protected_and_acceptance(project):
    subprocess.run([sys.executable, str(project / "scripts/lock_tests.py"), "tests/test_acceptance.py"],
                   capture_output=True, text=True, cwd=project)
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


# --- the guard also watches the shell -----------------------------------------

def guard_bash(project, command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(project / ".claude/hooks/guard.py")],
                          input=payload, capture_output=True, text=True)


def lock(project):
    subprocess.run([sys.executable, str(project / "scripts/lock_tests.py"), "tests/test_acceptance.py"],
                   capture_output=True, text=True, cwd=project)


@pytest.mark.parametrize("command", [
    "sed -i 's/assert/# assert/' tests/test_acceptance.py",
    "echo 'pass' > tests/test_acceptance.py",
    "cat new.py >> tests/test_acceptance.py",
    "printf x | tee data/calls.jsonl",
    "cp /tmp/fake.csv data/x.csv",
    "mv tests/test_acceptance.py tests/old.py && touch tests/test_acceptance.py",
    "rm data/calls.jsonl",
    "python -c \"open('tests/test_acceptance.py','w').write('')\"",
    "git checkout -- tests/test_acceptance.py",
    "perl -pi -e 's/1/2/' data/x.csv",
    "Set-Content -Path data/x.csv -Value ''",
])
def test_guard_blocks_shell_writes_to_protected_paths(project, command):
    lock(project)
    r = guard_bash(project, command)
    assert r.returncode == 2, command
    assert "BLOCKED" in r.stderr


@pytest.mark.parametrize("command", [
    "cat tests/test_acceptance.py",
    "python -m pytest -q tests/test_acceptance.py",
    "grep -n assert tests/test_acceptance.py > /tmp/asserts.txt",
    "diff data/calls.jsonl /tmp/other.jsonl",
    "echo hi > src/app.py",
    "sed -i 's/a/b/' src/app.py",
    "git status",
    "git commit -m 'step 3'",
])
def test_guard_allows_shell_reads_and_unprotected_writes(project, command):
    lock(project)
    assert guard_bash(project, command).returncode == 0, command


def test_guard_shell_respects_lane_ownership(project):
    (project / ".claude/lane.json").write_text(json.dumps({"task": "T3", "owns": ["src/report/"]}))
    assert guard_bash(project, "echo x > src/report/a.py").returncode == 0
    assert guard_bash(project, "echo x > src/other.py").returncode == 2


def test_settings_wire_the_guard_to_the_shell(project):
    s = json.loads((project / ".claude/settings.json").read_text())
    shell = [m for m in s["hooks"]["PreToolUse"] if "Bash" in m["matcher"]]
    assert shell and "guard.py" in shell[0]["hooks"][0]["command"]


# --- tests scoped to the edit once the suite is slow --------------------------

def run_tests_hook(project, edited):
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(edited)}})
    return subprocess.run([sys.executable, str(project / ".claude/hooks/run_tests.py")],
                          input=payload, capture_output=True, text=True, cwd=project)


def test_run_tests_skips_prose_and_scopes_when_slow(project):
    assert run_tests_hook(project, project / "NOTES.md").stdout == ""
    (project / "src").mkdir(exist_ok=True)
    (project / "src" / "pricing.py").write_text("def f():\n    return 1\n")
    (project / "tests" / "test_pricing.py").write_text("def test_f():\n    assert True\n")
    (project / ".claude" / "test_timing.json").write_text(json.dumps({"full_seconds": 999}))
    r = run_tests_hook(project, project / "src" / "pricing.py")
    if "pytest is not installed" in r.stdout:
        pytest.skip("pytest not importable by the hook interpreter")
    assert r.returncode == 0, r.stderr
    assert "scoped to this edit" in r.stdout
    r = run_tests_hook(project, project / "src" / "nothing_maps_here.py")
    assert "no tests belong to" in r.stdout


def test_run_tests_maps_files_to_their_tests(project):
    sys.path.insert(0, str(project / ".claude" / "hooks"))
    try:
        import importlib
        rt = importlib.import_module("run_tests")
        importlib.reload(rt)
        rt.ROOT = project
        (project / "tests" / "billing").mkdir(parents=True)
        a = project / "tests" / "test_ledger.py"; a.write_text("")
        b = project / "tests" / "billing" / "test_invoice.py"; b.write_text("")
        assert rt.tests_for(project / "src" / "ledger.py") == [a]
        assert b in rt.tests_for(project / "src" / "billing" / "anything.py")
        assert rt.tests_for(a) == [a]
    finally:
        sys.path.pop(0)
        sys.modules.pop("run_tests", None)


# --- the context budget -------------------------------------------------------

def budget(project, transcript):
    payload = json.dumps({"transcript_path": str(transcript)})
    return subprocess.run([sys.executable, str(project / ".claude/hooks/context_budget.py")],
                          input=payload, capture_output=True, text=True)


def transcript_with(tmp_path, tokens):
    t = tmp_path / "session.jsonl"
    rows = [{"type": "user", "message": {"role": "user", "content": "hi"}},
            {"type": "assistant", "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": tokens - 10,
                                                        "cache_creation_input_tokens": 0, "output_tokens": 50}}}]
    t.write_text("\n".join(json.dumps(r) for r in rows))
    return t


def test_context_budget_silent_then_warns_then_stops(project, tmp_path):
    assert budget(project, transcript_with(tmp_path, 40_000)).stdout == ""
    assert "suggest updating NOTES.md" in budget(project, transcript_with(tmp_path, 180_000)).stdout
    out = budget(project, transcript_with(tmp_path, 320_000)).stdout
    assert "Before anything else" in out and "/clear" in out
    assert budget(project, tmp_path / "missing.jsonl").stdout == ""


def test_settings_wire_the_context_budget(project):
    s = json.loads((project / ".claude/settings.json").read_text())
    cmds = [h["command"] for m in s["hooks"]["UserPromptSubmit"] for h in m["hooks"]]
    assert any("context_budget.py" in c for c in cmds)
    assert any("clock.py hook" in c for c in cmds)


def test_agent_cli_builtins_and_override(project):
    sys.path.insert(0, str(project / "scripts"))
    import importlib
    ac = importlib.import_module("agent_cli")
    importlib.reload(ac)
    c = ac.command("claude", "P", 7, exe="claude")
    assert c[:3] == ["claude", "-p", "P"] and "--max-turns" in c and "7" in c and "acceptEdits" in c
    assert "dangerously" not in " ".join(c)
    assert ac.command("codex", "P", exe="codex") == ["codex", "exec", "--full-auto", "P"]
    assert ac.command("gemini", "P", exe="gemini") == ["gemini", "-p", "P", "--approval-mode", "auto_edit"]
    (project / ".claude/agent_cli.json").write_text(json.dumps({"fake": ["python", "-c", "print(1)", "{prompt}"]}))
    importlib.reload(ac)
    assert ac.command("fake", "hello") == ["python", "-c", "print(1)", "hello"]
    with pytest.raises(ValueError):
        ac.command("nope", "x")
    sys.path.remove(str(project / "scripts"))


@pytest.mark.skipif(shutil.which("git") is None, reason="needs git")
def test_fanout_ranks_attempts_and_cleans_up(project):
    def run(*cmd, cwd=project):
        return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True)
    # a tiny project: one module, one test that needs add() to return a+b
    (project / "calc.py").write_text("def add(a, b):\n    raise NotImplementedError\n")
    (project / "tests" / "test_calc.py").write_text("from calc import add\n\ndef test_add():\n    assert add(2, 3) == 5\n")
    (project / "tests" / "test_acceptance.py").unlink()
    good = "open('calc.py','w').write('def add(a, b): return a + b')"
    bad = "open('calc.py','w').write('def add(a, b): return a - b')"
    (project / ".claude/agent_cli.json").write_text(json.dumps({
        "good": [sys.executable, "-c", good], "bad": [sys.executable, "-c", bad]}))
    for c in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
              ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"]):
        run(*c)
    env_cmd = [sys.executable, str(project / "scripts/fanout.py"), "--prompt-file", "PROMPT.md",
               "--agents", "bad,good", "--minutes", "2"]
    r = subprocess.run(env_cmd, cwd=project, capture_output=True, text=True,
                       env={**__import__("os").environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
    assert r.returncode == 0, r.stdout + r.stderr
    cmp = (project / "COMPARE.md").read_text()
    rows = [l for l in cmp.splitlines() if l.startswith("| 1 ") or l.startswith("| 2 ")]
    assert "fan/PROMPT/2" in rows[0] and "good" in rows[0] and "1 pass" in rows[0]
    assert "fan/PROMPT/1" in rows[1] and "fail" in rows[1]
    assert (project.parent / "fan-PROMPT-2").exists()
    run(sys.executable, str(project / "scripts/fanout.py"), "--cleanup", "PROMPT")
    assert not (project.parent / "fan-PROMPT-1").exists()
    assert "fan/PROMPT" not in run("git", "branch").stdout


def test_agents_md_points_to_claude_md(project):
    txt = (project / "AGENTS.md").read_text(encoding="utf-8")
    assert "CLAUDE.md" in txt and "acceptance tests" in txt
