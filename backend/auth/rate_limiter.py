"""
Rate limiting utilities for authentication endpoints.

Implements in-memory rate limiting to prevent brute force attacks.
"""
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter for authentication endpoints.

    Tracks login attempts per IP address and enforces rate limits.
    """

    def __init__(self, max_attempts: int = 5, window_minutes: int = 1):
        """
        Initialize rate limiter.

        Args:
            max_attempts: Maximum number of attempts allowed within the time window
            window_minutes: Time window in minutes for rate limiting
        """
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        # Store: {ip: [(timestamp1, timestamp2, ...)]}
        self.attempts: Dict[str, list] = defaultdict(list)

    def _clean_old_attempts(self, ip: str, now: datetime) -> None:
        """Remove attempts outside the time window."""
        cutoff = now - timedelta(minutes=self.window_minutes)
        self.attempts[ip] = [
            timestamp for timestamp in self.attempts[ip]
            if timestamp > cutoff
        ]

    def check_rate_limit(self, request: Request) -> None:
        """
        Check if request exceeds rate limit.

        Args:
            request: FastAPI request object

        Raises:
            HTTPException 429: If rate limit is exceeded
        """
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"

        now = datetime.now()

        # Clean old attempts
        self._clean_old_attempts(client_ip, now)

        # Check current attempt count
        attempt_count = len(self.attempts[client_ip])

        if attempt_count >= self.max_attempts:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: "
                f"{attempt_count} attempts in {self.window_minutes} minute(s)"
            )
            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Please try again in {self.window_minutes} minute(s)."
            )

        # Record this attempt
        self.attempts[client_ip].append(now)
        logger.debug(
            f"Login attempt recorded for IP {client_ip}: "
            f"{len(self.attempts[client_ip])}/{self.max_attempts}"
        )


# Global rate limiter instance
# 5 attempts per minute for login endpoints
login_rate_limiter = RateLimiter(max_attempts=5, window_minutes=1)
