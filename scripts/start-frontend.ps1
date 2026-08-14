# Start the invokeai-mcp webapp frontend (Vite, port 11155)
$ErrorActionPreference = "Continue"
Set-Location "D:\Dev\repos\invokeai-mcp\webapp"
Write-Host ""
Write-Host "  invokeai-mcp FRONTEND" -ForegroundColor Cyan
Write-Host "  webapp UI  ->  http://127.0.0.1:11155" -ForegroundColor Gray
Write-Host "  stop: Ctrl+C or close this window" -ForegroundColor DarkGray
Write-Host ""
$Host.UI.RawUI.WindowTitle = "invokeai-mcp FRONTEND :11155"
& "C:\Users\sandr\.bun\bin\bun.exe" run dev *> "C:\Users\sandr\AppData\Local\Temp\opencode\fe.log"
