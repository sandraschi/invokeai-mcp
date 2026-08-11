# Development Setup

## Tools Required

Install all of these before continuing:

```bash
# Windows (winget)
winget install astral-sh.uv
winget install Git.Git
winget install OpenJS.NodeJS
winget install Oven-sh.Bun
winget install Casey.Just

# Verify
uv --version
git --version
node --version
bun --version
just --version
```

## Setup

```bash
git clone https://github.com/sandraschi/invokeai-mcp
cd invokeai-mcp
uv sync --extra dev
cd webapp && bun install && cd ..
```

## Common Tasks

```bash
just lint        # ruff + biome
just test        # pytest
just type-check  # pyright + tsc
just e2e         # playwright (webapp)
just ci          # full local gate (ruff + pytest + tsc + biome)
just mcpb-pack   # MCPB bundle (wipe+recopy src -> mcpb/src, 3-4-100 check)
just serve       # start.ps1 - full stack on 11154/11155
```

## Running the stack

```powershell
.\start.ps1                    # backend + webapp + browser
uv run python -m invokeai_mcp.server --mode http --port 11154   # backend only
cd webapp; bun run dev         # webapp only (proxies /api to 11154)
```

## Tests

- `tests/test_client.py` - client endpoints against mocked HTTP (respx)
- `tests/test_graphs.py` - graph structure invariants per model family
- `tests/test_tools.py` - tool behaviour with a fake InvokeAI client
- `webapp/e2e/` - Playwright smoke (health + frontend loads)

## Code Standards

Follow the fleet standards in `mcp-central-docs/standards/`:
- TOOL_DESIGN_STANDARDS (portmanteau, pagination, dialogic returns)
- WEBAPP_SOTA_STANDARDS (catch-them-all pages, data-testid, dark theme)
- JUNE_2026_STANDARDS_BAR (FastMCP 3.4.4+, MCPB only)

## Onboarding: required

This repo wraps InvokeAI (host app), so onboarding is mandatory:
[docs/ONBOARDING.md](docs/ONBOARDING.md). The webapp shows declared MOCK
sample data until the InvokeAI health probe succeeds.

## Declared doubles

- Webapp mock data (see `webapp/src/lib/mockOnboarding.ts` + ONBOARDING.md
  "Declared doubles") - badged MOCK, clears on connect.
- MCP tools have no mock paths - real API calls or explicit structured errors.
