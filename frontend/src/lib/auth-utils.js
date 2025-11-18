/**
 * Authentication utility functions
 *
 * Provides shared utilities for handling auth errors and redirects
 */

/**
 * Check if an error response indicates password change is required
 *
 * @param {Error} error - The error object from axios/api call
 * @returns {boolean} True if password change is required
 */
export function isPasswordChangeRequired(error) {
  if (error.response?.status === 403) {
    const detail = error.response?.data?.detail
    return detail === 'PASSWORD_CHANGE_REQUIRED' || detail === 'PASSWORD_EXPIRED'
  }
  return false
}

/**
 * Handle password change required error by redirecting to force-change-password page
 *
 * @param {Error} error - The error object from axios/api call
 * @param {Function} navigate - React Router navigate function
 * @returns {boolean} True if error was handled (redirect performed)
 */
export function handlePasswordChangeRequired(error, navigate) {
  if (isPasswordChangeRequired(error)) {
    navigate('/force-change-password', { replace: true })
    return true
  }
  return false
}
