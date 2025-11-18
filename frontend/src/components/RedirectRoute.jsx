import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { handlePasswordChangeRequired } from '@/lib/auth-utils'

/**
 * RedirectRoute - Redirects to /dashboard if authenticated, otherwise to /login
 * Used for catch-all routes and the root route
 */
function RedirectRoute() {
  const [checking, setChecking] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    checkAuthAndRedirect()
  }, [])

  const checkAuthAndRedirect = async () => {
    try {
      await api.get('/api/auth/me')
      // User is authenticated, redirect to dashboard
      navigate('/dashboard', { replace: true })
    } catch (error) {
      // Check if password change is required
      if (handlePasswordChangeRequired(error, navigate)) {
        return
      }

      // User is not authenticated, redirect to login
      navigate('/login', { replace: true })
    } finally {
      setChecking(false)
    }
  }

  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return null
}

export default RedirectRoute
