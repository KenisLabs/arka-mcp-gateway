import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { handlePasswordChangeRequired } from '@/lib/auth-utils'
import Dashboard from '../pages/Dashboard'
import AdminDashboard from '../pages/AdminDashboard'

/**
 * DashboardRouter - Routes users to the appropriate dashboard based on their role
 *
 * - Admin users → AdminDashboard (MCP server management)
 * - Regular users → Dashboard (user-facing MCP connection view)
 * - Unauthenticated → Redirect to login
 */
function DashboardRouter() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Not authenticated:', error)
      setLoading(false)

      // Check if password change is required
      if (handlePasswordChangeRequired(error, navigate)) {
        return
      }

      navigate('/login')
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    )
  }

  // Route based on user role
  if (user?.role === 'admin') {
    return <AdminDashboard />
  }

  return <Dashboard />
}

export default DashboardRouter
