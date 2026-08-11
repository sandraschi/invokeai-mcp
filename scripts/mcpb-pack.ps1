# invokeai-mcp MCPB pack - fresh-stage src -> mcpb/src, verify, then pack
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Pkg = "invokeai_mcp"
$Stage = Join-Path $Root "mcpb"

Write-Host "=== invokeai-mcp MCPB pack ===" -ForegroundColor Cyan

# 1. Fresh wipe+recopy src -> mcpb/src (preserve package dir, never flatten)
$stageSrc = Join-Path $Stage "src"
if (Test-Path $stageSrc) {
    Write-Host "-> wiping stale mcpb/src" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $stageSrc
}
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "src") | Out-Null
Write-Host "-> copying src\$Pkg -> mcpb\src\$Pkg" -ForegroundColor Yellow
Copy-Item -Recurse -Force (Join-Path $Root "src\$Pkg") (Join-Path $stageSrc $Pkg)

# 2. Copy metadata (manifest + assets) if missing
if (-not (Test-Path (Join-Path $Stage "manifest.json"))) {
    Copy-Item (Join-Path $Root "manifest.json") $Stage
}
if (-not (Test-Path (Join-Path $Stage "assets"))) {
    Copy-Item -Recurse (Join-Path $Root "assets") (Join-Path $Stage "assets")
}
if (-not (Test-Path (Join-Path $Stage "README.md"))) {
    Copy-Item (Join-Path $Root "README.md") $Stage
}
if (-not (Test-Path (Join-Path $Stage "CHANGELOG.md"))) {
    Copy-Item (Join-Path $Root "CHANGELOG.md") $Stage
}

# 3. Mechanical checks
Write-Host "-> checks" -ForegroundColor Yellow

# 3a. Entry point import resolves from mcpb/src only
$env:PYTHONPATH = $stageSrc
$probe = & $Root\.venv\Scripts\python.exe -c "import invokeai_mcp, sys; print(invokeai_mcp.__file__)" 2>&1
if ($LASTEXITCODE -ne 0 -or $probe -notlike "$stageSrc*") {
    throw "Entry point import failed from mcpb/src: $probe"
}
Write-Host "  entry import OK: $probe" -ForegroundColor Green

# 3b. No pycache/bak pollution
$junk = Get-ChildItem $Stage -Recurse -Include "__pycache__","*.pyc","*.bak","*.bak.*","*.orig","*.rej" -ErrorAction SilentlyContinue
if ($junk) { throw "Pollution under mcpb/: $($junk.FullName -join ', ')" }
Write-Host "  no pollution" -ForegroundColor Green

# 3c. 3-4-100 prompts verification
function Word-Count([string]$Path) {
    (@(Get-Content -Raw $Path) -split '\s+' | Where-Object { $_ }).Count
}
$sys = Word-Count (Join-Path $Root "assets\prompts\system.md")
$user = Word-Count (Join-Path $Root "assets\prompts\user.md")
$ex = (Get-Content (Join-Path $Root "assets\prompts\examples.json") -Raw | ConvertFrom-Json).Count
Write-Host "  prompts: system=$sys user=$user examples=$ex" -ForegroundColor Gray
if ($sys -lt 3000 -or $user -lt 4000 -or $ex -lt 100) {
    throw "3-4-100 FAIL: system=$sys user=$user examples=$ex (need 3000 / 4000 / 100)"
}
Write-Host "  3-4-100 OK" -ForegroundColor Green

# 4. Pack
Write-Host "-> mcpb pack" -ForegroundColor Yellow
Push-Location $Stage
bunx @anthropic-ai/mcpb pack . (Join-Path $Root "dist\invokeai-mcp-0.1.0.mcpb")
if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed" }
Pop-Location

# 5. Cleanup staging
Remove-Item -Recurse -Force $stageSrc
Write-Host "=== pack complete: dist\invokeai-mcp-0.1.0.mcpb ===" -ForegroundColor Green
