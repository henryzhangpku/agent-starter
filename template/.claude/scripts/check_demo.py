"""Demo-prep gate: is the end-of-day report really ready?  python .claude/scripts/check_demo.py [--port 8000]

Starts nothing. Expects the server to be running on the port (start it first). Prints one line
per check and exits 1 if any fails, so /demo-prep cannot finish on memory alone.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROOT_OK = {"README.md", "WALKTHROUGH.md", "DECISIONS.md", "CLAUDE.md", "CHECKINS.md", "STATUS.md"}


def get(port: int, path: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:  # report, never crash the gate
        return 0, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    port = ap.parse_args().port
    checks: list[tuple[str, bool, str]] = []
    for path, want in (("/", "<"), ("/pitch", "<"), ("/docs", "<"), ("/architecture", "<")):
        code, body = get(port, path)
        checks.append((f"GET {path}", code == 200 and want in body, f"HTTP {code}"))
    code, body = get(port, "/openapi.json")
    try:
        ok = code == 200 and bool(json.loads(body).get("paths"))
    except ValueError:
        ok = False
    checks.append(("GET /openapi.json has paths", ok, f"HTTP {code}"))
    if ok:
        spec = json.loads(body)
        html = [p for p in spec["paths"] if p in ("/", "/pitch", "/docs", "/openapi.json")]
        checks.append(("spec documents API routes only", not html, ", ".join(html)))
        weak = []
        for path, ops in spec["paths"].items():
            for verb, op in ops.items():
                if not isinstance(op, dict):
                    continue
                resp = op.get("responses", {})
                ok2 = any(str(c).startswith("2") and "content" in r for c, r in resp.items())
                ok4 = any(str(c).startswith("4") for c in resp)
                if not (ok2 and ok4):
                    weak.append(f"{verb.upper()} {path}")
        checks.append(("every operation has a 2xx schema and a 4xx", not weak, ", ".join(weak[:4])))
    code, body = get(port, "/?view=customer")
    checks.append(("customer view", code == 200, f"HTTP {code}"))
    for f in ("docs/ARCHITECTURE.md", "docs/INTEGRATION.md", "docs/QA.md", "docs/TESTS.md", "docs/tools.json",
              "WALKTHROUGH.md", "README.md"):
        checks.append((f, (ROOT / f).exists(), "missing" if not (ROOT / f).exists() else ""))
    arch = (ROOT / "docs/ARCHITECTURE.md")
    checks.append(("architecture has a diagram", arch.exists() and "mermaid" in arch.read_text(encoding="utf-8"), ""))
    extra = sorted(p.name for p in ROOT.glob("*.md") if p.name not in ROOT_OK)
    checks.append(("repo root clean", not extra, ", ".join(extra)))
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    checks.append(("everything committed", not dirty, f"{len(dirty.splitlines())} uncommitted" if dirty else ""))
    bad = 0
    for name, ok, note in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}{('  (' + note + ')') if note and not ok else ''}")
        bad += not ok
    print(f"{len(checks) - bad}/{len(checks)} checks pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
