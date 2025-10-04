"""Cursor deep link API endpoints."""

import structlog
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer

from app.models import CursorLinkRequest, CursorLinkResponse, CursorPayload, ErrorResponse
from app.supabase_client import get_plan
from app.security import create_cursor_link

logger = structlog.get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


async def get_current_user_id(token: str = Depends(security)) -> str:
    """Extract user ID from authentication token."""
    # This is a simplified implementation
    # In production, you would validate the JWT token and extract the user ID
    return "user_123"  # Replace with actual user ID extraction


@router.post("/cursor-link", response_model=CursorLinkResponse)
async def create_cursor_deep_link(
    request: CursorLinkRequest,
    user_id: str = Depends(get_current_user_id)
) -> CursorLinkResponse:
    """Create a Cursor deep link for a plan."""
    try:
        logger.info("Creating cursor deep link", plan_id=request.planId)
        
        # Get the plan
        plan = await get_plan(request.planId)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        plan_json = plan["plan_json"]
        
        # Build the Cursor payload
        payload = CursorPayload(
            version=1,
            projectHint=plan.get("project_id"),
            plan={
                "title": plan_json["title"],
                "prBody": plan_json["prBody"]
            },
            files=[
                {
                    "path": file_data["path"],
                    "content": file_data["content"]
                }
                for file_data in plan_json["files"]
            ],
            postActions={
                "open": [
                    file_data["path"] 
                    for file_data in plan_json["files"][:3]  # Open first 3 files
                ],
                "runTask": "Blueprint: Tests"  # Optional task to run
            }
        )
        
        # Create the signed deep link
        link = create_cursor_link(payload.model_dump())
        
        logger.info("Cursor deep link created successfully", plan_id=request.planId)
        
        return CursorLinkResponse(link=link)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create cursor deep link", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
