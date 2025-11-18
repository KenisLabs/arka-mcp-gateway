import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import {
  ChevronDown,
  ChevronUp,
  Plus,
  Settings,
  Trash2,
  Check,
  X,
  AlertTriangle,
  ExternalLink,
  Server
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/useToast'
import AddMCPServerModal from '@/components/AddMCPServerModal'
import MCPServerSettingsModal from '@/components/MCPServerSettingsModal'

/**
 * AdminDashboard - MCP Server Management Dashboard
 *
 * Features:
 * - View configured MCP servers
 * - Browse available MCP servers from catalog
 * - Add new MCP servers with credentials
 * - Manage server settings and permissions
 */
function AdminDashboard() {
  const [user, setUser] = useState(null)
  const [configuredServers, setConfiguredServers] = useState([])
  const [catalogServers, setCatalogServers] = useState([])
  const [expandedConfigured, setExpandedConfigured] = useState({})
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedCatalogServer, setSelectedCatalogServer] = useState(null)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [selectedConfiguredServer, setSelectedConfiguredServer] = useState(null)
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
      await Promise.all([
        fetchConfiguredServers(),
        fetchCatalogServers()
      ])
      setLoading(false)
    } catch (error) {
      console.error('Not authenticated:', error)
      setLoading(false)
      navigate('/login')
    }
  }

  const fetchConfiguredServers = async () => {
    try {
      const response = await api.get('/api/admin/mcp-servers/configured')
      setConfiguredServers(response.data)
    } catch (error) {
      console.error('Failed to fetch configured servers:', error)
      toast({
        title: 'Error',
        description: 'Failed to load configured MCP servers',
        variant: 'destructive'
      })
    }
  }

  const fetchCatalogServers = async () => {
    try {
      const response = await api.get('/api/admin/mcp-servers/catalog')
      setCatalogServers(response.data)
    } catch (error) {
      console.error('Failed to fetch catalog:', error)
      toast({
        title: 'Error',
        description: 'Failed to load MCP server catalog',
        variant: 'destructive'
      })
    }
  }

  const toggleServerEnabled = async (serverId, currentEnabled) => {
    try {
      await api.put(
        `/api/admin/mcp-servers/${serverId}`,
        { is_enabled: !currentEnabled }
      )

      // Update local state
      setConfiguredServers(prev =>
        prev.map(server =>
          server.server_id === serverId
            ? { ...server, is_enabled: !currentEnabled }
            : server
        )
      )

      toast({
        title: 'Success',
        description: `Server ${!currentEnabled ? 'enabled' : 'disabled'} successfully`
      })
    } catch (error) {
      console.error('Failed to toggle server:', error)
      toast({
        title: 'Error',
        description: 'Failed to update server status',
        variant: 'destructive'
      })
    }
  }

  const handleRemoveServer = async (serverId) => {
    if (!confirm('Are you sure you want to remove this MCP server? This will delete all associated credentials and permissions.')) {
      return
    }

    try {
      await api.delete(`/api/admin/mcp-servers/${serverId}`)

      setConfiguredServers(prev => prev.filter(s => s.server_id !== serverId))

      toast({
        title: 'Success',
        description: 'MCP server removed successfully'
      })
    } catch (error) {
      console.error('Failed to remove server:', error)
      toast({
        title: 'Error',
        description: 'Failed to remove server',
        variant: 'destructive'
      })
    }
  }

  const handleAddServer = (catalogServer) => {
    setSelectedCatalogServer(catalogServer)
    setShowAddModal(true)
  }

  const handleOpenSettings = (server) => {
    setSelectedConfiguredServer(server)
    setShowSettingsModal(true)
  }

  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout', {})
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  // Filter out already configured servers from catalog
  const availableServers = catalogServers.filter(
    catalogServer => !configuredServers.some(
      configured => configured.server_id === catalogServer.id
    )
  )

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} onLogout={handleLogout} />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex flex-1 items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold">MCP Server Management</h1>
              <p className="text-sm text-muted-foreground">
                Configure and manage Model Context Protocol servers
              </p>
            </div>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-4 p-4">
          {/* Configured Servers Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Configured MCP Servers
                <Badge variant="secondary">{configuredServers.length}</Badge>
              </CardTitle>
              <CardDescription>
                MCP servers that have been added and configured for your organization
              </CardDescription>
            </CardHeader>
            <CardContent>
              {configuredServers.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Server className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">No MCP servers configured</h3>
                  <p className="text-sm text-muted-foreground mb-4 max-w-md">
                    Add MCP servers from the available catalog below to start using them in your organization
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {configuredServers.map((server) => (
                    <Card key={server.id} className="border-2">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                              <Server className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <CardTitle className="text-base">{server.display_name}</CardTitle>
                              <CardDescription className="text-sm">
                                {server.category}
                              </CardDescription>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {server.has_credentials && (
                              <Badge variant="outline" className="gap-1">
                                <Check className="h-3 w-3" />
                                Credentials
                              </Badge>
                            )}
                            <Badge variant={server.is_enabled ? 'default' : 'secondary'}>
                              {server.is_enabled ? 'Enabled' : 'Disabled'}
                            </Badge>
                            <Switch
                              checked={server.is_enabled}
                              onCheckedChange={() => toggleServerEnabled(server.server_id, server.is_enabled)}
                            />
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setExpandedConfigured(prev => ({
                                ...prev,
                                [server.id]: !prev[server.id]
                              }))}
                            >
                              {expandedConfigured[server.id] ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </div>
                      </CardHeader>

                      {expandedConfigured[server.id] && (
                        <CardContent className="border-t pt-4">
                          <div className="space-y-4">
                            <div>
                              <Label className="text-sm font-medium">Description</Label>
                              <p className="text-sm text-muted-foreground mt-1">
                                {server.description || 'No description available'}
                              </p>
                            </div>

                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleOpenSettings(server)}
                              >
                                <Settings className="h-4 w-4 mr-2" />
                                Settings
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => handleRemoveServer(server.server_id)}
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Remove
                              </Button>
                            </div>

                            <div className="text-xs text-muted-foreground">
                              Added by {server.added_by} • {new Date(server.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </CardContent>
                      )}
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Available Servers Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Available MCP Servers
                <Badge variant="secondary">{availableServers.length}</Badge>
              </CardTitle>
              <CardDescription>
                Browse and add MCP servers from the catalog
              </CardDescription>
            </CardHeader>
            <CardContent>
              {availableServers.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Check className="h-12 w-12 text-green-500 mb-4" />
                  <h3 className="text-lg font-medium mb-2">All servers configured</h3>
                  <p className="text-sm text-muted-foreground">
                    You've added all available MCP servers from the catalog
                  </p>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {availableServers.map((server) => (
                    <Card key={server.id} className="border-2 hover:border-primary/50 transition-colors">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                              <Server className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <CardTitle className="text-base">{server.name}</CardTitle>
                              <CardDescription className="text-xs">{server.category}</CardDescription>
                            </div>
                          </div>
                          {server.popular && (
                            <Badge variant="secondary" className="text-xs">Popular</Badge>
                          )}
                        </div>
                        <CardDescription className="text-sm mt-2 line-clamp-2">
                          {server.description}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="flex-1"
                            onClick={() => handleAddServer(server)}
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Add Server
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => window.open(server.documentation_url, '_blank')}
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Badge variant="outline" className="text-xs">
                            {server.auth_type}
                          </Badge>
                          <span>v{server.version}</span>
                          <span>•</span>
                          <span>{server.publisher}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </SidebarInset>

      {/* Add MCP Server Modal */}
      {showAddModal && selectedCatalogServer && (
        <AddMCPServerModal
          server={selectedCatalogServer}
          onClose={() => {
            setShowAddModal(false)
            setSelectedCatalogServer(null)
          }}
          onSuccess={async () => {
            setShowAddModal(false)
            setSelectedCatalogServer(null)
            await fetchConfiguredServers()
            toast({
              title: 'Success',
              description: `${selectedCatalogServer.name} has been added successfully`
            })
          }}
        />
      )}

      {/* MCP Server Settings Modal */}
      {showSettingsModal && selectedConfiguredServer && (
        <MCPServerSettingsModal
          server={selectedConfiguredServer}
          onClose={() => {
            setShowSettingsModal(false)
            setSelectedConfiguredServer(null)
          }}
          onSuccess={async () => {
            setShowSettingsModal(false)
            setSelectedConfiguredServer(null)
            await fetchConfiguredServers()
            toast({
              title: 'Success',
              description: `${selectedConfiguredServer.display_name} settings updated successfully`
            })
          }}
        />
      )}
    </SidebarProvider>
  )
}

export default AdminDashboard
