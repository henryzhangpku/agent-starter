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
