# Pre-commit Biome hook for the webapp (fleet template)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$WebApp = Join-Path $Root "webapp"
if (-not (Test-Path (Join-Path $WebApp "package.json"))) { exit 0 }
Push-Location $WebApp
try {
    bun run biome:ci
    if ($LASTEXITCODE -ne 0) { exit 1 }
} finally {
    Pop-Location
}
exit 0
