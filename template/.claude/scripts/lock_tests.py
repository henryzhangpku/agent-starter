"""Lock acceptance tests so the agent can no longer edit them.

  python .claude/scripts/lock_tests.py tests/test_acceptance.py [more paths]
  python .claude/scripts/lock_tests.py --list

Run it right after the failing acceptance tests are written and committed
(RUNBOOK Phase 4). Adds the paths to "acceptance_tests" in .claude/guard.json;
from then on the guard hook refuses any agent edit to them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / ".claude" / "guard.json"


def main(argv: list[str]) -> int:
    cfg = json.loads(CFG.read_text(encoding="utf-8")) if CFG.exists() else {}
    locked = cfg.setdefault("acceptance_tests", [])
    if not argv or argv == ["--list"]:
        print("locked:", ", ".join(locked) or "(none)")
        return 0
    for p in argv:
        rel = Path(p).as_posix().lstrip("./")
        if not (ROOT / rel).exists():
            print(f"not found: {rel}")
            return 1
        if rel not in locked:
            locked.append(rel)
    CFG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print("locked:", ", ".join(locked))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
