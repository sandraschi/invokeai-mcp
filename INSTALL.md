# Installing invokeai-mcp

> **First time?** Complete [docs/ONBOARDING.md](docs/ONBOARDING.md) before
> expecting live generation calls - you need InvokeAI installed and at least
> one model downloaded.

## Prerequisites

Install these if you don't have them already:

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Desktop | Required host | [download](https://claude.ai/download) |
| InvokeAI | The wrapped engine (all options) | [launcher](https://github.com/invoke-ai/launcher/releases/latest) |
| Git | Clone repo (Option C/D only) | `winget install Git.Git` |
| Python + uv | Run server (Option C/D only) | `winget install astral-sh.uv` |
| Node.js + Bun | Webapp + mcpb CLI (Options B/D) | `winget install OpenJS.NodeJS` + `winget install Oven-sh.Bun` |

> Windows: all installs via [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)
> macOS: use `brew install` equivalents | Linux: use your distro package manager

## Option A - Drag and Drop (Recommended)

1. Go to [Releases](https://github.com/sandraschi/invokeai-mcp/releases/latest)
2. Download `invokeai-mcp-0.1.0.mcpb`
3. Open Claude Desktop, drag the file onto the window
   Or: Settings, MCP Servers, Install from file

## Option B - mcpb CLI

```bash
# Requires Node.js (see Prerequisites)
npx @anthropic-ai/mcpb install https://github.com/sandraschi/invokeai-mcp
```

## Option C - Manual Configuration

1. Clone: `git clone https://github.com/sandraschi/invokeai-mcp`
2. Install deps: `cd invokeai-mcp && uv sync`
3. Add to Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "invokeai": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\invokeai-mcp", "run", "invokeai-mcp"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

4. Restart Claude Desktop

## Option D - Developer Mode (webapp + live stack)

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Quick start:

```powershell
.\start.ps1        # backend on 11154, webapp on 11155, opens browser
```

## Verify Installation

After installing, open Claude Desktop and type:

> "Check the InvokeAI health"

You should see a response reporting whether InvokeAI is reachable and at what
URL. Then try:

> "Generate an image of a lighthouse at dusk"

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues
(server not appearing, InvokeAI not reachable, empty model list, VRAM errors).
