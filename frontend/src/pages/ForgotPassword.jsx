import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Key, ArrowLeft, Check, AlertCircle, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import api from '@/lib/api'

function ForgotPassword() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1 = request reset, 2 = reset with token
  const [email, setEmail] = useState('')
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const validatePasswordForm = () => {
    if (!token || !newPassword || !confirmPassword) {
      setError('All fields are required')
      return false
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return false
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long')
      return false
    }

    return true
  }

  const handleRequestReset = async (e) => {
    e.preventDefault()
    setError(null)

    if (!email) {
      setError('Email is required')
      return
    }

    setLoading(true)

    try {
      await api.post('/api/auth/forgot-password', { email })
      setStep(2)
    } catch (err) {
      // Note: Backend always returns success to prevent email enumeration
      // So we should always proceed to step 2
      setStep(2)
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e) => {
    e.preventDefault()
    setError(null)

    if (!validatePasswordForm()) {
      return
    }

    setLoading(true)

    try {
      await api.post('/api/auth/reset-password', {
        token,
        new_password: newPassword,
      })

      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password')
    } finally {
      setLoading(false)
    }
  }

  // Redirect to login after successful password reset
  useEffect(() => {
    if (success) {
      const timeoutId = setTimeout(() => {
        navigate('/login')
      }, 3000)

      // Cleanup timeout if component unmounts
      return () => clearTimeout(timeoutId)
    }
  }, [success, navigate])

  // Success view
  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
              <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <CardTitle className="text-2xl">Password Reset Successful</CardTitle>
            <CardDescription>
              Your password has been successfully reset. You can now log in with your new password.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert className="border-green-200 bg-green-50 dark:bg-green-950">
              <Check className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-sm text-green-800 dark:text-green-200">
                Redirecting to login page in 3 seconds...
              </AlertDescription>
            </Alert>
            <Button
              className="w-full mt-4"
              onClick={() => navigate('/login')}
            >
              Go to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => step === 2 ? setStep(1) : navigate('/login')}
              className="h-8 w-8"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <CardTitle className="text-2xl">
                {step === 1 ? 'Forgot Password' : 'Reset Password'}
              </CardTitle>
              <CardDescription>
                {step === 1
                  ? 'Enter your email to receive password reset instructions'
                  : 'Enter the reset token and your new password'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {step === 1 ? (
            <form onSubmit={handleRequestReset} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">
                  Email Address <span className="text-red-500">*</span>
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={loading}
                    className="pl-10"
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  If an account exists with this email, you will receive password reset
                  instructions.
                </p>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Sending...' : 'Send Reset Instructions'}
              </Button>

              <div className="text-center text-sm">
                <span className="text-muted-foreground">Remember your password? </span>
                <Button
                  variant="link"
                  className="p-0 h-auto font-normal"
                  onClick={() => navigate('/login')}
                >
                  Back to Login
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <Alert>
                <Mail className="h-4 w-4" />
                <AlertDescription className="text-sm">
                  Check your email for the password reset token. If you don't see it, check your
                  spam folder.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <Label htmlFor="token">
                  Reset Token <span className="text-red-500">*</span>
                </Label>
                <div className="relative">
                  <Key className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="token"
                    type="text"
                    placeholder="Enter reset token"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    required
                    disabled={loading}
                    className="pl-10 font-mono"
                  />
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

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Resetting Password...' : 'Reset Password'}
              </Button>

              <div className="text-center text-sm">
                <span className="text-muted-foreground">Didn't receive a token? </span>
                <Button
                  variant="link"
                  className="p-0 h-auto font-normal"
                  onClick={() => setStep(1)}
                >
                  Request another one
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ForgotPassword
