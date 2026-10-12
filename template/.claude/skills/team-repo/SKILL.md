---
name: team-repo
description: Use when the build happens in the team's existing repository or alongside teammates - cloning their repo, matching their code style and tooling, branches and pull requests, someone else editing at the same time, or a teammate taking a piece of the work. Covers working in a shared codebase without surprises.
---

# Working in the team's repo, with the team

A collaborative build often means their code, their conventions and other
people typing at the same time. The goal: everything you add looks like it
belongs, and nobody is surprised.

## Before changing anything
- Read the README, the build and test commands, the linter and formatter
  config, and one or two files near where you will work. Run their tests
  once and note the baseline (what already fails is not ours).
- Write their conventions into CLAUDE.md project facts: language version,
  test command, formatter, folder layout, how they name things.
- Find the real interface you will plug into (the agent's tool call, the
  service boundary, the table) and read its code before designing.

## While building
- A branch for the day (`feat/<topic>`); small commits with plain messages;
  never rewrite shared history; never force-push a shared branch.
- Pull (rebase) before each wave; if a teammate changed a file you need,
  read their change first and build on it, never over it.
- Match their style: their test framework, their logging, their error
  types, their dependency manager. Ask before adding a dependency.
- Keep our kit files inside `.claude/` and `docs/`; their root stays theirs.

## Splitting work with a person
- Give them a contract, not a task: the function signature or endpoint,
  the data shape, and the test that proves it (in CONTRACTS.md).
- Agree who owns which files; integrate through the contract and the tests.
- Credit them by name in the check-in and the "how we spent the day" slide.

## At the end
Open a pull request (or a clear diff summary if there is no remote): what
it does, how to run it, the tests, the known gaps, who helped. Leave the
repo buildable with their own commands.
