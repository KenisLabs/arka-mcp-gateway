import axios from "axios";

// Create axios instance with default configuration
const api = axios.create({
  // No baseURL - let Vite proxy handle routing during development
  // In production, nginx will handle the routing
  withCredentials: true, // Always include cookies
  headers: {
    "Content-Type": "application/json",
  },
});

// Flag to prevent multiple refresh requests
let isRefreshing = false;
let refreshSubscribers = [];

// Function to add failed requests to queue
const subscribeTokenRefresh = (callback) => {
  refreshSubscribers.push(callback);
};

// Function to retry all queued requests after token refresh
const onRefreshed = () => {
  refreshSubscribers.forEach((callback) => callback());
  refreshSubscribers = [];
};

// Response interceptor to handle 401, 402 errors and token refresh
api.interceptors.response.use(
  (response) => {
    // If response is successful, just return it
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 402 Payment Required (Enterprise Edition features)
    if (error.response?.status === 402) {
      const errorMessage =
        error.response?.data?.detail ||
        "This is an Enterprise Edition feature. Contact support@kenislabs.com or visit kenislabs.com.com for more information.";

      // Create a custom error with enterprise feature information
      const enterpriseError = new Error(errorMessage);
      enterpriseError.isEnterpriseFeature = true;
      enterpriseError.status = 402;
      enterpriseError.originalError = error;

      // You can also show a toast/notification here if you have a toast system
      // For now, components will handle the error individually

      return Promise.reject(enterpriseError);
    }

    // Don't try to refresh on login, logout, or refresh endpoints
    const skipRefreshUrls = [
      "/api/auth/admin/login",
      "/api/auth/logout",
      "/api/auth/refresh",
    ];
    const shouldSkipRefresh = skipRefreshUrls.some((url) =>
      originalRequest.url?.includes(url)
    );

    // If error is 401 and we haven't tried to refresh yet
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !shouldSkipRefresh
    ) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve) => {
          subscribeTokenRefresh(() => {
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Try to refresh the token
        await axios.post(
          "/api/auth/refresh",
          {},
          {
            withCredentials: true,
          }
        );

        // Token refreshed successfully
        isRefreshing = false;
        onRefreshed();

        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - redirect to login
        isRefreshing = false;
        refreshSubscribers = [];

        // Clear any stored auth state
        console.error("Token refresh failed:", refreshError);

        // Redirect to login page
        window.location.href = "/login";

        return Promise.reject(refreshError);
      }
    }

    // For other errors, just reject
    return Promise.reject(error);
  }
);

export default api;
