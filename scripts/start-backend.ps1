# Start invokeai-mcp backend on 11154
$ErrorActionPreference = "Continue"
Set-Location "D:\Dev\repos\invokeai-mcp"
Write-Host ""
Write-Host "  invokeai-mcp BACKEND" -ForegroundColor Cyan
Write-Host "  REST /api + MCP /mcp  ->  http://127.0.0.1:11154" -ForegroundColor Gray
Write-Host "  API docs              ->  http://127.0.0.1:11154/docs" -ForegroundColor Gray
Write-Host "  stop: Ctrl+C or close this window" -ForegroundColor DarkGray
Write-Host ""
$Host.UI.RawUI.WindowTitle = "invokeai-mcp BACKEND :11154"
& "C:\Users\sandr\.local\bin\uv.exe" run python -m invokeai_mcp.server --mode http --port 11154 *> "$env:TEMP\invokeai-backend.log"
