# Examples

Each example is a real build that uses the kit. For each: what the kit file
became in that project, so you can see the template filled in.

## 1. call-eval: post-call evaluation for voice agents

Repo: https://github.com/henryzhangpku/call-eval · Demo: https://henryzhangpku.github.io/call-eval/

| kit file | in call-eval |
|---|---|
| `CLAUDE.md` | [`CLAUDE.md`](https://github.com/henryzhangpku/call-eval/blob/main/CLAUDE.md): ten rules plus project facts (commands, data contract, where things live) |
| `.claude/hooks/guard.py` | blocks edits to generated data, the sealed holdout, the answer key, the holdout ledger and the acceptance tests |
| `.claude/hooks/run_tests.py` | runs the 56-test suite after every edit |
| `.claude/agents/reviewer.md` | checks scope, "model extracts, code scores", evidence spans, holdout discipline |
| `PLAN.md` | the build plan, steps ticked as completed |
| `DECISIONS.md` | no vector store; model extracts, code scores; separate evidence for satisfaction and sentiment; quality gate; sealed holdout; calibration method |
| one module calls a model | `calleval/extract/jev.py`, enforced by `tests/test_architecture.py` |

The kit was extracted from this project, so call-eval predates `RUNBOOK.md`
and team mode. Later examples are built from the kit forward.

## Next

Practice builds will be added here as they are done, each started with the
one-line bootstrap and run through `RUNBOOK.md` against the clock.
