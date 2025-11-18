import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { Users, Shield, AlertTriangle, Check, X, RotateCcw, UserPlus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useToast } from '@/hooks/useToast'
import { CreateUserModal } from '@/components/CreateUserModal'

function AdminUsers() {
  const [user, setUser] = useState(null)
  const [users, setUsers] = useState([])
  const [servers, setServers] = useState([])
  const [selectedUser, setSelectedUser] = useState(null)
  const [selectedServer, setSelectedServer] = useState(null)
  const [userTools, setUserTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingTools, setLoadingTools] = useState(false)
  const [createUserModalOpen, setCreateUserModalOpen] = useState(false)
  const navigate = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    checkAuth()
  }, [])

  useEffect(() => {
    if (selectedUser && selectedServer) {
      fetchUserTools(selectedUser.email, selectedServer)
    }
  }, [selectedUser, selectedServer])

  const checkAuth = async () => {
    try {
      const response = await api.get('/api/auth/me')

      // Check if user is admin
      if (response.data.role !== 'admin') {
        navigate('/dashboard')
        return
      }

      setUser(response.data)
      await Promise.all([fetchUsers(), fetchServers()])
      setLoading(false)
    } catch (error) {
      console.error('Not authenticated:', error)
      setLoading(false)
      navigate('/login')
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/admin/users')
      setUsers(response.data.users)
    } catch (error) {
      console.error('Failed to fetch users:', error)
      toast.error('Failed to load users')
    }
  }

  const fetchServers = async () => {
    try {
      const response = await api.get('/api/admin/organization/tools')
      setServers(response.data.tools)

      // Auto-select first server if available
      if (response.data.tools.length > 0) {
        setSelectedServer(response.data.tools[0].id)
      }
    } catch (error) {
      console.error('Failed to fetch servers:', error)
      toast.error('Failed to load MCP servers')
    }
  }

  const fetchUserTools = async (userEmail, serverId) => {
    setLoadingTools(true)
    try {
      const response = await api.get(
        `/api/admin/users/${encodeURIComponent(userEmail)}/servers/${serverId}/tool-permissions`
      )
      setUserTools(response.data.tools)
    } catch (error) {
      console.error('Failed to fetch user tools:', error)

      // Check if this is an Enterprise Edition feature
      if (error.isEnterpriseFeature || error.status === 402) {
        toast.info(error.message || 'User-level tool permissions are only available in Enterprise Edition')
      } else {
        toast.error('Failed to load user tool permissions')
      }
      setUserTools([])
    } finally {
      setLoadingTools(false)
    }
  }

  const selectUser = (selectedUser) => {
    setSelectedUser(selectedUser)
  }

  const handleUserCreated = (newUser) => {
    // Refresh the users list
    fetchUsers()
    toast.success(`User ${newUser.email} created successfully`)
  }

  const toggleUserTool = async (toolId, currentEnabled) => {
    if (!selectedUser) return

    try {
      await api.put(
        `/api/admin/users/${encodeURIComponent(selectedUser.email)}/tools/${toolId}/toggle?enabled=${!currentEnabled}`,
        {}
      )

      // Update local state
      setUserTools(prevTools =>
        prevTools.map(tool =>
          tool.tool_id === toolId
            ? {
                ...tool,
                user_override: !currentEnabled,
                effective_access: tool.org_enabled ? !currentEnabled : false
              }
            : tool
        )
      )

      toast.success(`Tool ${!currentEnabled ? 'enabled' : 'disabled'} for user`)
    } catch (error) {
      console.error('Failed to toggle user tool:', error)

      // Check if this is an Enterprise Edition feature
      if (error.isEnterpriseFeature || error.status === 402) {
        toast.info(error.message || 'User-level tool permissions are only available in Enterprise Edition')
      } else {
        toast.error('Failed to update user tool permission')
      }
    }
  }

  const removeUserOverride = async (toolId) => {
    if (!selectedUser) return

    try {
      await api.delete(
        `/api/admin/users/${encodeURIComponent(selectedUser.email)}/tools/${toolId}/override`
      )

      // Update local state - revert to org default
      setUserTools(prevTools =>
        prevTools.map(tool =>
          tool.tool_id === toolId
            ? {
                ...tool,
                user_override: null,
                effective_access: tool.org_enabled
              }
            : tool
        )
      )

      toast.success('Override removed, reverted to organization default')
    } catch (error) {
      console.error('Failed to remove override:', error)

      // Check if this is an Enterprise Edition feature
      if (error.isEnterpriseFeature || error.status === 402) {
        toast.info(error.message || 'User-level tool permissions are only available in Enterprise Edition')
      } else {
        toast.error('Failed to remove override')
      }
    }
  }

  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout', {})
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      navigate('/login')
    }
  }

  // Group tools by category
  const groupToolsByCategory = (tools) => {
    const grouped = {}
    tools.forEach(tool => {
      const category = tool.category || 'Other'
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(tool)
    })
    return grouped
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} onLogout={handleLogout} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-purple-600" />
            <h1 className="text-xl font-semibold">User Management</h1>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant="secondary">{user?.role}</Badge>
            <span className="text-sm text-muted-foreground">{user?.name}</span>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4">
          <div className="grid gap-4 md:grid-cols-[300px_1fr]">
            {/* Users List */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Users</CardTitle>
                    <CardDescription>
                      Select a user to manage their tool access
                    </CardDescription>
                  </div>
                  <Button
                    onClick={() => setCreateUserModalOpen(true)}
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <UserPlus className="h-4 w-4" />
                    Create User
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {users.map((u) => (
                    <div
                      key={u.email}
                      className={`flex items-center justify-between rounded-lg border p-3 cursor-pointer transition-colors ${
                        selectedUser?.email === u.email
                          ? 'bg-accent border-primary'
                          : 'hover:bg-accent/50'
                      }`}
                      onClick={() => selectUser(u)}
                    >
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{u.name}</p>
                        <p className="text-sm text-muted-foreground truncate">{u.email}</p>
                      </div>
                      <Badge variant={u.role === 'admin' ? 'default' : 'secondary'}>
                        {u.role}
                      </Badge>
                    </div>
                  ))}

                  {users.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      No users found
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* User Tool Access */}
            <Card>
              <CardHeader>
                <CardTitle>
                  Tool Access
                  {selectedUser && `: ${selectedUser.name}`}
                </CardTitle>
                <CardDescription>
                  {selectedUser ? (
                    <div className="flex items-center gap-2 mt-2">
                      <span>Server:</span>
                      <Select value={selectedServer} onValueChange={setSelectedServer}>
                        <SelectTrigger className="w-[200px]">
                          <SelectValue placeholder="Select server" />
                        </SelectTrigger>
                        <SelectContent>
                          {servers.map((server) => (
                            <SelectItem key={server.id} value={server.id}>
                              {server.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  ) : (
                    'Select a user to manage their tool access'
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!selectedUser ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Select a user from the list to manage their tool access</p>
                  </div>
                ) : loadingTools ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                  </div>
                ) : userTools.length > 0 ? (
                  <div className="space-y-4">
                    {Object.entries(groupToolsByCategory(userTools)).map(
                      ([category, tools]) => (
                        <div key={category}>
                          <h4 className="font-medium text-sm text-muted-foreground mb-2 flex items-center gap-2">
                            {category}
                            <Badge variant="outline" className="text-xs">
                              {tools.filter(t => t.effective_access).length}/{tools.length}
                            </Badge>
                          </h4>
                          <div className="space-y-2">
                            {tools.map((tool) => (
                              <div
                                key={tool.tool_id}
                                className="rounded-lg border p-3"
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex items-start gap-3 flex-1">
                                    {tool.is_dangerous && (
                                      <AlertTriangle className="h-4 w-4 text-orange-500 mt-0.5" />
                                    )}
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2 mb-1">
                                        <span className="font-medium text-sm">
                                          {tool.display_name}
                                        </span>
                                        {tool.is_dangerous && (
                                          <Badge variant="destructive" className="text-xs">
                                            Dangerous
                                          </Badge>
                                        )}
                                      </div>
                                      {tool.description && (
                                        <p className="text-xs text-muted-foreground mb-2">
                                          {tool.description}
                                        </p>
                                      )}
                                      <div className="flex items-center gap-2 text-xs">
                                        <span className="text-muted-foreground">Org:</span>
                                        <Badge
                                          variant={tool.org_enabled ? "default" : "secondary"}
                                          className="text-xs"
                                        >
                                          {tool.org_enabled ? 'Enabled' : 'Disabled'}
                                        </Badge>
                                        {tool.user_override !== null && (
                                          <>
                                            <span className="text-muted-foreground ml-2">User:</span>
                                            <Badge variant="outline" className="text-xs">
                                              Override: {tool.user_override ? 'Enabled' : 'Disabled'}
                                            </Badge>
                                          </>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                  <div className="flex flex-col items-end gap-2">
                                    <div className="flex items-center gap-2">
                                      <Badge
                                        variant={tool.effective_access ? "default" : "secondary"}
                                        className="text-xs"
                                      >
                                        {tool.effective_access ? (
                                          <Check className="h-3 w-3" />
                                        ) : (
                                          <X className="h-3 w-3" />
                                        )}
                                      </Badge>
                                      <Switch
                                        checked={tool.user_override ?? tool.org_enabled}
                                        disabled={!tool.org_enabled || tool.readonly}
                                        onCheckedChange={() =>
                                          toggleUserTool(
                                            tool.tool_id,
                                            tool.user_override ?? tool.org_enabled
                                          )
                                        }
                                      />
                                    </div>
                                    {tool.user_override !== null && (
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => removeUserOverride(tool.tool_id)}
                                        className="h-7 text-xs"
                                      >
                                        <RotateCcw className="h-3 w-3 mr-1" />
                                        Reset
                                      </Button>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    No tools available for this server
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>

      {/* Create User Modal */}
      <CreateUserModal
        open={createUserModalOpen}
        onOpenChange={setCreateUserModalOpen}
        onUserCreated={handleUserCreated}
      />
    </SidebarProvider>
  )
}

export default AdminUsers
