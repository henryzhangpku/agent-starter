#!/usr/bin/env bash
# Open an isolated lane for one task: its own git worktree and branch, with the
# guard hook limited to the paths the task owns.
#   .claude/scripts/lane.sh T3 src/report/ src/report_cli.py
# Then: cd ../lane-T3 && claude   (paste the printed brief as the first message)
# Merge back from the main checkout:  git merge --no-ff lane/T3
# Remove when merged:                 git worktree remove ../lane-T3 && git branch -d lane/T3
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: .claude/scripts/lane.sh <task-id> <owned path> [<owned path> ...]" >&2
  exit 1
fi
task="$1"; shift
root="$(git rev-parse --show-toplevel)"
dir="$(dirname "$root")/lane-$task"

git -C "$root" worktree add "$dir" -b "lane/$task"

owns_json="$(printf '"%s",' "$@")"
printf '{"task": "%s", "owns": [%s]}\n' "$task" "${owns_json%,}" > "$dir/.claude/lane.json"
# lane.json is local to the lane; never commit or merge it
echo ".claude/lane.json" >> "$(git -C "$dir" rev-parse --git-path info/exclude)"

cat <<EOF
Lane $task ready at $dir (branch lane/$task), owning: $*

Paste this into the new session as the first message:
------------------------------------------------------------------
You are the implementer for task $task. Read TASKS.md (row $task),
CONTRACTS.md and CLAUDE.md. You may edit only: $* and tests/$task/
(the guard hook enforces this). Show me your plan first, then wait.
------------------------------------------------------------------
EOF
