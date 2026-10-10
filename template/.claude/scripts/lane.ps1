# Open an isolated lane for one task (Windows PowerShell). See lane.sh for details.
#   scripts\lane.ps1 T3 src/report/ src/report_cli.py
param([Parameter(Mandatory = $true)][string]$Task,
      [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)][string[]]$Owns)
$ErrorActionPreference = "Stop"

$root = (git rev-parse --show-toplevel).Trim()
$dir = Join-Path (Split-Path -Parent $root) "lane-$Task"
git -C $root worktree add $dir -b "lane/$Task"

$lane = @{ task = $Task; owns = $Owns } | ConvertTo-Json -Compress
Set-Content -Path (Join-Path $dir ".claude/lane.json") -Value $lane -Encoding utf8
$exclude = (git -C $dir rev-parse --git-path info/exclude).Trim()
Add-Content -Path $exclude -Value ".claude/lane.json"

Write-Host "Lane $Task ready at $dir (branch lane/$Task), owning: $($Owns -join ', ')"
Write-Host ""
Write-Host "Paste this into the new session as the first message:"
Write-Host "You are the implementer for task $Task. Read TASKS.md (row $Task), CONTRACTS.md and CLAUDE.md. You may edit only: $($Owns -join ', ') and tests/$Task/ (the guard hook enforces this). Show me your plan first, then wait."
