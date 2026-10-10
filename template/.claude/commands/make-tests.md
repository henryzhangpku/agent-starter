---
description: Step 3 - write the failing acceptance tests from PLAN.md, then lock and commit them
---

From PLAN.md and the skeleton's entry point and contract, propose 5 to 8 behaviour-level acceptance tests (no implementation details, no near-duplicates) in plain English: end-to-end
behaviour the demo depends on (every input gets one output, outputs valid,
the rules from TEAM.md hold, bad input goes to a review list). One test must run the end-to-end command
and validate every output file against the exact shape the team gave; any
metric we report must be computed with the team's definition. List them and
wait for my go; I may cut or add.

After my go: write them into tests/test_acceptance.py, replacing the
placeholder (if that file is locked, use tests/test_acceptance_build.py).
Do not implement anything. Run `python -m pytest -q` and show they fail.
Then lock the file with `python .claude/scripts/lock_tests.py <file>`, commit with
"acceptance tests (failing)", and give me the minute-30 line to say:
"Here's the plan and the N tests that define done. Thinnest slice first;
I'll check in at <next check-in time>." $ARGUMENTS
