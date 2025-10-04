"""Supabase client for database operations."""

import os
from typing import Any, Dict, List, Optional

import structlog
from supabase import Client, create_client

logger = structlog.get_logger(__name__)

_supabase_client: Optional[Client] = None


async def get_supabase_client() -> Client:
    """Get or create Supabase client."""
    global _supabase_client
    
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        _supabase_client = create_client(url, anon_key)
        logger.info("Supabase client initialized")
    
    return _supabase_client


async def get_style_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's style profile."""
    try:
        client = await get_supabase_client()
        result = client.table("style_profiles").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error("Failed to get style profile", user_id=user_id, error=str(e))
        return None


async def get_pattern(slug: str) -> Optional[Dict[str, Any]]:
    """Get development pattern by slug."""
    try:
        client = await get_supabase_client()
        result = client.table("patterns").select("*").eq("slug", slug).execute()
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error("Failed to get pattern", slug=slug, error=str(e))
        return None


async def create_plan(
    project_id: str, 
    user_id: str, 
    plan_json: Dict[str, Any]
) -> str:
    """Create a new plan and return its ID."""
    try:
        client = await get_supabase_client()
        result = client.table("plans").insert({
            "project_id": project_id,
            "user_id": user_id,
            "plan_json": plan_json
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        raise ValueError("Failed to create plan")
        
    except Exception as e:
        logger.error("Failed to create plan", error=str(e))
        raise


async def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    """Get plan by ID."""
    try:
        client = await get_supabase_client()
        result = client.table("plans").select("*").eq("id", plan_id).execute()
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error("Failed to get plan", plan_id=plan_id, error=str(e))
        return None


async def update_plan(plan_id: str, plan_json: Dict[str, Any]) -> bool:
    """Update plan with new JSON."""
    try:
        client = await get_supabase_client()
        result = client.table("plans").update({
            "plan_json": plan_json,
            "updated_at": "now()"
        }).eq("id", plan_id).execute()
        
        return bool(result.data)
        
    except Exception as e:
        logger.error("Failed to update plan", plan_id=plan_id, error=str(e))
        return False


async def create_plan_revision(
    plan_id: str, 
    message_id: str, 
    patch: List[Dict[str, Any]]
) -> bool:
    """Create a plan revision record."""
    try:
        client = await get_supabase_client()
        result = client.table("plan_revisions").insert({
            "plan_id": plan_id,
            "message_id": message_id,
            "patch": patch
        }).execute()
        
        return bool(result.data)
        
    except Exception as e:
        logger.error("Failed to create plan revision", error=str(e))
        return False


async def create_plan_message(
    plan_id: str, 
    user_question: str, 
    node_path: str, 
    selection_text: str
) -> str:
    """Create a plan message and return its ID."""
    try:
        client = await get_supabase_client()
        result = client.table("plan_messages").insert({
            "plan_id": plan_id,
            "user_question": user_question,
            "node_path": node_path,
            "selection_text": selection_text
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        raise ValueError("Failed to create plan message")
        
    except Exception as e:
        logger.error("Failed to create plan message", error=str(e))
        raise


async def log_dev_event(
    event_type: str, 
    user_id: str, 
    project_id: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Log a development event."""
    try:
        client = await get_supabase_client()
        result = client.table("dev_events").insert({
            "event_type": event_type,
            "user_id": user_id,
            "project_id": project_id,
            "metadata": metadata or {}
        }).execute()
        
        return bool(result.data)
        
    except Exception as e:
        logger.error("Failed to log dev event", error=str(e))
        return False
