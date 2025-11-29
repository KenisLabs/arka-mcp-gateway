"""
Enterprise route interception middleware.

This middleware intercepts requests to enterprise-only routes when running
in community edition and returns a 402 Payment Required response.

Enterprise routes are only registered when the enterprise submodule is present.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from edition import is_enterprise_edition
import logging

logger = logging.getLogger(__name__)


class EnterpriseRouteMiddleware(BaseHTTPMiddleware):
    """
    Middleware to intercept enterprise-only routes in community edition.

    When a request matches an enterprise route pattern and the system is
    running community edition, returns 402 Payment Required.
    """

    # Define enterprise-only route patterns
    # These routes should ONLY exist in the enterprise module
    ENTERPRISE_ROUTE_PATTERNS = [
        # Per-user tool permission routes
        "/admin/users/{user_email}/tools",
        "/admin/users/{user_email}/tools/{tool_id}/toggle",
        "/admin/users/{user_email}/tools/{tool_id}/override",
        "/admin/users/{user_email}/tools/bulk-toggle",
        "/admin/users/{user_email}/servers/{server_id}/tool-permissions",
        # Azure AD OAuth routes
        "/auth/azure",
    ]

    async def dispatch(self, request: Request, call_next):
        """
        Intercept requests and check if they match enterprise routes.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            402 response for enterprise routes in community edition,
            otherwise passes request to next handler
        """
        # If enterprise edition, let all requests through
        if is_enterprise_edition():
            return await call_next(request)

        # Check if request path matches any enterprise route pattern
        path = request.url.path

        # Check for exact matches or pattern matches
        if self._is_enterprise_route(path):
            logger.info(
                f"Blocked enterprise route '{path}' in community edition "
                f"(method: {request.method})"
            )
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Enterprise Feature Required",
                    "message": (
                        "This feature is only available in Enterprise Edition. "
                        "Contact support@kenislabs.com or visit kenislabs.com "
                        "for more information."
                    ),
                    "upgrade_url": "https://kenislabs.com/upgrade",
                    "feature": self._get_feature_name(path),
                },
            )

        # Not an enterprise route, continue normally
        return await call_next(request)

    def _is_enterprise_route(self, path: str) -> bool:
        """
        Check if a path matches any enterprise route pattern.

        Args:
            path: Request path

        Returns:
            True if path matches an enterprise route pattern
        """
        # Check for Azure AD routes
        if path.startswith("/auth/azure") or path.startswith("/api/auth/azure"):
            return True

        # Check for per-user tool permission routes
        # Pattern: /admin/users/{email}/tools... or /api/admin/users/{email}/tools...
        if "/admin/users/" in path:
            # Extract the part after /admin/users/
            parts = path.split("/admin/users/", 1)
            if len(parts) == 2 and parts[1]:
                # This is a user-specific route
                # Check if it contains /tools or /tool-permissions (per-user permissions)
                if "/tools" in parts[1] or "/tool-permissions" in parts[1]:
                    return True

        return False

    def _get_feature_name(self, path: str) -> str:
        """
        Get a human-readable feature name from the route path.

        Args:
            path: Request path

        Returns:
            Feature name string
        """
        if "/auth/azure" in path:
            return "Azure AD Authentication"
        elif "/admin/users/" in path and "/tools" in path:
            return "Per-User Tool Permissions"
        else:
            return "Enterprise Feature"
