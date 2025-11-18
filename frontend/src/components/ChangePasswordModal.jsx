import { useState, useEffect } from 'react'
import { Key, Check, AlertCircle, Eye, EyeOff } from 'lucide-react'
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
import { Alert, AlertDescription } from '@/components/ui/alert'
import api from '@/lib/api'
import { validatePasswordChange, PASSWORD_REQUIREMENTS } from '@/lib/password-validation'

export function ChangePasswordModal({ open, onOpenChange, onPasswordChanged }) {
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showOldPassword, setShowOldPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const resetForm = () => {
    setOldPassword('')
    setNewPassword('')
    setConfirmPassword('')
    setShowOldPassword(false)
    setShowNewPassword(false)
    setShowConfirmPassword(false)
    setError(null)
    setSuccess(false)
  }

  const handleClose = () => {
    resetForm()
    onOpenChange(false)
  }

  const validateForm = () => {
    const { isValid, error } = validatePasswordChange({
      oldPassword,
      newPassword,
      confirmPassword
    })

    if (!isValid) {
      setError(error)
    }

    return isValid
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      await api.post('/api/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      })

      setSuccess(true)

      // Notify parent
      if (onPasswordChanged) {
        onPasswordChanged()
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change password')
    } finally {
      setLoading(false)
    }
  }

  // Auto-close after 2 seconds on success
  useEffect(() => {
    if (success) {
      const timeoutId = setTimeout(() => {
        handleClose()
      }, 2000)

      // Cleanup timeout if component unmounts or success changes
      return () => clearTimeout(timeoutId)
    }
  }, [success])

  // If successful, show success view
  if (success) {
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Check className="h-5 w-5 text-green-600" />
              Password Changed Successfully
            </DialogTitle>
            <DialogDescription>
              Your password has been updated. You can now use your new password to log in.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Alert className="border-green-200 bg-green-50 dark:bg-green-950">
              <Check className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-sm text-green-800 dark:text-green-200">
                Password changed successfully. Closing...
              </AlertDescription>
            </Alert>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  // Otherwise show the form
  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Change Password
          </DialogTitle>
          <DialogDescription>
            Enter your current password and choose a new password. Your new password must be at
            least 8 characters long.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="old-password">
                Current Password <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <Input
                  id="old-password"
                  type={showOldPassword ? 'text' : 'password'}
                  placeholder="Enter current password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  required
                  disabled={loading}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                  onClick={() => setShowOldPassword(!showOldPassword)}
                  tabIndex={-1}
                >
                  {showOldPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">
                New Password <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <Input
                  id="new-password"
                  type={showNewPassword ? 'text' : 'password'}
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  disabled={loading}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  tabIndex={-1}
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Must be at least 8 characters long
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">
                Confirm New Password <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={loading}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  tabIndex={-1}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </div>
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
              {loading ? 'Changing Password...' : 'Change Password'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
