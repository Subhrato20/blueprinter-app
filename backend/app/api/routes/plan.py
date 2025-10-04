"""Plan generation API endpoints."""

import os
from uuid import uuid4

import structlog
from fastapi import APIRouter, HTTPException

from app.models import PlanRequest, PlanResponse, ErrorResponse, PlanJSON
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

        # Create a mock plan for quick testing
        plan_json = {
            "title": f"Development Plan: {idea}",
            "steps": [
                {
                    "kind": "config",
                    "target": "package.json",
                    "summary": "Initialize project configuration and dependencies"
                },
                {
                    "kind": "code",
                    "target": "src/index.js",
                    "summary": "Implement core functionality"
                },
                {
                    "kind": "test",
                    "target": "tests/index.test.js",
                    "summary": "Add unit tests for core features"
                }
            ],
            "files": [
                {
                    "path": "package.json",
                    "content": "{\n  \"name\": \"my-app\",\n  \"version\": \"1.0.0\",\n  \"scripts\": {\n    \"start\": \"node src/index.js\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"express\": \"^4.18.0\"\n  },\n  \"devDependencies\": {\n    \"jest\": \"^29.0.0\"\n  }\n}"
                },
                {
                    "path": "src/index.js",
                    "content": "const express = require('express');\nconst app = express();\nconst PORT = process.env.PORT || 3000;\n\napp.get('/', (req, res) => {\n  res.json({ message: 'Hello, World!' });\n});\n\napp.listen(PORT, () => {\n  console.log(`Server running on port ${PORT}`);\n});"
                },
                {
                    "path": "tests/index.test.js",
                    "content": "const request = require('supertest');\nconst app = require('../src/index');\n\ndescribe('Basic functionality', () => {\n  test('should return hello world', async () => {\n    const response = await request(app).get('/');\n    expect(response.status).toBe(200);\n    expect(response.body.message).toBe('Hello, World!');\n  });\n});"
                }
            ],
            "risks": [
                "Technical complexity may require additional time",
                "Dependencies might have compatibility issues",
                "Testing coverage might be insufficient"
            ],
            "tests": [
                "Verify basic functionality works as expected",
                "Test error handling and edge cases",
                "Validate API endpoints return correct responses"
            ],
            "prBody": f"## Development Plan: {idea}\n\nThis PR implements the development plan for: {idea}\n\n### Changes\n- Project setup and configuration\n- Core feature implementation\n- Testing and validation\n\n### Files Added\n- `package.json` - Project configuration\n- `src/index.js` - Main application file\n- `tests/index.test.js` - Unit tests\n\n### Testing\nRun `npm test` to execute the test suite."
        }

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

        # Validate the plan structure explicitly to surface issues clearly
        validated_plan = PlanJSON(**plan_json)
        logger.info("Plan created successfully", plan_id=plan_id)
        return PlanResponse(plan=validated_plan, planId=plan_id)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Validation error in plan creation", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create plan", error=str(e))
        # Show detailed error in development for easier debugging
        debug = os.getenv("DEBUG", "false").lower() == "true"
        detail = f"Internal server error: {str(e)}" if debug else "Internal server error"
        raise HTTPException(status_code=500, detail=detail)


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
