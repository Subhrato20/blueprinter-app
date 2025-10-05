"""Middleware to automatically track API fetch requests."""

import time
import json
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.supabase_client import get_supabase_client

logger = structlog.get_logger(__name__)


class FetchTrackerMiddleware(BaseHTTPMiddleware):
    """Middleware to track all API fetch requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track the request and response."""
        # Skip tracking for certain endpoints
        skip_paths = ["/health", "/docs", "/openapi.json", "/fetch-history"]
        
        should_track = (
            request.url.path.startswith("/api/") and
            not any(skip in request.url.path for skip in skip_paths)
        )
        
        if not should_track:
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Get request data
        request_data = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_data = json.loads(body.decode())
                # Important: recreate the request with the body for downstream handlers
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            except Exception as e:
                logger.warning("Failed to parse request body", error=str(e))
        
        # Process request
        response = None
        error_message = None
        response_data = None
        
        try:
            response = await call_next(request)
            
            # Try to capture response data (this is tricky with streaming responses)
            # For now, we'll just track status codes
            
        except Exception as e:
            error_message = str(e)
            logger.error("Request failed", error=error_message)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log to database (non-blocking)
            try:
                await self._log_fetch(
                    endpoint=request.url.path,
                    method=request.method,
                    request_data=request_data,
                    response_data=response_data,
                    status_code=response.status_code if response else None,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )
            except Exception as e:
                # Don't fail the request if logging fails
                logger.warning("Failed to log fetch history", error=str(e))
        
        return response
    
    async def _log_fetch(
        self,
        endpoint: str,
        method: str,
        request_data: dict = None,
        response_data: dict = None,
        status_code: int = None,
        duration_ms: int = None,
        error_message: str = None,
    ):
        """Log fetch to database."""
        try:
            supabase = await get_supabase_client()
            
            data = {
                "endpoint": endpoint,
                "method": method,
                "request_data": request_data,
                "response_data": response_data,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "error_message": error_message,
            }
            
            supabase.table("fetch_history").insert(data).execute()
            
        except Exception as e:
            logger.warning("Failed to insert fetch history", error=str(e))
