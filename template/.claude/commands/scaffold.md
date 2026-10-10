---
description: Step 3b - build the project skeleton from PROMPT.md and PLAN.md so every later step has a place to land
---

Read PROMPT.md, PLAN.md, TEAM.md and whatever the team handed us (data/,
any package already here). Propose the skeleton in one screen and wait for
my "go":

- **Language**: the one the team uses (from PROMPT.md answers or the code
  they handed us; if unknown, ask; default Python with pytest). If it is not
  Python, set `"test_command"` in `.claude/guard.json` (e.g. `npm test`,
  `go test ./...`) so the test hook runs their tests.
- **Package**: one package named for the product, with one module per
  plan part (load, the core logic, the one model module if a model is used,
  report/output), each with typed function signatures and docstrings that
  raise NotImplementedError. Reuse any schema the team handed us; do not
  redefine it.
- **Data boundary**: all reading of input goes through one `load` module
  that returns the contract types; today it reads the files in data/, and
  swapping to their real logs, JSON or a database means writing one new
  loader, nothing else. No other module opens a file or knows a record id.
- **Contract**: the data types passed between parts (frozen dataclasses or
  TypedDicts) in `<package>/schema.py`, and the same fields written into
  CONTRACTS.md.
- **Entry point**: `python -m <package> --data data --out out` that runs the
  whole pipeline and writes the output files in the agreed format; until the
  parts exist it may write an empty but valid output.
- **Facts**: fill the "Project facts" section of CLAUDE.md (data path and
  format, the model module, the contract, the run and test commands), and set
  `.claude/guard.json`: every input directory under `protected_prefixes`.

After my go: create it, run `python -m <package> --data data --out out` and
`python -m pytest -q` to show it imports and runs, and commit with
"skeleton". Do not implement logic. $ARGUMENTS
