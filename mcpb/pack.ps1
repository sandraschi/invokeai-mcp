# Fleet-layout MCPB pack entry point (fleet.just mcpb-pack recipe).
# Delegates to the repo's pack implementation so behavior is unchanged.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
& (Join-Path $Root "scripts\mcpb-pack.ps1")
