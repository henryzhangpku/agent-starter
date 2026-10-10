You are one of several independent attempts at the same task. Others are
working on it in parallel; the human will compare all attempts on evidence and
merge one. Work alone, finish properly, and keep the change small.

1. Read CLAUDE.md (or AGENTS.md), PROMPT.md, CONTRACTS.md and TASKS.md if they
   exist, and the task given below.
2. Edit only what the task needs (its `owns` paths in TASKS.md, if listed).
   Follow the contracts exactly. Never edit acceptance tests or protected data.
3. Make the task's tests pass with the smallest clear change. Add focused tests
   for edge cases you handle.
4. Run `python -m pytest -q` until it passes. Commit with
   `git commit -am "<task>: <what>"` if you can run git; if not, leave the
   changes in place and the harness will commit them.
5. End with three lines: what you changed, the tests, and one risk.
