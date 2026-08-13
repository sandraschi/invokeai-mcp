# Start the invokeai-mcp webapp frontend (Vite, port 11155)
$ErrorActionPreference = "Continue"
Set-Location "D:\Dev\repos\invokeai-mcp\webapp"
& "C:\Users\sandr\.bun\bin\bun.exe" run dev *> "C:\Users\sandr\AppData\Local\Temp\opencode\fe.log"
