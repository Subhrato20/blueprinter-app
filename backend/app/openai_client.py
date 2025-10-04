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
        raw = json.loads(content)

        # Normalize possible variants to the expected PlanJSON shape
        def _get(obj: Dict[str, Any], *candidates: str, default=None):
            for key in candidates:
                if key in obj and obj[key] is not None:
                    return obj[key]
            return default

        root = raw.get("plan") if isinstance(raw, dict) and isinstance(raw.get("plan"), dict) else raw
        if not isinstance(root, dict):
            raise ValueError("Plan payload is not a JSON object")

        title = _get(root, "title", "name", default=f"Development Plan: {idea}")
        steps = _get(root, "steps", default=[])
        files = _get(root, "files", default=[])
        risks = _get(root, "risks", default=[])
        tests = _get(root, "tests", default=[])
        pr_body = _get(root, "prBody", "pr_body", default=f"## Development Plan: {idea}")

        # Coerce lists
        if not isinstance(steps, list):
            steps = []
        if not isinstance(files, list):
            files = []
        if not isinstance(risks, list):
            risks = []
        if not isinstance(tests, list):
            tests = []

        # Minimal step coercion
        def _coerce_step(s: Any) -> Dict[str, Any]:
            if not isinstance(s, dict):
                return {"kind": "code", "target": "src/main", "summary": str(s)}
            kind = s.get("kind") or "code"
            target = s.get("target") or s.get("path") or "src/main"
            summary = s.get("summary") or s.get("description") or "Implement step"
            return {"kind": kind, "target": target, "summary": summary}

        steps = [_coerce_step(s) for s in steps]

        # Minimal file coercion
        def _coerce_file(f: Any) -> Dict[str, Any]:
            if not isinstance(f, dict):
                return {"path": "README.md", "content": str(f)}
            path = f.get("path") or f.get("file") or "README.md"
            content_val = f.get("content")
            if content_val is None:
                # some models wrap as {content: {language, code}}
                body = f.get("body") or f.get("code")
                content_val = body if isinstance(body, str) else json.dumps(body) if body is not None else ""
            return {"path": path, "content": content_val}

        files = [_coerce_file(f) for f in files]

        plan_data = {
            "title": title,
            "steps": steps,
            "files": files,
            "risks": risks,
            "tests": tests,
            "prBody": pr_body,
        }
        
        # Convert to our PlanJSON model
        return PlanJSON(
            title=plan_data["title"],
            steps=plan_data["steps"],
            files=plan_data["files"],
            risks=plan_data["risks"],
            tests=plan_data["tests"],
            prBody=plan_data["prBody"],
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
