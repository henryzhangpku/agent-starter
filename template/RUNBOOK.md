# Runbook: one build day with a coding agent, start to finish

Every step has a time box, what you do, what you say or paste, what it produces,
and the commit that closes it. Times assume a 9:30 start and a 4:30 demo; shift
them to your day. Copy-paste prompts are in `> quotes`.

## Principles (re-read before every run)

**Specify before you generate. Verify independently. Present only what is proven. Talk the whole time.**

Print or keep open `CARD.md`: the whole day on one page.

- **Productivity:** front-load the spec (PROMPT.md, contracts, failing tests);
  thinnest end-to-end slice first, runnable at every commit; one small,
  checkable task per prompt; decide the cut list by minute 20; the agent writes
  plumbing, tests-from-spec and docs, you make decisions and find edge cases.
- **Quality through separated roles:** the agent that writes code never grades
  it. Architect sets contracts; implementer builds one task; test-engineer
  writes tests from the spec without reading the code; reviewer and
  safety-reviewer judge with fresh context; you run the tests yourself and
  decide. Separation is the point, not the number of agents: two or three
  roles that check each other beat five that agree with each other.
- **Correctness:** tests are the spec and are protected; test invariants, not
  just examples; measure against a baseline and, where possible, a human
  ceiling; read every diff, reject clever code; fail closed.
- **Presentable:** one command demos it; README leads with the number and
  what it's compared against; git log tells the story; visuals last; name
  the gaps first.
- **Time split for a three-hour build:** ~15% framing, 50% building, 20%
  verifying, 15% presenting. `clock.py report` shows where yours drifts.

## Pick the mode in the first five minutes

| situation | path through this runbook |
|---|---|
| **New, standalone problem** | Phases 0 to 10 in order |
| **Their existing codebase** | Phase 0 (skip `git init`; branch instead), **Phase A**, then 1 to 10; ship with **Phase S** |
| **A feature or subsystem with the team, deployed** | Phase A, 1 to 4, then **Phase T** for parallel work, **Phase S** to ship |
| **Short on time** | 0, 1, 3, 4, 5, 9: plan, failing tests, thinnest slice, walkthrough |

Keep `TEAM.md` open all day in every mode: who owns what, what you asked, what they said.

---

## Phase 0. Set up (10 minutes, before the prompt)

**0.1 Check the machine (1 min).**
```
claude --version; git --version; python3 --version || python --version
```
Missing Claude Code? `curl -fsSL https://claude.ai/install.sh | bash` (macOS/Linux)
or `irm https://claude.ai/install.ps1 | iex` (Windows). Then `claude` once to sign in.

**0.2 Make the project (1 min).**
```
mkdir build && cd build && git init
```
In someone else's repo instead: `git checkout -b build/<topic>` and ask before adding files.

**0.3 Install the kit (1 min).** Ask first if it's not your machine.
```
curl -fsSL https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.sh | bash
# Windows: irm https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.ps1 | iex
```

**0.4 Python loop (3 min).**
```
python3 -m venv .venv && . .venv/bin/activate && pip install pytest     # Windows: .venv\Scripts\activate
python -m pytest -q                                                     # the placeholder test passes
```

**0.5 Smoke-test the agent (2 min).** Start `claude`, then:
> Read CLAUDE.md and tell me in three lines how you will work in this repo. Do not edit anything.

It should repeat: plan first, small steps, tests first, protected tests. If it doesn't, the file wasn't read.

**0.6 Commit.** `git add -A && git commit -m "start: agent kit"`

---

## Phase 1. Capture the problem (minutes 0-5)

**1.0 Start the clock** the moment the prompt is given, with the demo time you agree:
```
python scripts/clock.py start --demo 16:30 --every 30
```
Practice runs: `python scripts/clock.py start --budget 120` instead, run the
build to completion, mark each milestone as you actually reach it
(`clock.py done plan|tests|slice|green|stop|readme|demo`, where `green` means
every acceptance test passes), and finish with `clock.py report` for the real
minutes per phase. That table is how you learn your own pace.

From now on every prompt you send carries one line of time context, and the
agent tells you when a check-in or milestone is due or overdue.
`python scripts/clock.py status` shows the whole timeline.

**1.1 Write the prompt word for word** into `PROMPT.md` under *Word for word*,
while it is being explained. Say: "Let me write that down exactly."

**1.2 Find out who to talk to.** `/questions` reads the prompt and writes into
`TEAM.md` the roles this build depends on, up to three prompt-specific
questions for each, when to ask them, and what you can offer each person.
It ends with the three questions to ask in the first five minutes.

**1.3 Ask them out loud** (the generic five are also in `PROMPT.md`) and type the
answers: who uses the output, what data, what done looks like, what is off
limits, which mistake costs more.

**1.4 Write your assumptions** at the bottom, and read them back: "I'm assuming
X and Y; correct me."

**Output:** `PROMPT.md` filled. Nothing else yet.

---

## Phase 2. Tell the agent the facts (minutes 5-10)

**2.1 Fill the project facts** at the bottom of `CLAUDE.md`: data path and
format, the one module allowed to call a model, the data contract between
parts, the test command.

**2.2 Set the guard paths** in `.claude/guard.json`: input data directories
under `protected_prefixes`, any audit file under `protected_files`.

**2.3 Commit.** `git commit -am "prompt, answers, working agreement"`

---

## Phase 3. Plan out loud (minutes 10-20)

**3.1 Enter plan mode:** `Shift+Tab` until it says plan mode. Paste:
> Read PROMPT.md, CLAUDE.md and the data. Propose a plan for this build:
> the thinnest end-to-end slice first, then improvements in priority order.
> For each step: what it produces and the test that proves it. List the
> risks and what you would cut if we run short. Do not write code.

**3.2 Edit its plan with the people in the room.** Say each change aloud:
- **Cut:** what the plan over-builds for one day.
- **Reorder:** a crude result for every input first; improvements after.
- **Add:** what it missed (measurement, bad-input handling, the human ceiling).
- **Ask one question** of the team about the trade-off that matters most.

**3.3 Save it:**
> Save the agreed plan as PLAN.md using its existing structure: a checkbox and
> a test name per step, the cut list and the risks. Leave the check-in table.

**3.4 Log the first decisions** in `DECISIONS.md` (e.g. "proposed a vector
store / chose none / nothing is retrieved").

**3.5 Commit.** `git commit -am "plan"`

---

## Phase 4. Define done (minutes 20-30)

**4.1 Dictate five to ten acceptance tests** in plain English, each one checkable:
> Write these as pytest tests in tests/test_acceptance.py, replacing the
> placeholder. They should fail now. Do not implement anything.
> 1. ...
> 2. ...

Good tests check behaviour: every input gets one output; outputs are in valid
ranges; bad inputs go to a review list; same input twice gives the same output;
evidence points at real input; the held-out set is read once.

**4.2 Read every test before running it.** Reject any that is trivially true
or tests an implementation detail.

**4.3 Run them and show they fail:** `python -m pytest -q`

**4.4 Commit.** `git commit -am "acceptance tests (failing)"`

**4.5 Say the minute-30 line:** "Here's the plan and the N tests that define
done. Thinnest slice first; I'll check in at <time>."

From now on the guard refuses any edit to `tests/test_acceptance.py`.

---

## Phase 5. Thinnest slice (until about 11:30)

Loop for each of the first plan steps:

**5.1** `/next`. The agent names files, the test, and a three-line plan, then waits.
**5.2** Read the plan; say "go" or correct it in one sentence.
**5.3** It makes the test pass with the smallest change; the test hook runs the suite after every edit.
**5.4** **Read the diff** before accepting. Explain one line aloud now and then. Reject with a reason when it's wrong.
**5.5** Commit: `git commit -am "step N: <what>"`

**Stop rule:** if the agent goes the wrong way, `Esc` and redirect in one
sentence. Fighting it for five minutes? Take the keyboard.

**Milestone (about 11:30):** every input gets a crude output in the contract
format. **Demo it to the room**, even if it's ugly.

---

## Phase 6. Check in every 30 minutes

> /checkin

Say the four lines out loud: works, next, deciding, risk. It fills the row in
`PLAN.md` and logs the time to `CHECKINS.md`, so the clock stops nagging. Mark
milestones as you hit them: `python scripts/clock.py done slice` (plan, tests,
slice, stop, readme). Before lunch and before any `/clear`, also:
> Update NOTES.md: what is done, what is in progress, open questions, gotchas.

Then `/clear` is free: the next session reads `PROMPT.md`, `PLAN.md` and `NOTES.md`.

---

## Phase 7. Improve, with review (midday to about 3:30)

**7.1** Keep the `/next` loop through the improvement steps.

**7.2 After each step, before committing:**
> Use the reviewer subagent on the last change.

Act on blockers; log suggestions you decline in `DECISIONS.md`.

**7.3 Optional second lane** (only once the contract is fixed and the slice works):
fill `LANE.md`, then
```
git worktree add ../build-<lane> -b <lane>
cd ../build-<lane> && claude        # paste LANE.md as the first message
```
You merge it; read its diff aloud first. Better still: give that lane to a person.

**7.4 Measure:** run the evaluation on the development split; touch any
held-out set once, at the end, and say so.

---

## Phase 7b. A bounded loop for a well-specified backlog (optional)

When the remaining plan items are small, specified and covered by tests:
```
python scripts/loop.py --iterations 4 --minutes 15      # --dry-run first to see the command
```
Fresh headless sessions take one item per pass, keep the tests green, commit,
and log to LOOP.md; it stops when done, stalled twice, or at the limit.
Say it out loud, keep it short and visible, and review every commit after.

## Phase 8. Stop building (about 3:30 to 4:00)

**8.1 Stop adding features.** Run everything on all inputs: `python -m pytest -q` and the main command.
**8.2 Held-out set, once.** Record the result in `NOTES.md`.
**8.3 Write the README:**
> Write README.md: one-sentence purpose; how to run it; the headline result
> with the number to compare it against; three decisions from DECISIONS.md;
> what is not done and the next three steps. Under 40 lines.

**8.4 Tidy `DECISIONS.md`** to its five to eight real decisions.
**8.5 Commit.** `git commit -am "walkthrough"`

---

## Phase 9. Walkthrough (about 4:00 to 4:30, five minutes spoken)

1. **Demo** (90 seconds): run it; show one input end to end.
2. **The story:** `git log --oneline`: plan, failing tests, each step, review, held-out set.
3. **Three decisions** from `DECISIONS.md`, including one where you overrode the tool.
4. **Honest gaps:** what fails, before anyone else names it.
5. **Next three steps.**

---

## Phase 9b (practice builds). Open-source it

`/publish` prepares README, licence, demo page and a post draft after the
checks (secrets, names, data provenance). You create the repo and push;
share one build at a time.

## Phase 10. Leave clean

`/logout` in Claude Code; sign out of browser sessions; close private
windows. Push nothing to your own accounts from someone else's machine unless
they asked. Leave the repo and branch where they can see it.

---

## Phase A. Existing codebase: learn before you touch (15-20 minutes)

**A.1** Branch: `git checkout -b <you>/<feature>`. Their `CLAUDE.md`, linters
and conventions win; the installer never overwrites their files. Ask before
adding the kit's files; if they'd rather not, keep them in a sibling folder.

**A.2** `/onboard` (explorer subagent, read-only). You get: how to run, test
and ship; the main flow; conventions with example files; files the change
will touch; owners from git history; questions for the team.

**A.3 Talk to people, with the questions it produced.** One question per
owner, short: "I'm adding X near your Y; is Z the right seam, or is there a
pattern you'd rather I follow?" Write answers in `TEAM.md`. This is the
collaboration they are watching.

**A.4** Run their tests once before changing anything, so you know the baseline.

**A.5** Copy the conventions you found into the project facts in `CLAUDE.md`
(or a local note) so every agent session follows them.

---

## Phase T. Team mode: parallel agents like an engineering team (after Phase 4)

Use once the plan and acceptance tests exist and the work splits cleanly.
Three to five parallel tasks is the sweet spot; more costs more to integrate
than it saves.

**T.1 Split.** `/team-plan`: the architect subagent writes `CONTRACTS.md`
(every shared interface, fixed first) and `TASKS.md` (tasks with disjoint
file ownership, dependencies, done-when tests, waves). **You** approve the
split out loud: "contracts first, then three tasks in parallel."

**T.2 Land the contracts.** The task that owns shared code (usually T1) goes
first, alone. Commit.

**T.3 Run a wave.** `/dispatch 1`. Implementer and test-engineer subagents
run in parallel, each limited to its task's paths. Test-engineers write tests
from the spec without reading the code, so the tests are independent.

**T.4 Integrate.** `/integrate`: full test run, a path-ownership check, the
reviewer and (for risky changes) the safety-reviewer in parallel, then one
commit per task after your approval.

**T.5 Heavier isolation, when tasks run long:** a separate session per task
in its own worktree, with the guard enforcing ownership:
```
scripts/lane.sh T3 src/report/          # Windows: scripts\lane.ps1 T3 src/report/
cd ../lane-T3 && claude                  # paste the printed brief
git merge --no-ff lane/T3                # from the main checkout, after review
```

**T.6 Mix in people.** A teammate can own a task row like any agent: same
contract, same done-when tests. Hand them one; it's the best collaboration
signal of the day. Record it in `TEAM.md`.

**Roles available:** architect (opus, plans and contracts), implementer
(sonnet, one task), test-engineer (sonnet, independent tests), reviewer
(fresh context), safety-reviewer (opus, failure paths and data), explorer
(read-only mapping).

---

## Phase S. Ship it through their process

**S.1** `/ship`: the team's own test, lint and type commands; scope check;
migrations; rollout behind a flag or safe default; rollback steps;
observability; a PR description with reviewers from CODEOWNERS.

**S.2** Open the PR the way they do. Ask the owner from `TEAM.md` to review.
Never merge or deploy on your own on someone else's system; walk through the
rollout and rollback with whoever owns deploys, then let their pipeline do it.

**S.3** After deploy: check the signal you named in S.1 (a log line, a metric,
a dashboard) and say what you saw.

---

## The rules that apply all day

- Say the prompt before you type it.
- One small task per prompt; never "build the system".
- Read every diff; run the tests yourself; trust test output, not "done".
- Money, identity and compliance checks stay in plain code you can explain.
- Never let the agent edit or delete a test to make it pass (the guard enforces it).
- No auto-accept, no plugins, no code pasted from outside the room.
