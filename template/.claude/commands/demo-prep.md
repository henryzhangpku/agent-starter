---
description: Step 6 - stop building; run everything, tidy README and DECISIONS, write the 5-minute walkthrough
---

We are stopping feature work. Do these in order and do not add features:
1. Run the full suite and the end-to-end command; show the result. Start the
   demo page and check it loads and works on three real inputs; the live
   demo is the page, not the terminal. Refresh its "How we spent the day" timeline from
   the clock and git log, credit people by name, and check it against the
   MVP demo bar in make-plan.md and fix any gap before writing the walkthrough.
2. `python .claude/scripts/clock.py done stop`.
3. **Senior-engineer pass on the code** (the team will open the repo):
   use the reviewer on the whole product package, not a diff, for
   simplicity only. Apply the safe simplifications: delete dead code and
   unused helpers, merge one-caller abstractions, cut duplicate or
   implementation-detail tests, clear names. Behaviour must not change: the
   acceptance tests stay green. Report lines and tests before and after.
4. **Clean the repo** so it reads like an engineer's project, not a kit.
   The root keeps only README.md, WALKTHROUGH.md, DECISIONS.md and CLAUDE.md
   (plus code, tests, data). `git mv` PROMPT.md, PLAN.md and CONTRACTS.md
   into `docs/`, and TEAM.md, TASKS.md, NOTES.md, STATUS.md, CHECKINS.md,
   COMMANDS.md and AGENTS.md into `docs/process/` (delete any that still hold
   only template text). Leave `.claude/` and `.claude/scripts/` (the tooling); README
   says in one line that they are the agent-starter tooling. Do not rewrite
   history.
4b. Write `docs/TESTS.md`: a table of each test file, the behaviours it
   proves, how many tests, and which risk it guards (the hard rules first);
   name any part of the product with no test. Keep it to one screen.
5. Update README.md: what it does, how to run it, the result, known gaps.
6. Tidy DECISIONS.md to the three decisions that matter most, each with the
   alternative we rejected and why.
6b. Build **the internal pitch** in the look from `.claude/kit/LOOK.md` (link the kit's `look.css`; light by default, dark only by the toggle): `/pitch` on the same server, one HTML file,
   no libraries, arrow keys and click to advance, readable from the back of a
   room, same look as the demo page. A short internal pitch, not a fundraise:
   nine slides, one idea each, real numbers only:
   1. The problem: their prompt in one line, and who feels it.
   2. What we heard: the questions I asked and the answers that shaped it.
   3. The solution: what it does and how, in one picture or flow.
   4. Live demo: a button that opens the demo page on the guided scenes.
   5. Results: the headline numbers against the baseline, the weakness beside them.
   6. How we spent the day: the timeline, MVP time, feedback rounds, the
      change and its trade-off, thanks by name.
   7. Gaps: what it gets wrong today, and how we know.
   8. Roadmap, grounded in their system: Now (today's MVP), Next week (close
      the gaps, their real data through the loader, wire the API into their
      service), Next month (scale, monitoring, the features the team asked
      for); what each needs from them. Concrete, small, no fundraising talk.
   Vary the deck to the problem: titles in the problem's own words, not a
   fixed template; no line reused from another build.
   9. Evidence of how I work: three timestamped facts from the day (e.g.
      "test locked 3 minutes after the change"), then "Questions?".
7. Write WALKTHROUGH.md for presenting in this order: **(1) the pitch**, to
   leave a strong impression (5 minutes, slide by slide; slide 4 is a short
   live taste of the demo, then back); **(2) the team view**, the report
   walked top to bottom (mission and decisions, how the day went, the guided
   scenes, the gaps), for questions; **(3) the customer view**
   (`?view=customer`): the product alone, used the way a customer would, ending
   with someone in the room trying their own input. The pitch script in my voice (.claude/kit/VOICE.md), the case that I
   should be hired after a day in their office:
   - 0:00 Mission: their prompt in one line, and what I asked first and why.
   - 0:45 Solution: what we built, how, and the one decision that mattered most.
   - 1:30 How we spent the day: the timeline; MVP time, the feedback rounds
     and whose they were, the change we absorbed and its trade-off; thank
     people by name.
   - 2:30 The product, live: the three scenes (everyday, refused on purpose,
     hard case), then invite someone to try their own input.
   - 4:00 Honest gaps and the roadmap: what it gets wrong, what a week adds.
   - 4:40 Close: one sentence on how I like to work with a team, then stop and
     take questions.
   Add, for each of the three core functions, a two-sentence plain-English
   explanation I can say if asked about the code.
7a. Write `docs/ARCHITECTURE.md` with two Mermaid diagrams, drawn the LOOK.md way (top-down, 2-4 word boxes, 1-3 word arrows, every detail in the table under the diagram, rendered with the kit's `diagrams.js`): a **runtime
   view** (process boundaries, where state lives and whether it survives a
   restart, the failure path for each dependency, the PII boundary, the
   latency budget per hop) and a **component view** (components:
   loader, core logic, the one model module if any, store, API, demo page,
   and where their agent calls in; arrows labelled with the contract type),
   one paragraph per component, the data flow for one request, and what
   would change at 10x and 100x. Show the same diagram in the team view
   (rendered) and on the pitch's solution slide, and serve the doc itself
   rendered at `/architecture` (and `/integration`, `/qa`) with the diagrams
   drawn, so a reviewer can open it from the browser. Check `/openapi.json` and
   `/docs` load and match the code; link both from the team view. The spec
   documents API routes only (no HTML pages); every operation has request
   and response schemas, one example and a 4xx error schema; 400 responses
   say which field is wrong. `/docs` must work offline too (a rendered
   fallback when the CDN is unreachable). Lead the results with the
   end-to-end number against the trivial baselines, subsets second.
7b. Write `docs/INTEGRATION.md`, one screen: where it sits in their agent's
   turn (a small diagram: caller → agent → our tool or guard → reply), the
   tool definitions in `docs/tools.json`, one real request and response,
   latency (measured p50/p95), what happens on timeout or error, and how
   their real data plugs in through the loader. Add a test that plays a
   tiny agent loop: it reads `docs/tools.json`, calls the API the way an
   agent would, and checks the answer and the fail-closed path. Add an
   "Plug it into your agent" section to the team view and to the roadmap
   slide.
8. Write `docs/QA.md`: the ten questions the room is most likely to ask
   after the demo, each with a short answer in my voice. Cover:
   - **Why X, not Y**: each key decision in DECISIONS.md, the alternative
     we rejected and the reason (time, risk, the answer someone gave us).
   - **Why didn't you ask Z**: from TEAM.md, who we talked to, who we did
     not, why (time, scope, what we assumed instead), and what we would ask
     them now.
   - **What if we added feature xyz**: the top three cut-list or roadmap
     items, each with rough cost, what it would touch, and the trade-off;
     and the line "Want me to start it now? I can show you the impact in two
     minutes" (then `/step <their feature>` runs /change live).
   - **Why tech abc, not xyz**: every technology choice we made (language,
     standard-library server vs a framework, rules vs a model, file store vs
     a database, the test approach), the obvious alternative, and the
     reason in one line (their constraints, the day's time, fewer moving
     parts), plus when we would switch ("at real traffic, FastAPI and
     Postgres; here's where they plug in").
   - Where it breaks, how it scales, swapping in their real data, how we
     know it's right (tests, scorer, the hand-checked sample).
   Each answer: agree with what's fair, give the reason, say what I'd do next.
   Never defensive, never invented.
9. **Facts, not notes.** Regenerate every count, time and file reference on
   the page, the pitch and the docs from a fresh test run and from git right
   now, never from earlier notes. Any claim that names a test or file gives
   its path; any failing test is named by its title. A gap of more than 20
   minutes with no commit gets one plain sentence (what happened); no
   boilerplate apologies.
10. **Show the change and the miss live.** One guided scene (or a preset
   try-your-own input) exercises the mid-build requirement change, and its
   output names the change; if a trade-off was later reversed, the timeline
   says "cut at T, restored at T2". The case behind the page's main weakness
   runs live too, and its "why" matches the page's account of the miss.
   Reasons name the specific thing detected, not only a rule code.
11. **No residue.** Answers credited to the team must come from the team
   (PROMPT.md answers with who and when); our own defaults are labelled as
   ours. No line repeated across QA answers. The pitch's last slide is
   "Evidence of how I work": timestamped facts from the day, not adjectives.
**The gate.** Start the server, then run
`python .claude/scripts/check_demo.py --port <port>`. Demo prep is not done
until every check passes; fix what fails and run it again. Paste its output
in your reply.
Finally: run the suite three times (no flakes), check every number in
README and WALKTHROUGH against the measured output (same definitions as the
problem statement; the main weakness in the same sentence as the headline),
commit with "demo prep", and confirm `git status --porcelain` is empty.
$ARGUMENTS
