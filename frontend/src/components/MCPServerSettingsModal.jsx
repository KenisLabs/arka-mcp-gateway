import { useState, useEffect } from 'react'
import api from '@/lib/api'
import { X, AlertCircle, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import { Separator } from '@/components/ui/separator'

/**
 * MCPServerSettingsModal - Modal for managing MCP server settings
 *
 * Features:
 * - Update OAuth credentials
 * - Manage tool permissions (enable/disable specific tools)
 */
function MCPServerSettingsModal({ server, onClose, onSuccess }) {
  const [credentials, setCredentials] = useState({})
  const [availableTools, setAvailableTools] = useState([])
  const [enabledTools, setEnabledTools] = useState(new Set())
  const [loading, setLoading] = useState(false)
  const [loadingTools, setLoadingTools] = useState(true)
  const [error, setError] = useState('')
  const [secretEditMode, setSecretEditMode] = useState(false)
  const [newSecret, setNewSecret] = useState('')

  useEffect(() => {
    fetchServerData()
  }, [server.server_id])

  const fetchServerData = async () => {
    try {
      setLoadingTools(true)

      // Fetch OAuth credentials
      const credResponse = await api.get(
        `/api/admin/mcp-servers/${server.server_id}/credentials`
      )
      setCredentials(credResponse.data)

      // Fetch available tools for this MCP server
      const toolsResponse = await api.get(
        `/api/admin/servers/${server.server_id}/tools`
      )

      setAvailableTools(toolsResponse.data.tools || [])

      // Set enabled tools
      const enabled = new Set(
        toolsResponse.data.tools
          ?.filter(tool => tool.is_enabled !== false)
          .map(tool => tool.name) || []
      )
      setEnabledTools(enabled)

      setLoadingTools(false)
    } catch (error) {
      console.error('Failed to fetch server data:', error)
      setError('Failed to load server settings')
      setLoadingTools(false)
    }
  }

  const handleCredentialChange = (fieldName, value) => {
    setCredentials(prev => ({
      ...prev,
      [fieldName]: value
    }))
  }

  const handleToolToggle = (toolName) => {
    setEnabledTools(prev => {
      const newSet = new Set(prev)
      if (newSet.has(toolName)) {
        newSet.delete(toolName)
      } else {
        newSet.add(toolName)
      }
      return newSet
    })
  }

  const handleSave = async () => {
    setError('')
    setLoading(true)

    try {
      // Build credentials payload
      const credentialsPayload = {
        client_id: credentials.client_id,
        redirect_uri: credentials.redirect_uri,
        scopes: credentials.scopes
      }

      // Only include client_secret if in edit mode and has value
      if (secretEditMode && newSecret.trim()) {
        credentialsPayload.client_secret = newSecret
      }

      // Update OAuth credentials
      await api.put(
        `/api/admin/mcp-servers/${server.server_id}`,
        { credentials: credentialsPayload }
      )

      // Update tool permissions
      const toolUpdates = availableTools.map(tool => ({
        tool_name: tool.name,
        is_enabled: enabledTools.has(tool.name)
      }))

      await api.post(
        `/api/admin/servers/${server.server_id}/tools/bulk-update`,
        { tools: toolUpdates }
      )

      // Reset secret edit mode
      setSecretEditMode(false)
      setNewSecret('')

      // Refresh credentials to get new hint
      await fetchServerData()

      setLoading(false)
      onSuccess()
    } catch (error) {
      console.error('Failed to update server settings:', error)

      let errorMessage = 'Failed to update server settings'
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }

      setError(errorMessage)
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 overflow-y-auto">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="sticky top-0 bg-background border-b z-10">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle>Server Settings: {server.display_name}</CardTitle>
              <CardDescription className="mt-2">
                Manage OAuth credentials and tool permissions
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="shrink-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-6 pt-6">
          {/* OAuth Credentials Section */}
          <div className="space-y-4">
            <div>
              <Label className="text-base font-semibold">OAuth Credentials</Label>
              <p className="text-sm text-muted-foreground mt-1">
                Update your OAuth application credentials
              </p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="client_id">Client ID</Label>
                <Input
                  id="client_id"
                  type="text"
                  value={credentials.client_id || ''}
                  onChange={(e) => handleCredentialChange('client_id', e.target.value)}
                  placeholder="Enter OAuth Client ID"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="client_secret">Client Secret</Label>
                {!secretEditMode ? (
                  // Read-only mode - show hint with Update button
                  <div className="flex gap-2">
                    <Input
                      id="client_secret"
                      type="text"
                      value={credentials.client_secret_hint || '••••'}
                      readOnly
                      disabled
                      className="flex-1 font-mono bg-muted"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setSecretEditMode(true)
                        setNewSecret('')
                      }}
                    >
                      Update
                    </Button>
                  </div>
                ) : (
                  // Edit mode - allow input with Cancel button
                  <div className="flex gap-2">
                    <Input
                      id="client_secret"
                      type="password"
                      value={newSecret}
                      onChange={(e) => setNewSecret(e.target.value)}
                      placeholder="Enter new client secret"
                      className="flex-1"
                      autoFocus
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => {
                        setSecretEditMode(false)
                        setNewSecret('')
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                )}
                {credentials.client_secret_configured && !secretEditMode && (
                  <p className="text-xs text-muted-foreground">
                    Last updated: {credentials.client_secret_updated_at
                      ? new Date(credentials.client_secret_updated_at).toLocaleDateString()
                      : 'Unknown'}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="redirect_uri">Redirect URI</Label>
                <Input
                  id="redirect_uri"
                  type="text"
                  value={credentials.redirect_uri || ''}
                  onChange={(e) => handleCredentialChange('redirect_uri', e.target.value)}
                  placeholder={`https://your-domain.com/servers/${server.server_id}/auth-callback`}
                />
                <p className="text-xs text-muted-foreground">
                  Format: https://your-domain.com/servers/{server.server_id}/auth-callback
                </p>
              </div>
            </div>
          </div>

          <Separator />

          {/* Tool Permissions Section */}
          <div className="space-y-4">
            <div>
              <Label className="text-base font-semibold">Tool Permissions</Label>
              <p className="text-sm text-muted-foreground mt-1">
                Select which tools are enabled for this MCP server
              </p>
            </div>

            {loadingTools ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-sm text-muted-foreground">Loading tools...</div>
              </div>
            ) : availableTools.length === 0 ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-sm text-muted-foreground">No tools available for this server</div>
              </div>
            ) : (
              <div className="space-y-3">
                {availableTools.map((tool) => (
                  <div
                    key={tool.name}
                    className="rounded-lg border p-4 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <Checkbox
                        id={tool.name}
                        checked={enabledTools.has(tool.name)}
                        onCheckedChange={() => handleToolToggle(tool.name)}
                      />
                      <Label
                        htmlFor={tool.name}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                      >
                        {tool.display_name || tool.name}
                      </Label>
                    </div>
                    {tool.description && (
                      <p className="text-sm text-muted-foreground mt-2 ml-7">
                        {tool.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default MCPServerSettingsModal
