"""Refresh the agent-starter tooling in this repo from the latest version on GitHub.

    python scripts/update_kit.py

Overwrites only the kit's own tooling: .claude/commands, .claude/agents, .claude/hooks,
.claude/kit, scripts/ and COMMANDS.md. Never touches your project files (PROMPT.md, PLAN.md,
CLAUDE.md, TEAM.md, DECISIONS.md, NOTES.md, TASKS.md, CONTRACTS.md, .claude/guard.json,
.claude/settings.json, tests/, your code or data).
"""
from __future__ import annotations

import io
import tarfile
import urllib.request
from pathlib import Path

URL = "https://github.com/henryzhangpku/agent-starter/archive/refs/heads/main.tar.gz"
PREFIX = "agent-starter-main/template/"
TOOLING = (".claude/commands/", ".claude/agents/", ".claude/hooks/", ".claude/kit/", "scripts/", "COMMANDS.md")


def main() -> None:
    data = urllib.request.urlopen(URL, timeout=30).read()
    added = updated = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            if not m.isfile() or not m.name.startswith(PREFIX):
                continue
            rel = m.name[len(PREFIX):]
            if not rel.startswith(TOOLING):
                continue
            new = tar.extractfile(m).read()
            dest = Path(rel)
            if dest.exists() and dest.read_bytes() == new:
                continue
            existed = dest.exists()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(new)
            print(("updated: " if existed else "added: ") + rel)
            updated += existed
            added += not existed
    print(f"agent-starter tooling: {updated} updated, {added} added. Project files untouched.")


if __name__ == "__main__":
    main()
