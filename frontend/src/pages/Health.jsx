function Health() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center">
          <div className="flex size-12 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500">
            <span className="text-2xl font-bold text-white">A</span>
          </div>
        </div>
        <h1 className="text-4xl font-bold text-foreground">Arka MCP Gateway</h1>
        <div className="flex items-center justify-center gap-2">
          <div className="size-3 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-lg text-muted-foreground">Service is healthy</span>
        </div>
        <div className="mt-8 space-y-2 text-sm text-muted-foreground">
          <p>API Status: <span className="text-green-500 font-semibold">Online</span></p>
          <p>Version: 1.0.0</p>
        </div>
      </div>
    </div>
  )
}

export default Health
