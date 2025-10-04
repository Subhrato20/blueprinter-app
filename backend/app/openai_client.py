"""OpenAI client for GPT-5 integration."""

import json
import os
from typing import Any, Dict, List

import structlog
from openai import OpenAI
from pydantic import BaseModel

from app.models import PatchResponse, PlanJSON

logger = structlog.get_logger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("GPT5_MODEL", "gpt-5-reasoning")


class PlanOut(BaseModel):
    """Output model for plan generation."""
    title: str
    steps: List[Dict[str, Any]]
    files: List[Dict[str, str]]
    risks: List[str]
    tests: List[str]
    prBody: str


class PatchOut(BaseModel):
    """Output model for patch generation."""
    rationale: str
    patch: List[Dict[str, Any]]  # RFC6902


async def gpt5_plan(
    idea: str, 
    route: str, 
    pattern: Dict[str, Any], 
    style: Dict[str, Any]
) -> PlanJSON:
    """Generate a development plan using GPT-5."""
    try:
        system_prompt = (
            "You are an expert software architect and developer. "
            "You produce deterministic, production-safe development plans. "
            "Return ONLY valid JSON matching the provided schema. "
            "Be specific about implementation details, consider edge cases, "
            "and provide comprehensive test scenarios."
        )
        
        user_content = {
            "idea": idea,
            "route": route,
            "patternTemplate": pattern.get("template", {}),
            "styleTokens": style
        }
        
        tool_schema = PlanOut.model_json_schema()
        
        # Note: This is a placeholder for the actual GPT-5 API call
        # The actual implementation will depend on the final GPT-5 API structure
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content)}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "generate_plan",
                    "description": "Generate a development plan",
                    "parameters": tool_schema
                }
            }]
        )
        
        # Extract the plan data from the response
        # This is a simplified version - actual implementation may vary
        plan_data = json.loads(response.choices[0].message.content)
        
        # Convert to our PlanJSON model
        return PlanJSON(
            title=plan_data["title"],
            steps=plan_data["steps"],
            files=plan_data["files"],
            risks=plan_data["risks"],
            tests=plan_data["tests"],
            prBody=plan_data["prBody"]
        )
        
    except Exception as e:
        logger.error("Failed to generate plan with GPT-5", error=str(e))
        raise


async def gpt5_patch(context: Dict[str, Any]) -> PatchResponse:
    """Generate a JSON patch using GPT-5."""
    try:
        system_prompt = (
            "You are an expert code reviewer and developer. "
            "You propose MINIMAL JSON Patch edits to the given nodePath only. "
            "Return JSON with 'rationale' and 'patch' fields. "
            "Maximum 10 operations, 10KB total. "
            "Focus on the specific area requested by the user."
        )
        
        # Note: This is a placeholder for the actual GPT-5 API call
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(context)}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "generate_patch",
                    "description": "Generate a JSON patch",
                    "parameters": PatchOut.model_json_schema()
                }
            }]
        )
        
        # Extract the patch data from the response
        patch_data = json.loads(response.choices[0].message.content)
        
        return PatchResponse(
            rationale=patch_data["rationale"],
            patch=patch_data["patch"]
        )
        
    except Exception as e:
        logger.error("Failed to generate patch with GPT-5", error=str(e))
        raise


async def analyze_intent(idea: str) -> Dict[str, str]:
    """Analyze user intent to extract feature and route information."""
    try:
        system_prompt = (
            "You are an expert at analyzing software development requests. "
            "Extract the main feature and target route from the user's idea. "
            "Return JSON with 'feature' and 'route' fields. "
            "Be specific about the route path (e.g., '/users', '/api/products')."
        )
        
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this idea: {idea}"}
            ]
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logger.error("Failed to analyze intent", error=str(e))
        # Fallback to default values
        return {"feature": "general", "route": "/api"}
