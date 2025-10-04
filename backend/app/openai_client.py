"""OpenAI client for GPT-5 integration."""

import json
import os
from typing import Any, Dict, List

import structlog
from openai import OpenAI
from pydantic import BaseModel

from app.models import PatchResponse, PlanJSON

logger = structlog.get_logger(__name__)

# OpenAI client will be initialized lazily
client = None


def get_model() -> str:
    """Return the model to use, honoring env override at call time.

    Defaults to "gpt-5" per project preference. Avoids stale import-time values
    and removes the older placeholder default (gpt-5-reasoning).
    """
    model = os.getenv("GPT5_MODEL")
    return model if model else "gpt-5"


def get_openai_client():
    """Get or create OpenAI client."""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        client = OpenAI(api_key=api_key)
    return client


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
        model_name = get_model()
        logger.info("Calling OpenAI for plan", model=model_name)
        response = get_openai_client().chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content)}
            ],
        )

        # Extract plan JSON from content or tool call args
        msg = response.choices[0].message
        content = getattr(msg, "content", None)
        if not content:
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                try:
                    content = tool_calls[0].function.arguments
                    logger.info("Parsed plan from tool call arguments")
                except Exception:
                    content = None
        if not content:
            raise ValueError("Model returned empty response content for plan")
        plan_data = json.loads(content)
        
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
        model_name = get_model()
        logger.info("Calling OpenAI for patch", model=model_name)
        response = get_openai_client().chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(context)}
            ],
        )

        # Extract the patch data from the response (content or tool call args)
        msg = response.choices[0].message
        content = getattr(msg, "content", None)
        if not content:
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                try:
                    content = tool_calls[0].function.arguments
                    logger.info("Parsed patch from tool call arguments")
                except Exception:
                    content = None
        if not content:
            raise ValueError("Model returned empty response content for patch")
        patch_data = json.loads(content)
        
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
        
        model_name = get_model()
        logger.info("Calling OpenAI for intent", model=model_name)
        response = get_openai_client().chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this idea: {idea}"}
            ]
        )

        msg = response.choices[0].message
        content = getattr(msg, "content", None)
        if not content:
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                try:
                    content = tool_calls[0].function.arguments
                    logger.info("Parsed intent from tool call arguments")
                except Exception:
                    content = None
        if not content:
            raise ValueError("Model returned empty response content for intent")
        return json.loads(content)
        
    except Exception as e:
        logger.error("Failed to analyze intent", error=str(e))
        # Fallback to default values
        return {"feature": "general", "route": "/api"}
