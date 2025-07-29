#!/usr/bin/env python3
"""
Rate limiting middleware
Implements request rate limiting per user/IP
"""

import time
import json
from typing import Callable, Dict, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config import get_settings

settings = get_settings()

class InMemoryRateLimit:
    """Simple in-memory rate limiting implementation"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, window_seconds: int, max_requests: int) -> tuple[bool, dict]:
        """
        Check if request is allowed based on rate limit
        
        Args:
            key: Unique identifier for rate limiting (user_id or IP)
            window_seconds: Time window in seconds
            max_requests: Maximum requests allowed in window
            
        Returns:
            tuple: (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Initialize or get existing requests for this key
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if req_time > window_start
        ]
        
        # Check if under the limit
        current_requests = len(self.requests[key])
        is_allowed = current_requests < max_requests
        
        if is_allowed:
            self.requests[key].append(current_time)
        
        # Calculate reset time
        if self.requests[key]:
            reset_time = int(self.requests[key][0] + window_seconds)
        else:
            reset_time = int(current_time + window_seconds)
        
        rate_limit_info = {
            "limit": max_requests,
            "remaining": max(0, max_requests - current_requests - (1 if is_allowed else 0)),
            "reset": reset_time,
            "window": window_seconds
        }
        
        return is_allowed, rate_limit_info

# Global rate limiter instance
rate_limiter = InMemoryRateLimit()

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for request rate limiting"""
    
    def __init__(
        self, 
        app: ASGIApp,
        requests_per_minute: int = None,
        requests_per_hour: int = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS
        self.requests_per_hour = requests_per_hour or (settings.RATE_LIMIT_REQUESTS * 60)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply rate limiting to requests
        
        Args:
            request: HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response: HTTP response or rate limit error
        """
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            return await call_next(request)
        
        # Try to get user ID from request (if authenticated)
        rate_limit_key = await self._get_rate_limit_key(request)
        
        # Check per-minute rate limit
        allowed_minute, limit_info_minute = rate_limiter.is_allowed(
            f"{rate_limit_key}:minute", 
            60, 
            self.requests_per_minute
        )
        
        # Check per-hour rate limit
        allowed_hour, limit_info_hour = rate_limiter.is_allowed(
            f"{rate_limit_key}:hour", 
            3600, 
            self.requests_per_hour
        )
        
        # Use the most restrictive limit
        if not allowed_minute:
            return self._rate_limit_response(limit_info_minute, "minute")
        
        if not allowed_hour:
            return self._rate_limit_response(limit_info_hour, "hour")
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(limit_info_minute["remaining"])
        response.headers["X-RateLimit-Reset-Minute"] = str(limit_info_minute["reset"])
        
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(limit_info_hour["remaining"])
        response.headers["X-RateLimit-Reset-Hour"] = str(limit_info_hour["reset"])
        
        return response
    
    async def _get_rate_limit_key(self, request: Request) -> str:
        """
        Get unique key for rate limiting (user ID or IP address)
        
        Args:
            request: HTTP request
            
        Returns:
            str: Rate limit key
        """
        # Try to extract user ID from JWT token
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                import jwt
                token = auth_header.split(" ")[1]
                payload = jwt.decode(
                    token, 
                    settings.JWT_SECRET, 
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_id = payload.get("sub")
                if user_id:
                    return f"user:{user_id}"
            except:
                pass  # Fall back to IP-based rate limiting
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _rate_limit_response(self, limit_info: dict, limit_type: str) -> JSONResponse:
        """
        Create rate limit exceeded response
        
        Args:
            limit_info: Rate limit information
            limit_type: Type of limit ("minute" or "hour")
            
        Returns:
            JSONResponse: Rate limit error response
        """
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": f"Rate limit exceeded ({limit_type})",
                "limit": limit_info["limit"],
                "window": limit_info["window"],
                "reset": limit_info["reset"],
                "retry_after": limit_info["reset"] - int(time.time())
            },
            headers={
                "Retry-After": str(limit_info["reset"] - int(time.time())),
                f"X-RateLimit-Limit-{limit_type.title()}": str(limit_info["limit"]),
                f"X-RateLimit-Remaining-{limit_type.title()}": "0",
                f"X-RateLimit-Reset-{limit_type.title()}": str(limit_info["reset"]),
            }
        )