import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import ForgotPassword from './pages/ForgotPassword'
import ForceChangePassword from './pages/ForceChangePassword'
import DashboardRouter from './components/DashboardRouter'
import Documentation from './pages/Documentation'
import Profile from './pages/Profile'
import Billing from './pages/Billing'
import AdminUsers from './pages/AdminUsers'
import EnterprisePlaceholder from './pages/EnterprisePlaceholder'
import RedirectRoute from './components/RedirectRoute'
import { ToastProvider } from './hooks/useToast'
import { Toaster } from './components/Toaster'

// Simple root redirect component
function RootRedirect() {
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is likely authenticated by looking for auth cookies
    const hasAuthCookie = document.cookie.includes('access_token')
    navigate(hasAuthCookie ? '/dashboard' : '/login', { replace: true })
  }, [navigate])

  return null
}

function App() {
  return (
    <ToastProvider>
      <Router>
        <Routes>
          {/* Root path - simple redirect without auth check */}
          <Route path="/" element={<RootRedirect />} />

          {/* Implemented routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/force-change-password" element={<ForceChangePassword />} />
          <Route path="/dashboard" element={<DashboardRouter />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/documentation" element={<Documentation />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/admin/users" element={<AdminUsers />} />

          {/* Enterprise Features */}
          <Route path="/enterprise/:feature" element={<EnterprisePlaceholder />} />

          {/* Catch-all route - redirect to dashboard if logged in, otherwise login */}
          <Route path="*" element={<RedirectRoute />} />
        </Routes>
        <Toaster />
      </Router>
    </ToastProvider>
  )
}

export default App
