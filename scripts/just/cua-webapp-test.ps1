# CUA webapp test runner - pre-Tauri browser walk (fleet standard)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root
uv run python scripts/cua-webapp-test.py
