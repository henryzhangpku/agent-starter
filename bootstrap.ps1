# Copy the agent-starter template into the current directory.
# Never overwrites an existing file. Usage, in an empty or existing project:
#   irm https://raw.githubusercontent.com/henryzhangpku/agent-starter/main/bootstrap.ps1 | iex
$ErrorActionPreference = "Stop"

$zip = Join-Path $env:TEMP ("agent-starter-" + [guid]::NewGuid() + ".zip")
$dir = Join-Path $env:TEMP ("agent-starter-" + [guid]::NewGuid())
try {
    Invoke-WebRequest -UseBasicParsing "https://github.com/henryzhangpku/agent-starter/archive/refs/heads/main.zip" -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $dir
    $src = Join-Path $dir "agent-starter-main\template"
    $copied = 0; $skipped = 0
    Get-ChildItem -Path $src -Recurse -File -Force | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length + 1)
        if (Test-Path -LiteralPath $rel) {
            Write-Host "skip (exists): $rel"; $skipped++
        } else {
            $parent = Split-Path -Parent $rel
            if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
            Copy-Item -LiteralPath $_.FullName -Destination $rel
            Write-Host "added: $rel"; $copied++
        }
    }
    Write-Host ""
    Write-Host "agent-starter: $copied files added, $skipped kept as they were."
    Write-Host "Next: fill in the project facts in CLAUDE.md and the paths in .claude\guard.json, then run: claude"
} finally {
    Remove-Item -Force -ErrorAction SilentlyContinue $zip
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $dir
}
