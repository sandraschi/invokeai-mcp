set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

UV := "C:\\Users\\sandr\\.local\\bin\\uv.exe"
REPO := "D:\\Dev\\repos\\invokeai-mcp"

install:
    & "{{UV}}" sync --extra dev

bootstrap: install
    Set-Location "{{REPO}}"
    if (Test-Path "{{REPO}}\webapp\package.json") { Set-Location "{{REPO}}\webapp"; bun install }
    Write-Host "Bootstrap complete." -ForegroundColor Green

serve:
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File start.ps1

dev: serve

lint:
    & "{{UV}}" run ruff check src tests
    & "{{UV}}" run ruff format --check src tests
    Set-Location "{{REPO}}\webapp"; bun run biome:ci

fmt:
    & "{{UV}}" run ruff check src tests --fix
    & "{{UV}}" run ruff format src tests
    Set-Location "{{REPO}}\webapp"; bun run biome:write

type-check:
    & "{{UV}}" run pyright src/
    Set-Location "{{REPO}}\webapp"; bun run tsc:noEmit

test:
    & "{{UV}}" run python -m pytest -q tests/

e2e:
    Set-Location "{{REPO}}\webapp"; bun run test:e2e

screenshots:
    Set-Location "{{REPO}}\webapp"; bunx playwright test screenshots --reporter=line

ci:
    & "{{UV}}" run ruff check src tests
    & "{{UV}}" run ruff format --check src tests
    & "{{UV}}" run python -m pytest -q tests/
    Set-Location "{{REPO}}\webapp"; bun run check
    Set-Location "{{REPO}}\webapp"; bun run biome:ci

# Bundle MCP server for Claude Desktop (MCPB) - MUST wipe+recopy src -> mcpb/src first
mcpb-pack:
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/mcpb-pack.ps1

cua-webapp-test:
    Set-Location "{{REPO}}"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/cua-webapp-test.ps1
