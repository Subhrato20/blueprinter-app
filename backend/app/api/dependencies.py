"""API dependencies for authentication and database access."""

from typing import Dict, Any
import structlog
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..supabase_client import get_supabase_client
from ..openai_client import get_openai_client

logger = structlog.get_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    request: Request,
    supabase=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get the current user - simplified for single user setup."""
    # For single user setup, we'll use a fixed user ID
    # In a real multi-user app, you'd get this from authentication
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID
        "email": "user@example.com",
        "user_metadata": {}
    }
