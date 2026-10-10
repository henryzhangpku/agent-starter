You are one pass of a loop. You start fresh; everything you need is in files.

1. Read CLAUDE.md, PROMPT.md, CONTRACTS.md (if present), PLAN.md, TASKS.md (if
   present) and NOTES.md.
2. Pick exactly ONE item: the first unchecked `- [ ]` step in PLAN.md, or the
   first `todo` task in TASKS.md whose dependencies are done. If none remain,
   check that `python -m pytest -q` passes and stop.
3. Make that item's tests pass with the smallest change, editing only the files
   it needs. Never edit acceptance tests or protected data (the guard refuses).
   If the item needs a contract change or a decision, do not guess: write the
   question in NOTES.md under "Open questions", leave the item unchecked, and stop.
4. Run `python -m pytest -q`. Only if everything passes: tick the item in
   PLAN.md (or set the task to done in TASKS.md), add one line to NOTES.md
   (what changed, anything surprising), and commit with
   `git add <files> && git commit -m "<item>: <what>"`.
5. If tests fail and you cannot fix them within this pass, revert your partial
   change with no commit, record what you tried in NOTES.md, and stop.

One item per pass. No refactors outside the item. No new dependencies.
