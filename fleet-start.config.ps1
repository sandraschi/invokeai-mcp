# Per-repo fleet start config for invokeai-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'invokeai-mcp'
    BackendPort  = 11154
    FrontendPort = 11155
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind    = 'custom'
        Command = "uv run --no-sync --project '$PSScriptRoot' invokeai-mcp --mode http --port 11154"
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'bun'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
