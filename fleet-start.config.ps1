@{
    Name         = 'invokeai-mcp'
    BackendPort  = 11154
    FrontendPort = 11155
    HealthPath   = '/api/health'
    WebRoot      = 'D:\Dev\repos\invokeai-mcp\webapp'

    Backend = @{
        Kind       = 'module-serve'
        Module     = 'invokeai_mcp.server'
        SyncExtras = @('dev')
    }

    Frontend = @{
        Kind           = 'vite-bun'
        PackageManager = 'bun'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
