"""Plan generation API endpoints."""

import structlog
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer

from app.models import PlanRequest, PlanResponse, ErrorResponse
from app.langgraph.graph import generate_plan
from app.supabase_client import create_plan, log_dev_event

logger = structlog.get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


async def get_current_user_id(token: str = Depends(security)) -> str:
    """Extract user ID from authentication token."""
    # This is a simplified implementation
    # In production, you would validate the JWT token and extract the user ID
    # For now, we'll use a placeholder
    return "user_123"  # Replace with actual user ID extraction


@router.post("/plan", response_model=PlanResponse)
async def create_development_plan(
    request: PlanRequest,
    user_id: str = Depends(get_current_user_id)
) -> PlanResponse:
    """Generate a development plan from a one-line idea."""
    try:
        logger.info("Creating development plan", idea=request.idea, project_id=request.projectId)
        
        # Generate the plan using LangGraph workflow
        plan_json = await generate_plan(
            idea=request.idea,
            project_id=request.projectId,
            user_id=user_id
        )
        
        # Store the plan in the database
        plan_id = await create_plan(
            project_id=request.projectId,
            user_id=user_id,
            plan_json=plan_json
        )
        
        # Log the development event
        await log_dev_event(
            event_type="plan_created",
            user_id=user_id,
            project_id=request.projectId,
            metadata={"plan_id": plan_id, "idea": request.idea}
        )
        
        logger.info("Plan created successfully", plan_id=plan_id)
        
        return PlanResponse(plan=plan_json, planId=plan_id)
        
    except ValueError as e:
        logger.error("Validation error in plan creation", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error("Failed to create plan", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/plan/{plan_id}")
async def get_plan(plan_id: str):
    """Get a specific plan by ID."""
    try:
        from app.supabase_client import get_plan
        
        plan = await get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get plan", plan_id=plan_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
