import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { handlePasswordChangeRequired } from '@/lib/auth-utils'

/**
 * useAuth hook - Fetches and manages user authentication state
 * @returns {Object} { user, loading, logout }
 */
export function useAuth() {
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

  const logout = async () => {
    try {
      await api.post('/api/auth/logout', {})
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      navigate('/login')
    }
  }

  return { user, loading, logout }
}
