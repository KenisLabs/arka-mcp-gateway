import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Construction } from 'lucide-react'

function APIKeys() {
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
            <h1 className="text-3xl font-bold blur-sm select-none">API Keys</h1>
            <p className="text-muted-foreground mt-2 blur-sm select-none">
              Manage your API keys for accessing the gateway
            </p>
          </div>

          <Card className="blur-sm select-none pointer-events-none">
            <CardHeader>
              <CardTitle>Your API Keys</CardTitle>
              <CardDescription>
                API keys allow you to authenticate requests to the MCP Gateway
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-sm text-muted-foreground">
                  No API keys yet. Create one to get started.
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
                      API Keys feature is currently under development and will be available soon.
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

export default APIKeys
