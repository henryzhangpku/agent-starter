---
description: Integrate a finished wave - full test run, reviews, status update, one commit per task
---

Integrate the tasks that just finished.

1. Run `python -m pytest -q` on the whole repo. If anything fails, report
   which task's paths the failure is in and stop.
2. Run `git diff --stat` and confirm every changed path belongs to a task in
   this wave (TASKS.md `owns`). Report any path that doesn't.
3. Use the reviewer subagent on the combined change. If any task touched
   external calls, user data, money or decisions, also use the
   safety-reviewer subagent. Run them in parallel.
4. Show me: test result, blockers from each review, and suggestions.
5. After I approve: mark the tasks `done` in TASKS.md, append declined review
   suggestions to DECISIONS.md, and make one commit per task with the message
   `T<id>: <goal>` using `git add <that task's paths>`.
$ARGUMENTS
