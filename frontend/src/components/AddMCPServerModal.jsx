import { useState } from 'react'
import api from '@/lib/api'
import { X, AlertCircle, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'

/**
 * AddMCPServerModal - Modal form for adding new MCP servers
 *
 * Displays server details, setup instructions, and credential input form
 */
function AddMCPServerModal({ server, onClose, onSuccess }) {
  const [credentials, setCredentials] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleInputChange = (fieldName, value) => {
    setCredentials(prev => ({
      ...prev,
      [fieldName]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validate required fields
      const missingFields = server.auth_fields
        .filter(field => field.required && !credentials[field.name])
        .map(field => field.label)

      if (missingFields.length > 0) {
        setError(`Please fill in: ${missingFields.join(', ')}`)
        setLoading(false)
        return
      }

      await api.post(
        '/api/admin/mcp-servers',
        {
          server_id: server.id,
          display_name: server.display_name,
          credentials: credentials
        }
      )

      onSuccess()
    } catch (error) {
      console.error('Failed to add server:', error)

      // Extract detailed error message from API response
      let errorMessage = 'Failed to add MCP server. Please check your credentials and try again.'

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
              <CardTitle className="flex items-center gap-2">
                Add {server.name}
                {server.popular && <Badge variant="secondary">Popular</Badge>}
              </CardTitle>
              <CardDescription className="mt-2">
                {server.description}
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
          {/* Server Information */}
          <div className="space-y-4">
            <div>
              <Label className="text-base font-semibold">About this server</Label>
              <div className="mt-2 space-y-2">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Badge variant="outline">{server.category}</Badge>
                  <span>•</span>
                  <span>v{server.version}</span>
                  <span>•</span>
                  <span>{server.publisher}</span>
                </div>
              </div>
            </div>

            <div>
              <Label className="text-sm font-medium">Capabilities</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {server.capabilities.map((capability, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs">
                    {capability}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Setup Instructions */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-base font-semibold">Setup Instructions</Label>
              <Button
                variant="link"
                size="sm"
                onClick={() => window.open(server.documentation_url, '_blank')}
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                View Documentation
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <pre className="text-xs whitespace-pre-wrap text-muted-foreground">
                {server.setup_instructions}
              </pre>
            </div>
          </div>

          {/* Credentials Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-base font-semibold">Configuration</Label>
              <p className="text-sm text-muted-foreground mt-1">
                Enter your {server.name} credentials to connect this MCP server
              </p>
            </div>

            {server.auth_fields.map((field) => (
              <div key={field.name} className="space-y-2">
                <Label htmlFor={field.name}>
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </Label>
                <Input
                  id={field.name}
                  type={field.type}
                  placeholder={field.placeholder}
                  value={credentials[field.name] || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  required={field.required}
                />
                {field.help_text && (
                  <p className="text-xs text-muted-foreground">{field.help_text}</p>
                )}
              </div>
            ))}

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
              <Button type="submit" disabled={loading}>
                {loading ? 'Adding Server...' : 'Add Server'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default AddMCPServerModal
