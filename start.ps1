param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$ReuseIfRunning
)
$ErrorActionPreference = "Stop"
$ReposRoot = "D:\Dev\repos"
$configPath = Join-Path $PSScriptRoot "fleet-start.config.ps1"
. "$ReposRoot\mcp-central-docs\scripts\Invoke-FleetWebappStart.ps1"
Start-FleetWebapp @PSBoundParameters -ConfigPath $configPath -LauncherRoot $PSScriptRoot
