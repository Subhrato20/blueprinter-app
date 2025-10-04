"""Plan generation API endpoints."""

import os
from uuid import uuid4

import structlog
from fastapi import APIRouter, HTTPException

from app.models import PlanRequest, PlanResponse, ErrorResponse
from app.langgraph.graph import generate_plan
from app.supabase_client import create_plan, log_dev_event

logger = structlog.get_logger(__name__)
router = APIRouter()

DEFAULT_USER_ID = os.getenv("DEFAULT_PLAN_USER_ID", "demo-user")


def _supabase_configured() -> bool:
    """Determine whether Supabase credentials look usable."""
    url = os.getenv("SUPABASE_URL", "")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not service_key:
        return False
    # Setup scripts ship placeholders containing "..." – treat them as not configured.
    return "..." not in service_key


@router.get("/plan/test")
async def test_plan_endpoint():
    """Test endpoint to verify the plan route is working."""
    return {"message": "Plan endpoint is working", "status": "ok"}

@router.post("/plan", response_model=PlanResponse)
async def create_development_plan(request: PlanRequest) -> PlanResponse:
    """Generate a development plan from a one-line idea."""
    try:
        logger.info("Creating development plan", idea=request.idea, project_id=request.projectId)

        idea = request.idea.strip()
        if not idea:
            raise HTTPException(status_code=400, detail="Idea must not be empty")

        user_id = DEFAULT_USER_ID

        plan_json = await generate_plan(idea=idea, project_id=request.projectId, user_id=user_id)

        plan_id = str(uuid4())

        if _supabase_configured():
            try:
                plan_id = await create_plan(
                    project_id=request.projectId,
                    user_id=user_id,
                    plan_json=plan_json,
                )
                await log_dev_event(
                    event_type="plan_created",
                    user_id=user_id,
                    project_id=request.projectId,
                    metadata={"idea": idea},
                )
            except Exception as supabase_error:
                logger.warning(
                    "Failed to persist plan to Supabase; returning in-memory plan",
                    error=str(supabase_error),
                )

        logger.info("Plan created successfully", plan_id=plan_id)
        return PlanResponse(plan=plan_json, planId=plan_id)

    except HTTPException:
        raise
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
