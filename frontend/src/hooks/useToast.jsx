import { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((toast) => {
    const id = Math.random().toString(36).substr(2, 9)
    setToasts((prev) => [...prev, { ...toast, id }])

    // Auto-dismiss after duration
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, toast.duration || 5000)

    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // Main toast function that supports both formats:
  // toast({ title, description, variant }) or toast.success(message)
  const toast = useCallback((options) => {
    if (typeof options === 'object' && options !== null) {
      // Called as toast({ title, description, variant })
      const type = options.variant === 'destructive' ? 'error' : 'success'
      const message = options.description || options.message || options.title
      return addToast({ type, message, ...options })
    }
  }, [addToast])

  // Add convenience methods
  toast.success = useCallback((message, options = {}) =>
    addToast({ type: 'success', message, ...options }), [addToast])
  toast.error = useCallback((message, options = {}) =>
    addToast({ type: 'error', message, ...options }), [addToast])
  toast.info = useCallback((message, options = {}) =>
    addToast({ type: 'info', message, ...options }), [addToast])
  toast.warning = useCallback((message, options = {}) =>
    addToast({ type: 'warning', message, ...options }), [addToast])

  return (
    <ToastContext.Provider value={{ toast, toasts, removeToast }}>
      {children}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}
