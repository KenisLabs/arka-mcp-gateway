import { useState } from 'react'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAuth } from '@/hooks/useAuth'
import { ChangePasswordModal } from '@/components/ChangePasswordModal'
import { Key, Shield } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/useToast'

function Profile() {
  const { user, loading, logout } = useAuth()
  const [changePasswordModalOpen, setChangePasswordModalOpen] = useState(false)
  const { toast } = useToast()

  const handlePasswordChanged = () => {
    toast.success('Password changed successfully')
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} onLogout={logout} />
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
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="mt-4">
            <h1 className="text-3xl font-bold">Profile</h1>
            <p className="text-muted-foreground mt-2">
              Manage your account settings and preferences
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Your account details and information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <Avatar className="h-20 w-20">
                    <AvatarFallback className="bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500 text-white text-2xl">
                      {user?.name?.charAt(0).toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" value={user?.name || ''} readOnly />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" value={user?.email || ''} readOnly />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <div className="flex items-center gap-2">
                    <Badge variant={user?.role === 'admin' ? 'default' : 'secondary'}>
                      {user?.role || 'user'}
                    </Badge>
                  </div>
                </div>
                {user?.provider && (
                  <div className="space-y-2">
                    <Label htmlFor="provider">Authentication Provider</Label>
                    <Input id="provider" value={user.provider} readOnly className="capitalize" />
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security
                </CardTitle>
                <CardDescription>
                  Manage your account security settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg border p-4 space-y-3">
                  <div className="flex items-start gap-3">
                    <Key className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">Password</p>
                      <p className="text-xs text-muted-foreground">
                        {user?.provider === 'admin'
                          ? 'Change your password to keep your account secure'
                          : 'You are logged in via OAuth. Password management is handled by your provider.'}
                      </p>
                    </div>
                  </div>
                  {user?.provider === 'admin' && (
                    <Button
                      className="w-full"
                      variant="outline"
                      onClick={() => setChangePasswordModalOpen(true)}
                    >
                      <Key className="h-4 w-4 mr-2" />
                      Change Password
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>

      {/* Change Password Modal */}
      <ChangePasswordModal
        open={changePasswordModalOpen}
        onOpenChange={setChangePasswordModalOpen}
        onPasswordChanged={handlePasswordChanged}
      />
    </SidebarProvider>
  )
}

export default Profile
