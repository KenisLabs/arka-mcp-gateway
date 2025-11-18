import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Construction } from 'lucide-react'

function Usage() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="h-6" />
          <div className="flex items-center gap-2">
            <div className="flex size-6 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500">
              <span className="text-sm font-bold text-white">A</span>
            </div>
            <span className="font-semibold text-sm">Arka MCP Gateway</span>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0 backdrop-blur-sm">
          <div className="mt-4">
            <h1 className="text-3xl font-bold blur-sm select-none">Usage</h1>
            <p className="text-muted-foreground mt-2 blur-sm select-none">
              Monitor your API usage and metrics
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3 blur-sm select-none pointer-events-none">
            <Card>
              <CardHeader>
                <CardTitle>API Requests</CardTitle>
                <CardDescription>This month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-muted-foreground mt-2">
                  No requests yet
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Connections</CardTitle>
                <CardDescription>Current</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-muted-foreground mt-2">
                  No active connections
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Transfer</CardTitle>
                <CardDescription>This month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0 MB</div>
                <p className="text-xs text-muted-foreground mt-2">
                  No data transferred yet
                </p>
              </CardContent>
            </Card>
          </div>

          <Card className="blur-sm select-none pointer-events-none">
            <CardHeader>
              <CardTitle>Usage History</CardTitle>
              <CardDescription>
                View your historical usage data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-sm text-muted-foreground">
                  No usage data available yet
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Coming Soon Overlay */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <Card className="max-w-md pointer-events-auto shadow-2xl border-2">
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center gap-4">
                  <div className="rounded-full bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500 p-4">
                    <Construction className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold mb-2">Coming Soon</h2>
                    <p className="text-muted-foreground">
                      Usage Analytics feature is currently under development and will be available soon.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default Usage
