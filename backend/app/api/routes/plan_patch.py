"""Plan patch API endpoints."""

import structlog
from fastapi import APIRouter, HTTPException

from app.models import PlanPatchRequest, ErrorResponse
from app.utils.json_patch import apply_patch, validate_patch_operations
from app.supabase_client import get_plan, update_plan, create_plan_revision

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/plan/patch")
async def apply_plan_patch(request: PlanPatchRequest):
    """Apply a JSON patch to a plan."""
    try:
        logger.info("Applying plan patch", plan_id=request.planId, operations_count=len(request.patch))
        
        # Validate patch operations
        if not validate_patch_operations(request.patch):
            raise HTTPException(status_code=400, detail="Invalid patch operations")
        
        # Get the current plan
        plan = await get_plan(request.planId)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Store the original plan for revision tracking
        original_plan_json = plan["plan_json"]
        
        # Apply the patch
        updated_plan_json = apply_patch(original_plan_json, request.patch)
        
        # Update the plan in the database
        success = await update_plan(request.planId, updated_plan_json)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update plan")
        
        # Create a revision record if messageId is provided
        if request.messageId:
            await create_plan_revision(
                plan_id=request.planId,
                message_id=request.messageId,
                patch=request.patch
            )
        
        logger.info("Plan patch applied successfully", plan_id=request.planId)
        
        return {
            "success": True,
            "planId": request.planId,
            "updatedPlan": updated_plan_json
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to apply plan patch", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
