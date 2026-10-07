#!/usr/bin/env bash
# Copy the agent-starter template into the current directory.
# Never overwrites an existing file. Usage, in an empty or existing project:
#   curl -fsSL https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.sh | bash
set -euo pipefail

REPO="https://github.com/henryzhangpku/agent-starter/archive/refs/heads/main.tar.gz"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl -fsSL "$REPO" | tar -xz -C "$tmp"
src="$tmp/agent-starter-main/template"

copied=0; skipped=0
while IFS= read -r -d '' f; do
  rel="${f#"$src"/}"
  if [ -e "$rel" ]; then
    echo "skip (exists): $rel"; skipped=$((skipped + 1))
  else
    mkdir -p "$(dirname "$rel")"
    cp "$f" "$rel"
    echo "added: $rel"; copied=$((copied + 1))
  fi
done < <(find "$src" -type f -print0)

echo
echo "agent-starter: $copied files added, $skipped kept as they were."
echo "Next: fill in the project facts in CLAUDE.md and the paths in .claude/guard.json, then run: claude"
