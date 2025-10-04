"""API dependencies for authentication and database access."""

from typing import Dict, Any
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..supabase_client import get_supabase_client
from ..openai_client import get_openai_client

logger = structlog.get_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get the current authenticated user from JWT token."""
    try:
        # Verify the JWT token with Supabase
        response = supabase.auth.get_user(credentials.credentials)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "user_metadata": response.user.user_metadata or {}
        }
        
    except Exception as e:
        logger.error("Failed to authenticate user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
