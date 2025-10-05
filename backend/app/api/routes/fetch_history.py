"""Fetch History API routes."""

from typing import Optional
from datetime import datetime

import structlog
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models import (
    CreateFetchHistoryRequest,
    FetchHistoryResponse,
    FetchHistoryItem,
)
from app.supabase_client import get_supabase_client

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/fetch-history")
async def create_fetch_history(request: CreateFetchHistoryRequest):
    """Create a new fetch history entry."""
    try:
        supabase = await get_supabase_client()
        
        data = {
            "endpoint": request.endpoint,
            "method": request.method,
            "request_data": request.request_data,
            "response_data": request.response_data,
            "status_code": request.status_code,
            "duration_ms": request.duration_ms,
            "error_message": request.error_message,
        }
        
        result = supabase.table("fetch_history").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create history entry")
        
        return JSONResponse(
            status_code=201,
            content={"success": True, "id": result.data[0]["id"]}
        )
    except Exception as e:
        logger.error("Failed to create fetch history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-history", response_model=FetchHistoryResponse)
async def get_fetch_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
):
    """Get fetch history with pagination and filters."""
    try:
        supabase = await get_supabase_client()
        
        # Build query
        query = supabase.table("fetch_history").select("*", count="exact")
        
        # Apply filters
        if endpoint:
            query = query.ilike("endpoint", f"%{endpoint}%")
        if method:
            query = query.eq("method", method.upper())
        if status_code:
            query = query.eq("status_code", status_code)
        
        # Get total count
        count_result = query.execute()
        total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order("created_at", desc=True).range(offset, offset + page_size - 1)
        
        result = query.execute()
        
        items = [
            FetchHistoryItem(
                id=str(item["id"]),
                user_id=str(item["user_id"]) if item.get("user_id") else None,
                endpoint=item["endpoint"],
                method=item["method"],
                request_data=item.get("request_data"),
                response_data=item.get("response_data"),
                status_code=item.get("status_code"),
                duration_ms=item.get("duration_ms"),
                error_message=item.get("error_message"),
                created_at=item["created_at"],
            )
            for item in result.data
        ]
        
        return FetchHistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error("Failed to get fetch history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/fetch-history/{history_id}")
async def delete_fetch_history(history_id: str):
    """Delete a fetch history entry."""
    try:
        supabase = await get_supabase_client()
        
        result = supabase.table("fetch_history").delete().eq("id", history_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="History entry not found")
        
        return JSONResponse(content={"success": True})
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete fetch history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/fetch-history")
async def clear_fetch_history():
    """Clear all fetch history entries."""
    try:
        supabase = await get_supabase_client()
        
        # Delete all entries
        result = supabase.table("fetch_history").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        return JSONResponse(
            content={"success": True, "deleted_count": len(result.data) if result.data else 0}
        )
    except Exception as e:
        logger.error("Failed to clear fetch history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-history/stats")
async def get_fetch_history_stats():
    """Get statistics about fetch history."""
    try:
        supabase = await get_supabase_client()
        
        # Get all history entries for stats
        result = supabase.table("fetch_history").select("*").execute()
        
        total = len(result.data)
        
        # Calculate stats
        methods = {}
        endpoints = {}
        status_codes = {}
        total_duration = 0
        error_count = 0
        
        for item in result.data:
            method = item.get("method", "UNKNOWN")
            methods[method] = methods.get(method, 0) + 1
            
            endpoint = item.get("endpoint", "unknown")
            endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
            
            status_code = item.get("status_code")
            if status_code:
                status_codes[str(status_code)] = status_codes.get(str(status_code), 0) + 1
            
            duration = item.get("duration_ms", 0)
            if duration:
                total_duration += duration
            
            if item.get("error_message"):
                error_count += 1
        
        avg_duration = total_duration / total if total > 0 else 0
        
        return {
            "total_requests": total,
            "methods": methods,
            "endpoints": endpoints,
            "status_codes": status_codes,
            "average_duration_ms": round(avg_duration, 2),
            "error_count": error_count,
            "success_rate": round((total - error_count) / total * 100, 2) if total > 0 else 0,
        }
    except Exception as e:
        logger.error("Failed to get fetch history stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
