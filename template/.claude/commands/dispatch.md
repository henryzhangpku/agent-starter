---
description: Run one wave of TASKS.md in parallel with implementer and test-engineer subagents
---

Dispatch wave $ARGUMENTS from TASKS.md (if no wave is given, the lowest wave
with todo tasks).

1. Check first: every task in the wave has status todo, its dependencies are
   done, and no two tasks in the wave own the same path. If any check fails,
   stop and tell me.
2. Set those tasks to `in progress` in TASKS.md.
3. In a single message, launch one subagent per task, in parallel: the
   implementer for implementer tasks and the test-engineer for test tasks.
   Give each its task id and tell it to edit only that task's `owns` paths.
4. When all return, give me one line per task: done / blocked, tests, and any
   request to change a contract or a path outside its ownership.
5. Do not merge, refactor or fix anything yourself. Wait for /integrate.
