/**
 * Password validation utilities
 *
 * Provides shared password validation logic for forms
 */

/**
 * Validate password change form inputs
 *
 * @param {Object} formData - The form data to validate
 * @param {string} formData.oldPassword - Current/old password
 * @param {string} formData.newPassword - New password
 * @param {string} formData.confirmPassword - Confirmation of new password
 * @returns {Object} { isValid: boolean, error: string|null }
 */
export function validatePasswordChange({ oldPassword, newPassword, confirmPassword }) {
  // Check all fields are filled
  if (!oldPassword || !newPassword || !confirmPassword) {
    return {
      isValid: false,
      error: 'All fields are required'
    }
  }

  // Check passwords match
  if (newPassword !== confirmPassword) {
    return {
      isValid: false,
      error: 'New passwords do not match'
    }
  }

  // Check password length
  if (newPassword.length < 8) {
    return {
      isValid: false,
      error: 'New password must be at least 8 characters long'
    }
  }

  // Check password is different from old password
  if (oldPassword === newPassword) {
    return {
      isValid: false,
      error: 'New password must be different from old password'
    }
  }

  return {
    isValid: true,
    error: null
  }
}

/**
 * Password strength requirements
 */
export const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  description: 'Must be at least 8 characters long'
}
