"""Ask Copilot API endpoints."""

import structlog
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer

from app.models import AskRequest, PatchResponse, ErrorResponse
from app.openai_client import gpt5_patch
from app.supabase_client import get_plan, create_plan_message

logger = structlog.get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


async def get_current_user_id(token: str = Depends(security)) -> str:
    """Extract user ID from authentication token."""
    # This is a simplified implementation
    # In production, you would validate the JWT token and extract the user ID
    return "user_123"  # Replace with actual user ID extraction


@router.post("/ask", response_model=PatchResponse)
async def ask_copilot(
    request: AskRequest,
    user_id: str = Depends(get_current_user_id)
) -> PatchResponse:
    """Ask the copilot for suggestions about a specific part of the plan."""
    try:
        logger.info("Processing copilot request", plan_id=request.planId, node_path=request.nodePath)
        
        # Get the current plan
        plan = await get_plan(request.planId)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Create a message record
        message_id = await create_plan_message(
            plan_id=request.planId,
            user_question=request.userQuestion,
            node_path=request.nodePath,
            selection_text=request.selectionText
        )
        
        # Prepare context for GPT-5
        context = {
            "plan": plan["plan_json"],
            "nodePath": request.nodePath,
            "selectionText": request.selectionText,
            "userQuestion": request.userQuestion,
            "messageId": message_id
        }
        
        # Generate patch using GPT-5
        patch_response = await gpt5_patch(context)
        
        logger.info("Copilot response generated", message_id=message_id)
        
        return patch_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process copilot request", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
