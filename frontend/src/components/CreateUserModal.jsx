import { useState } from 'react'
import { Copy, Check, AlertCircle, UserPlus } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'

export function CreateUserModal({ open, onOpenChange, onUserCreated }) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState('user')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [createdUser, setCreatedUser] = useState(null)
  const [copied, setCopied] = useState(false)

  const resetForm = () => {
    setEmail('')
    setName('')
    setRole('user')
    setError(null)
    setCreatedUser(null)
    setCopied(false)
  }

  const handleClose = () => {
    resetForm()
    onOpenChange(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await fetch('/api/admin/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          name: name || null,
          role,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create user')
      }

      const data = await response.json()
      setCreatedUser(data)

      // Notify parent to refresh user list
      if (onUserCreated) {
        onUserCreated(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const copyPassword = async () => {
    if (createdUser?.temporary_password) {
      await navigator.clipboard.writeText(createdUser.temporary_password)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const copyAllDetails = async () => {
    if (createdUser) {
      const details = `New User Created:
Email: ${createdUser.email}
Name: ${createdUser.name || 'N/A'}
Role: ${createdUser.role}
Temporary Password: ${createdUser.temporary_password}
Password Expires: ${new Date(createdUser.password_expires_at).toLocaleString()}

Please change your password after first login.`

      await navigator.clipboard.writeText(details)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // If user is created, show success view
  if (createdUser) {
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Check className="h-5 w-5 text-green-600" />
              User Created Successfully
            </DialogTitle>
            <DialogDescription>
              The user account has been created. Please securely share these credentials with the user.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Email</Label>
              <Input value={createdUser.email} readOnly className="font-mono text-sm" />
            </div>

            <div className="space-y-2">
              <Label>Name</Label>
              <Input value={createdUser.name || 'N/A'} readOnly />
            </div>

            <div className="space-y-2">
              <Label>Role</Label>
              <Input value={createdUser.role} readOnly className="capitalize" />
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                Temporary Password
                <span className="text-xs text-muted-foreground font-normal">
                  (expires in 24 hours)
                </span>
              </Label>
              <div className="flex gap-2">
                <Input
                  value={createdUser.temporary_password}
                  readOnly
                  className="font-mono text-sm bg-yellow-50 dark:bg-yellow-950"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={copyPassword}
                  className="shrink-0"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-sm">
                {createdUser.message}
              </AlertDescription>
            </Alert>
          </div>

          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={copyAllDetails}
              className="flex items-center gap-2"
            >
              <Copy className="h-4 w-4" />
              Copy All Details
            </Button>
            <Button onClick={handleClose}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  // Otherwise show the form
  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="h-5 w-5" />
            Create New User
          </DialogTitle>
          <DialogDescription>
            Create a new user account with a temporary password. The user will be required to change
            their password on first login.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="email">
                Email Address <span className="text-red-500">*</span>
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="user@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Name (optional)</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
              />
              <p className="text-xs text-muted-foreground">
                If not provided, the email prefix will be used
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select value={role} onValueChange={setRole} disabled={loading}>
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create User'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
