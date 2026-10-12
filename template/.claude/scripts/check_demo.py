"""Demo-prep gate: is the end-of-day report really ready?  python .claude/scripts/check_demo.py [--port 8000]

Starts nothing. Expects the server to be running on the port (start it first). Prints one line
per check and exits 1 if any fails, so /demo-prep cannot finish on memory alone.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROOT_OK = {"README.md", "WALKTHROUGH.md", "DECISIONS.md", "CLAUDE.md", "CHECKINS.md", "STATUS.md"}
EDGE_MAX, NODE_MAX = 28, 40          # readable when drawn: details belong in the table under the diagram
RAW_MD_LINK = re.compile(r"\[[^\]\n]{1,80}\]\((?:https?://|/|\./|\.\./)?[\w./#?=&-]+\)")
EDGE_PIPE = re.compile(r"\|([^|\n]+)\|")
EDGE_DASH = re.compile(r"--\s+([^>|\n-][^>\n]*?)\s+-->")
NODE = re.compile(r"[\w-]+\s*(?:\[\[|\[\(|\(\[|\(\(|\[|\(|\{)\s*\"?([^\]\)\}\"\n]+)")


def lint_mermaid(md: str) -> list[str]:
    """Problems that make a Mermaid diagram unreadable once drawn: left-right layout, long labels."""
    problems = []
    for i, block in enumerate(re.findall(r"```mermaid\s*\n(.*?)```", md, re.S), 1):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip() and not ln.strip().startswith("%%")]
        head = lines[0].split() if lines else []
        if head and head[0] in ("flowchart", "graph") and (len(head) < 2 or head[1] not in ("TD", "TB")):
            problems.append(f"diagram {i}: '{lines[0]}', draw it top-down (flowchart TD)")
        body = "\n".join(lines[1:])
        for lab in EDGE_PIPE.findall(body) + EDGE_DASH.findall(body):
            if len(lab.strip().strip('"')) > EDGE_MAX:
                problems.append(f"diagram {i}: arrow label over {EDGE_MAX} chars: '{lab.strip()[:40]}'")
        for lab in NODE.findall(body):
            if len(lab.strip()) > NODE_MAX:
                problems.append(f"diagram {i}: box label over {NODE_MAX} chars: '{lab.strip()[:40]}'")
    return problems


def visible_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|code|pre|textarea)\b.*?</\1>", " ", html)
    return re.sub(r"<[^>]+>", " ", html)


def get(port: int, path: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:  # report, never crash the gate
        return 0, str(e)


def with_assets(port: int, html: str) -> str:
    """The page plus the same-origin stylesheets and scripts it loads."""
    refs = re.findall(r"(?:href|src)=[\"'](/[^\"']+\.(?:css|js))[\"']", html)
    return "\n".join([html] + [get(port, ref)[1] for ref in refs])


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
    pages = {p: get(port, p) for p in ("/", "/pitch", "/architecture", "/integration", "/qa")}
    shown = {p: with_assets(port, b) for p, (c, b) in pages.items() if c == 200}
    nolook = [p for p in ("/", "/pitch", "/architecture") if "look v1" not in shown.get(p, "")]
    checks.append(("pages use the shared look (.claude/kit/look.css)", not nolook, ", ".join(nolook)))
    dark = [p for p, t in shown.items() if re.search(r"prefers-color-scheme:\s*dark", t)]
    checks.append(("light by default, dark only by toggle", not dark, ", ".join(dark)))
    checks.append(("diagrams drawn big, click for full screen (.claude/kit/diagrams.js)",
                   "diagrams v1" in shown.get("/architecture", ""), ""))
    raw = [p for p in shown if RAW_MD_LINK.search(visible_text(pages[p][1]))
           or re.search(r"\]\((?!https?://)[^)\s]*\.md\)|href=[\"'](?!https?://)[^\"']*\.md[\"']", pages[p][1])]
    checks.append(("doc links are page links (/integration), not raw markdown or .md files", not raw, ", ".join(raw)))
    for f in ("docs/ARCHITECTURE.md", "docs/INTEGRATION.md", "docs/QA.md", "docs/TESTS.md", "docs/tools.json",
              "WALKTHROUGH.md", "README.md"):
        checks.append((f, (ROOT / f).exists(), "missing" if not (ROOT / f).exists() else ""))
    arch = (ROOT / "docs/ARCHITECTURE.md")
    checks.append(("architecture has a diagram", arch.exists() and "mermaid" in arch.read_text(encoding="utf-8"), ""))
    lint = lint_mermaid(arch.read_text(encoding="utf-8")) if arch.exists() else []
    checks.append(("diagrams readable: top-down, short labels", not lint, "; ".join(lint[:3])))
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
