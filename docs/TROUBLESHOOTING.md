# Troubleshooting

## Server doesn't appear in Claude Desktop
**Cause**: Config JSON is malformed, or uv path is wrong
**Fix**: Validate at jsonlint.com; check `command: "uv"` and the
`--directory` path in `claude_desktop_config.json`; restart Claude Desktop

## "command not found: uv"
**Cause**: uv not installed or not in PATH
**Fix**: `winget install astral-sh.uv` then restart the terminal

## invokeai_system health returns configured: false
**Cause**: InvokeAI is not running, or INVOKEAI_URL is wrong
**Fix**: Start InvokeAI via its launcher; verify `http://127.0.0.1:9090`
opens in a browser; check INVOKEAI_URL in config

## Generation fails with connection_error
**Cause**: InvokeAI process exited or is still starting (first launch takes minutes)
**Fix**: Open the launcher, confirm the engine started (web UI loads); retry

## "No main models installed"
**Cause**: The InvokeAI model folder is empty
**Fix**: InvokeAI UI, Models tab, install a model (SDXL or SD1.5 to start);
then `invokeai_models(operation="list", model_type="main")`

## Model not found / invalid key
**Cause**: model_key does not match any installed model
**Fix**: `invokeai_models(operation="list", model_type="main")` and copy the
exact `key`

## CUDA out of memory during generation
**Cause**: Model too large for VRAM, or another model still resident
**Fix**: Use SD1.5/SDXL instead of Flux; lower width/height; wait for the
queue to idle; restart InvokeAI to clear VRAM

## Queue stuck (nothing runs)
**Cause**: Processor paused after a failed job
**Fix**: `invokeai_queue(operation="resume")`

## Install job never completes
**Cause**: Large model download, slow network, or gated repo needing a token
**Fix**: Poll `invokeai_models(operation="installs")`; for gated models set
INVOKEAI_ACCESS_TOKEN or log into HuggingFace in the InvokeAI UI

## Webapp shows MOCK data forever
**Cause**: Backend cannot reach InvokeAI (onboarding not complete)
**Fix**: Complete docs/ONBOARDING.md; the MOCK badges clear automatically
when health succeeds

## Webapp loads but API calls fail (dev mode)
**Cause**: Vite proxy not running or backend not started
**Fix**: Start backend first (`uv run python -m invokeai_mcp.server --mode http --port 11154`);
check the Vite proxy targets 11154

## Frontend port already in use
**Cause**: A zombie Vite process
**Fix**: `Get-NetTCPConnection -LocalPort 11155 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`
