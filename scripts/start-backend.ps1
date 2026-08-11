# Start invokeai-mcp backend on 11154
$ErrorActionPreference = "Continue"
Set-Location "D:\Dev\repos\invokeai-mcp"
& "C:\Users\sandr\.local\bin\uv.exe" run python -m invokeai_mcp.server --mode http --port 11154 *> "$env:TEMP\invokeai-backend.log"
