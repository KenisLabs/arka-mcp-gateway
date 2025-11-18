import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { Users, Shield, Settings, Key, Plus, Edit, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/useToast'

function Admin() {
  const [user, setUser] = useState(null)
  const [tools, setTools] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState(null)
  const [userTools, setUserTools] = useState([])
  const [oauthProviders, setOauthProviders] = useState([])
  const [showOAuthForm, setShowOAuthForm] = useState(false)
  const [editingProvider, setEditingProvider] = useState(null)
  const [oauthForm, setOauthForm] = useState({
    mcp_server_id: '',
    provider_name: '',
    client_id: '',
    client_secret: '',
    redirect_uri: '',
    auth_url: '',
    token_url: '',
    scopes: '',
    additional_config: '{}'
  })
  const navigate = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await api.get('/api/auth/me')

      // Check if user is admin
      if (response.data.role !== 'admin') {
        navigate('/dashboard')
        return
      }

      setUser(response.data)
      await Promise.all([fetchOrganizationTools(), fetchUsers(), fetchOAuthProviders()])
      setLoading(false)
    } catch (error) {
      console.error('Not authenticated:', error)
      setLoading(false)
      navigate('/login')
    }
  }

  const fetchOrganizationTools = async () => {
    try {
      const response = await api.get('/api/admin/organization/tools')
      setTools(response.data.tools)
    } catch (error) {
      console.error('Failed to fetch organization tools:', error)
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/admin/users')
      setUsers(response.data.users)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    }
  }

  const fetchUserTools = async (userEmail) => {
    try {
      const response = await api.get(`/api/admin/users/${encodeURIComponent(userEmail)}/tools`)
      setUserTools(response.data.tools)
    } catch (error) {
      console.error('Failed to fetch user tools:', error)
    }
  }

  const toggleOrganizationTool = async (serverId, enabled) => {
    try {
      await api.put(
        `/api/admin/organization/tools/${serverId}/toggle?enabled=${enabled}`,
        {}
      )
      toast.success(`Tool ${enabled ? 'enabled' : 'disabled'} at organization level`)
      // Refresh the tools list
      await fetchOrganizationTools()
      // If a user is selected, refresh their tools too
      if (selectedUser) {
        await fetchUserTools(selectedUser.email)
      }
    } catch (error) {
      console.error('Failed to toggle organization tool:', error)
      toast.error('Failed to update organization tool access')
    }
  }

  const toggleUserTool = async (userEmail, serverId, enabled) => {
    try {
      await api.put(
        `/api/admin/users/${encodeURIComponent(userEmail)}/tools/${serverId}/toggle?enabled=${enabled}`,
        {}
      )
      toast.success(`Tool access ${enabled ? 'enabled' : 'disabled'} for user`)
      // Refresh user tools
      await fetchUserTools(userEmail)
    } catch (error) {
      console.error('Failed to toggle user tool:', error)
      toast.error('Failed to update user tool access')
    }
  }

  const selectUser = async (user) => {
    setSelectedUser(user)
    await fetchUserTools(user.email)
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

  // OAuth Provider Management Functions
  const fetchOAuthProviders = async () => {
    try {
      const response = await api.get('/api/admin/oauth-providers')
      setOauthProviders(response.data.providers)
    } catch (error) {
      console.error('Failed to fetch OAuth providers:', error)
    }
  }

  const handleOAuthFormChange = (field, value) => {
    setOauthForm(prev => ({ ...prev, [field]: value }))
  }

  const handleCreateOAuthProvider = async (e) => {
    e.preventDefault()
    try {
      // Parse scopes from comma-separated string to array
      const scopes = oauthForm.scopes.split(',').map(s => s.trim()).filter(s => s)

      // Parse additional_config JSON
      let additionalConfig = {}
      try {
        additionalConfig = JSON.parse(oauthForm.additional_config)
      } catch (err) {
        toast.error('Invalid JSON in additional config')
        return
      }

      await api.post('/api/admin/oauth-providers', {
        mcp_server_id: oauthForm.mcp_server_id,
        provider_name: oauthForm.provider_name,
        client_id: oauthForm.client_id,
        client_secret: oauthForm.client_secret,
        redirect_uri: oauthForm.redirect_uri,
        auth_url: oauthForm.auth_url,
        token_url: oauthForm.token_url,
        scopes,
        additional_config: additionalConfig
      })

      toast.success('OAuth provider created successfully')
      setShowOAuthForm(false)
      resetOAuthForm()
      await fetchOAuthProviders()
    } catch (error) {
      console.error('Failed to create OAuth provider:', error)
      toast.error(error.response?.data?.detail || 'Failed to create OAuth provider')
    }
  }

  const handleUpdateOAuthProvider = async (e) => {
    e.preventDefault()
    try {
      // Parse scopes from comma-separated string to array
      const scopes = oauthForm.scopes.split(',').map(s => s.trim()).filter(s => s)

      // Parse additional_config JSON
      let additionalConfig = {}
      try {
        additionalConfig = JSON.parse(oauthForm.additional_config)
      } catch (err) {
        toast.error('Invalid JSON in additional config')
        return
      }

      await api.put(`/api/admin/oauth-providers/${editingProvider}`, {
        provider_name: oauthForm.provider_name,
        client_id: oauthForm.client_id,
        client_secret: oauthForm.client_secret || undefined,
        redirect_uri: oauthForm.redirect_uri,
        auth_url: oauthForm.auth_url,
        token_url: oauthForm.token_url,
        scopes,
        additional_config: additionalConfig
      })

      toast.success('OAuth provider updated successfully')
      setShowOAuthForm(false)
      setEditingProvider(null)
      resetOAuthForm()
      await fetchOAuthProviders()
    } catch (error) {
      console.error('Failed to update OAuth provider:', error)
      toast.error(error.response?.data?.detail || 'Failed to update OAuth provider')
    }
  }

  const handleDeleteOAuthProvider = async (serverId) => {
    if (!confirm(`Are you sure you want to delete the OAuth provider for ${serverId}?`)) {
      return
    }

    try {
      await api.delete(`/api/admin/oauth-providers/${serverId}`)
      toast.success('OAuth provider deleted successfully')
      await fetchOAuthProviders()
    } catch (error) {
      console.error('Failed to delete OAuth provider:', error)
      toast.error(error.response?.data?.detail || 'Failed to delete OAuth provider')
    }
  }

  const startEditingProvider = async (provider) => {
    setEditingProvider(provider.mcp_server_id)
    setOauthForm({
      mcp_server_id: provider.mcp_server_id,
      provider_name: provider.provider_name,
      client_id: provider.client_id,
      client_secret: '', // Don't populate secret for security
      redirect_uri: provider.redirect_uri,
      auth_url: provider.auth_url,
      token_url: provider.token_url,
      scopes: Array.isArray(provider.scopes) ? provider.scopes.join(', ') : '',
      additional_config: JSON.stringify(provider.additional_config || {}, null, 2)
    })
    setShowOAuthForm(true)
  }

  const resetOAuthForm = () => {
    setOauthForm({
      mcp_server_id: '',
      provider_name: '',
      client_id: '',
      client_secret: '',
      redirect_uri: '',
      auth_url: '',
      token_url: '',
      scopes: '',
      additional_config: '{}'
    })
    setEditingProvider(null)
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
            <Shield className="h-5 w-5 text-purple-600" />
            <h1 className="text-xl font-semibold">Admin Dashboard</h1>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant="secondary">{user?.role}</Badge>
            <span className="text-sm text-muted-foreground">{user?.name}</span>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4">
          {/* Organization Tools Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                <CardTitle>Organization Tools</CardTitle>
              </div>
              <CardDescription>
                Manage which MCP servers are available to all users
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {tools.map((tool) => (
                  <div
                    key={tool.id}
                    className="flex items-center justify-between rounded-lg border p-4"
                  >
                    <div className="flex-1">
                      <h3 className="font-medium">{tool.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {tool.description}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={tool.enabled ? "default" : "secondary"}>
                        {tool.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                      <Switch
                        checked={tool.enabled}
                        onCheckedChange={(checked) =>
                          toggleOrganizationTool(tool.id, checked)
                        }
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* OAuth Provider Management Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Key className="h-5 w-5" />
                  <CardTitle>OAuth Provider Configuration</CardTitle>
                </div>
                <Button
                  onClick={() => {
                    resetOAuthForm()
                    setShowOAuthForm(true)
                  }}
                  size="sm"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add OAuth Provider
                </Button>
              </div>
              <CardDescription>
                Configure OAuth credentials for MCP servers that require authentication
              </CardDescription>
            </CardHeader>
            <CardContent>
              {showOAuthForm && (
                <form
                  onSubmit={editingProvider ? handleUpdateOAuthProvider : handleCreateOAuthProvider}
                  className="space-y-4 mb-6 p-4 border rounded-lg bg-muted/50"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="mcp_server_id">MCP Server ID</Label>
                      <Input
                        id="mcp_server_id"
                        value={oauthForm.mcp_server_id}
                        onChange={(e) => handleOAuthFormChange('mcp_server_id', e.target.value)}
                        disabled={editingProvider}
                        required
                        placeholder="e.g., github-mcp"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="provider_name">Provider Name</Label>
                      <Input
                        id="provider_name"
                        value={oauthForm.provider_name}
                        onChange={(e) => handleOAuthFormChange('provider_name', e.target.value)}
                        required
                        placeholder="e.g., github, google"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="client_id">Client ID</Label>
                      <Input
                        id="client_id"
                        value={oauthForm.client_id}
                        onChange={(e) => handleOAuthFormChange('client_id', e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="client_secret">
                        Client Secret {editingProvider && <span className="text-xs text-muted-foreground">(leave blank to keep existing)</span>}
                      </Label>
                      <Input
                        id="client_secret"
                        type="password"
                        value={oauthForm.client_secret}
                        onChange={(e) => handleOAuthFormChange('client_secret', e.target.value)}
                        required={!editingProvider}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="auth_url">Authorization URL</Label>
                      <Input
                        id="auth_url"
                        value={oauthForm.auth_url}
                        onChange={(e) => handleOAuthFormChange('auth_url', e.target.value)}
                        required
                        placeholder="https://..."
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="token_url">Token URL</Label>
                      <Input
                        id="token_url"
                        value={oauthForm.token_url}
                        onChange={(e) => handleOAuthFormChange('token_url', e.target.value)}
                        required
                        placeholder="https://..."
                      />
                    </div>
                    <div className="space-y-2 col-span-2">
                      <Label htmlFor="redirect_uri">Redirect URI</Label>
                      <Input
                        id="redirect_uri"
                        value={oauthForm.redirect_uri}
                        onChange={(e) => handleOAuthFormChange('redirect_uri', e.target.value)}
                        required
                        placeholder={`${import.meta.env.VITE_API_URL || window.location.origin}/servers/{server_id}/auth-callback`}
                      />
                    </div>
                    <div className="space-y-2 col-span-2">
                      <Label htmlFor="scopes">Scopes (comma-separated)</Label>
                      <Input
                        id="scopes"
                        value={oauthForm.scopes}
                        onChange={(e) => handleOAuthFormChange('scopes', e.target.value)}
                        placeholder="repo, user, read:org"
                      />
                    </div>
                    <div className="space-y-2 col-span-2">
                      <Label htmlFor="additional_config">Additional Config (JSON)</Label>
                      <textarea
                        id="additional_config"
                        className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                        value={oauthForm.additional_config}
                        onChange={(e) => handleOAuthFormChange('additional_config', e.target.value)}
                        placeholder='{"allow_signup": false}'
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit">
                      {editingProvider ? 'Update' : 'Create'} OAuth Provider
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowOAuthForm(false)
                        resetOAuthForm()
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              )}

              <div className="space-y-4">
                {oauthProviders.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No OAuth providers configured yet
                  </div>
                ) : (
                  oauthProviders.map((provider) => (
                    <div
                      key={provider.id}
                      className="flex items-center justify-between rounded-lg border p-4"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium">{provider.mcp_server_id}</h3>
                          <Badge variant="outline">{provider.provider_name}</Badge>
                        </div>
                        <div className="text-sm text-muted-foreground space-y-1">
                          <p>Client ID: {provider.client_id}</p>
                          <p>Redirect URI: {provider.redirect_uri}</p>
                          {provider.scopes && provider.scopes.length > 0 && (
                            <p>Scopes: {provider.scopes.join(', ')}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => startEditingProvider(provider)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteOAuthProvider(provider.mcp_server_id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Users Section */}
          <div className="grid gap-4 md:grid-cols-2">
            {/* Users List */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  <CardTitle>Users</CardTitle>
                </div>
                <CardDescription>
                  Select a user to manage their tool access
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {users.map((u) => (
                    <div
                      key={u.email}
                      className={`flex items-center justify-between rounded-lg border p-3 cursor-pointer transition-colors ${
                        selectedUser?.email === u.email
                          ? 'bg-accent'
                          : 'hover:bg-accent/50'
                      }`}
                      onClick={() => selectUser(u)}
                    >
                      <div>
                        <p className="font-medium">{u.name}</p>
                        <p className="text-sm text-muted-foreground">{u.email}</p>
                      </div>
                      <Badge variant={u.role === 'admin' ? 'default' : 'secondary'}>
                        {u.role}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* User Tool Access */}
            <Card>
              <CardHeader>
                <CardTitle>User Tool Access</CardTitle>
                <CardDescription>
                  {selectedUser
                    ? `Managing access for ${selectedUser.name}`
                    : 'Select a user to manage their tool access'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selectedUser ? (
                  <div className="space-y-4">
                    {userTools.map((tool) => (
                      <div
                        key={tool.id}
                        className="flex items-center justify-between rounded-lg border p-4"
                      >
                        <div className="flex-1">
                          <h3 className="font-medium">{tool.name}</h3>
                          <div className="mt-1 flex gap-2">
                            <Badge
                              variant={tool.org_enabled ? "default" : "secondary"}
                              className="text-xs"
                            >
                              Org: {tool.org_enabled ? "On" : "Off"}
                            </Badge>
                            {tool.user_override !== null && (
                              <Badge variant="outline" className="text-xs">
                                Override: {tool.user_override ? "On" : "Off"}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={tool.effective_access ? "default" : "secondary"}
                          >
                            {tool.effective_access ? "Accessible" : "Blocked"}
                          </Badge>
                          <Switch
                            checked={tool.user_override ?? true}
                            disabled={!tool.org_enabled}
                            onCheckedChange={(checked) =>
                              toggleUserTool(selectedUser.email, tool.id, checked)
                            }
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    Select a user from the list to manage their tool access
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default Admin
