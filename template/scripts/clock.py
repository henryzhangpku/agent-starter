"""The build-day clock: check-ins and milestones you can't forget.

  python scripts/clock.py start --demo 16:30 [--every 30]   once, when the prompt is given
  python scripts/clock.py status                            the timeline, what's done, what's next
  python scripts/clock.py checkin "works X; next Y; deciding Z"   log a check-in (the /checkin command does this)
  python scripts/clock.py done <milestone>                  mark a milestone done (plan, tests, slice, stop, readme)
  python scripts/clock.py report                            actual minutes per phase vs plan (for estimating)
  python scripts/clock.py hook                              used by the UserPromptSubmit hook

Practice runs to completion: start with --budget 120 instead of --demo, mark
each milestone with `done` as you actually reach it (plus `done green` when
every acceptance test passes), and `report` prints a row of real phase times.

The hook runs on every prompt you send. It adds one line of context for the
agent: time to the demo and what's next, and a loud reminder when a check-in or
milestone is due or overdue. The agent then tells you; you never run past one.
State lives in .claude/clock.json; check-ins are appended to CHECKINS.md.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".claude" / "clock.json"
LOG = ROOT / "CHECKINS.md"
FMT = "%Y-%m-%dT%H:%M"
HEADS_UP = timedelta(minutes=10)

# (key, label, minutes from start or None, minutes before demo or None)
MILESTONES = [
    ("plan", "plan agreed and saved as PLAN.md", 20, None),
    ("tests", "failing acceptance tests committed; say the minute-30 line", 30, None),
    ("slice", "thinnest end-to-end slice running; demo it to the room", 120, None),
    ("stop", "stop building features; run everything; held-out set once", None, 60),
    ("readme", "README and DECISIONS tidy; rehearse the walkthrough", None, 30),
    ("demo", "walkthrough: demo, git log, three decisions, gaps, next", None, 0),
]
EXTRA = {"green": "all acceptance tests passing"}


def now() -> datetime:
    return datetime.now().replace(second=0, microsecond=0)


def load() -> dict | None:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def schedule(state: dict) -> list[dict]:
    start = datetime.strptime(state["start"], FMT)
    demo = datetime.strptime(state["demo"], FMT)
    items = []
    for key, label, after, before in MILESTONES:
        at = start + timedelta(minutes=after) if after is not None else demo - timedelta(minutes=before)
        items.append({"key": key, "label": label, "at": at, "kind": "milestone"})
    t = start + timedelta(minutes=state["every"])
    i = 1
    while t < demo - timedelta(minutes=30):
        items.append({"key": f"checkin-{i}", "label": "check-in: works / next / deciding / risk, out loud",
                      "at": t, "kind": "checkin"})
        t += timedelta(minutes=state["every"])
        i += 1
    items.sort(key=lambda x: x["at"])
    for it in items:
        it["done"] = it["key"] in state.get("done", {})
    return items


def hm(d: timedelta) -> str:
    mins = int(d.total_seconds() // 60)
    sign = "-" if mins < 0 else ""
    mins = abs(mins)
    return f"{sign}{mins // 60}h{mins % 60:02d}m" if mins >= 60 else f"{sign}{mins}m"


def parse_clock(s: str, base: datetime) -> datetime:
    h, m = map(int, s.split(":"))
    t = base.replace(hour=h, minute=m)
    return t if t > base else t + timedelta(days=1)


def cmd_start(a) -> int:
    t0 = now()
    if not a.demo and not a.budget:
        print("give --demo HH:MM or --budget MINUTES")
        return 1
    demo = parse_clock(a.demo, t0) if a.demo else t0 + timedelta(minutes=a.budget)
    save({"start": t0.strftime(FMT), "demo": demo.strftime(FMT), "every": a.every, "done": {}})
    if not LOG.exists():
        LOG.write_text("# Check-ins\n\n| time | note |\n|---|---|\n", encoding="utf-8")
    print(f"Clock started {t0:%H:%M}; demo {demo:%H:%M}; check-ins every {a.every} min.")
    return cmd_status(a)


def cmd_status(_a) -> int:
    st = load()
    if not st:
        print("Clock not started: python scripts/clock.py start --demo 16:30")
        return 1
    n = now()
    demo = datetime.strptime(st["demo"], FMT)
    print(f"now {n:%H:%M} · demo {demo:%H:%M} ({hm(demo - n)} left)")
    for it in schedule(st):
        mark = "x" if it["done"] else ("!" if it["at"] <= n else " ")
        print(f"  [{mark}] {it['at']:%H:%M}  {it['label']}")
    return 0


def cmd_checkin(a) -> int:
    st = load()
    if not st:
        print("Clock not started.")
        return 1
    n = now()
    due = [it for it in schedule(st) if it["kind"] == "checkin" and not it["done"] and it["at"] <= n + HEADS_UP]
    key = due[0]["key"] if due else f"extra-{n:%H%M}"
    st["done"][key] = n.strftime(FMT)
    save(st)
    note = " ".join(a.note).strip() or "(no note)"
    if not LOG.exists():
        LOG.write_text("# Check-ins\n\n| time | note |\n|---|---|\n", encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"| {n:%H:%M} | {note.replace('|', '/')} |\n")
    print(f"Check-in logged at {n:%H:%M} ({key}).")
    return 0


def cmd_done(a) -> int:
    st = load()
    if not st:
        print("Clock not started.")
        return 1
    keys = {m[0] for m in MILESTONES} | set(EXTRA)
    if a.milestone not in keys:
        print(f"Unknown milestone; use one of: {', '.join(sorted(keys))}")
        return 1
    st["done"][a.milestone] = now().strftime(FMT)
    save(st)
    print(f"{a.milestone} marked done.")
    return 0


def cmd_report(_a) -> int:
    st = load()
    if not st:
        print("Clock not started.")
        return 1
    start = datetime.strptime(st["start"], FMT)
    plan = {it["key"]: it["at"] for it in schedule(st)}
    done = {k: datetime.strptime(v, FMT) for k, v in st.get("done", {}).items()}
    order = ["plan", "tests", "slice", "green", "stop", "readme", "demo"]
    print("| milestone | planned (min) | actual (min) | late by |")
    print("|---|---|---|---|")
    for k in order:
        p = int((plan[k] - start).total_seconds() // 60) if k in plan else None
        a = int((done[k] - start).total_seconds() // 60) if k in done else None
        late = (a - p) if (a is not None and p is not None) else None
        print(f"| {k} | {'' if p is None else p} | {'' if a is None else a} | {'' if late is None else late} |")
    cis = [it for it in schedule(st) if it["kind"] == "checkin" and it["at"] <= now()]
    on_time = sum(1 for it in cis if it["done"])
    total = int((max(done.values()) - start).total_seconds() // 60) if done else 0
    print()
    print(f"check-ins logged: {on_time}/{len(cis)} due so far; elapsed to last milestone: {total} min")
    return 0


def cmd_hook(_a) -> int:
    sys.stdin.read()
    st = load()
    if not st:
        return 0  # no clock running: say nothing
    n = now()
    demo = datetime.strptime(st["demo"], FMT)
    items = schedule(st)
    overdue = [it for it in items if not it["done"] and it["at"] <= n]
    soon = [it for it in items if not it["done"] and n < it["at"] <= n + HEADS_UP]
    nxt = next((it for it in items if not it["done"] and it["at"] > n), None)
    line = f"[clock] {n:%H:%M}, {hm(demo - n)} to the demo"
    if nxt:
        line += f"; next: {nxt['at']:%H:%M} {nxt['label']}"
    print(line)
    for it in overdue:
        late = hm(n - it["at"])
        verb = "run /checkin and say it out loud" if it["kind"] == "checkin" else \
            f"then: python scripts/clock.py done {it['key']}"
        print(f"[clock] OVERDUE by {late}: {it['label']}. Tell the human first, before anything else; {verb}.")
    for it in soon:
        print(f"[clock] in {hm(it['at'] - n)}: {it['label']}. Mention it to the human.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--demo", help="demo time today, HH:MM (24h)")
    s.add_argument("--budget", type=int, help="or: minutes from now to the demo (practice runs)")
    s.add_argument("--every", type=int, default=30, help="minutes between check-ins")
    s.set_defaults(fn=cmd_start)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    c = sub.add_parser("checkin")
    c.add_argument("note", nargs="*")
    c.set_defaults(fn=cmd_checkin)
    d = sub.add_parser("done")
    d.add_argument("milestone")
    d.set_defaults(fn=cmd_done)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    sub.add_parser("hook").set_defaults(fn=cmd_hook)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
