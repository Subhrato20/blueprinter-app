"""API routes for managing coding preferences and signals."""

import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import structlog

from ..dependencies import get_current_user
from ...supabase_client import get_supabase_client
from ...openai_client import get_openai_client

# Real Supabase integration

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/coding-preferences", tags=["coding-preferences"])


# Pydantic models for coding preferences
class PreferenceCategory(str, Enum):
    FRONTEND_FRAMEWORK = "frontend_framework"
    BACKEND_PATTERN = "backend_pattern"
    CODE_STYLE = "code_style"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    NAMING_CONVENTION = "naming_convention"


class PreferenceStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    ABSOLUTE = "absolute"


class CodingPreferenceCreate(BaseModel):
    category: PreferenceCategory
    preference_text: str = Field(..., description="The actual preference description")
    context: Optional[str] = Field(None, description="Additional context about when this preference applies")
    strength: PreferenceStrength = Field(PreferenceStrength.MODERATE)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CodingPreferenceUpdate(BaseModel):
    preference_text: Optional[str] = None
    context: Optional[str] = None
    strength: Optional[PreferenceStrength] = None
    metadata: Optional[Dict[str, Any]] = None


class CodingPreferenceResponse(BaseModel):
    id: str
    category: PreferenceCategory
    preference_text: str
    context: Optional[str]
    strength: PreferenceStrength
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class CodingSignalCreate(BaseModel):
    signal_type: str = Field(..., description="Type of signal (e.g., 'file_created', 'code_pattern_used')")
    signal_data: Dict[str, Any] = Field(..., description="The actual signal data")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)


class SimilaritySearchRequest(BaseModel):
    query_text: str = Field(..., description="Text to find similar preferences for")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    max_results: int = Field(10, ge=1, le=50)


class SimilaritySearchResponse(BaseModel):
    preferences: List[CodingPreferenceResponse]
    similarities: List[float]


class CodingStyleSummary(BaseModel):
    category: PreferenceCategory
    preference_count: int
    top_preferences: List[str]


@router.post("/", response_model=CodingPreferenceResponse)
async def create_coding_preference(
    preference: CodingPreferenceCreate,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client),
    openai=Depends(get_openai_client)
):
    """Create a new coding preference with automatic embedding generation."""
    try:
        user_id = current_user["id"]
        
        # Insert preference into database (without embedding for now)
        result = supabase.table("coding_preferences").insert({
            "user_id": user_id,
            "category": preference.category,
            "preference_text": preference.preference_text,
            "context": preference.context,
            "strength": preference.strength,
            "metadata": preference.metadata
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create coding preference"
            )
        
        return CodingPreferenceResponse(**result.data[0])
        
    except Exception as e:
        logger.error("Failed to create coding preference", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coding preference: {str(e)}"
        )


@router.get("/", response_model=List[CodingPreferenceResponse])
async def get_coding_preferences(
    category: Optional[PreferenceCategory] = None,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client)
):
    """Get all coding preferences for the current user, optionally filtered by category."""
    try:
        user_id = current_user["id"]
        
        query = supabase.table("coding_preferences").select("*").eq("user_id", user_id)
        
        if category:
            query = query.eq("category", category)
        
        result = query.order("created_at", desc=True).execute()
        
        return [CodingPreferenceResponse(**pref) for pref in result.data]
        
    except Exception as e:
        logger.error("Failed to get coding preferences", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coding preferences: {str(e)}"
        )


@router.get("/summary", response_model=List[CodingStyleSummary])
async def get_coding_style_summary(
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client)
):
    """Get a summary of the user's coding style preferences by category."""
    try:
        user_id = current_user["id"]
        
        result = supabase.rpc("get_coding_style_summary", {
            "user_id_param": user_id
        }).execute()
        
        return [CodingStyleSummary(**summary) for summary in result.data]
        
    except Exception as e:
        logger.error("Failed to get coding style summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coding style summary: {str(e)}"
        )


@router.put("/{preference_id}", response_model=CodingPreferenceResponse)
async def update_coding_preference(
    preference_id: str,
    preference_update: CodingPreferenceUpdate,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client),
    openai=Depends(get_openai_client)
):
    """Update an existing coding preference."""
    try:
        user_id = current_user["id"]
        
        # Get current preference
        current_result = supabase.table("coding_preferences").select("*").eq("id", preference_id).eq("user_id", user_id).execute()
        
        if not current_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coding preference not found"
            )
        
        current_pref = current_result.data[0]
        
        # Prepare update data
        update_data = {}
        for field, value in preference_update.dict(exclude_unset=True).items():
            update_data[field] = value
        
        # If preference text or context changed, regenerate embedding
        if preference_update.preference_text or preference_update.context:
            new_text = preference_update.preference_text or current_pref["preference_text"]
            new_context = preference_update.context or current_pref["context"]
            
            embedding = await generate_preference_embedding(new_text, new_context, openai)
            update_data["embedding"] = embedding
        
        # Update preference
        result = supabase.table("coding_preferences").update(update_data).eq("id", preference_id).eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update coding preference"
            )
        
        return CodingPreferenceResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update coding preference", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update coding preference: {str(e)}"
        )


@router.delete("/{preference_id}")
async def delete_coding_preference(
    preference_id: str,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client)
):
    """Delete a coding preference."""
    try:
        user_id = current_user["id"]
        
        result = supabase.table("coding_preferences").delete().eq("id", preference_id).eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coding preference not found"
            )
        
        return {"message": "Coding preference deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete coding preference", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete coding preference: {str(e)}"
        )


@router.post("/search", response_model=SimilaritySearchResponse)
async def search_similar_preferences(
    search_request: SimilaritySearchRequest,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client),
    openai=Depends(get_openai_client)
):
    """Search for similar coding preferences using vector similarity."""
    try:
        user_id = current_user["id"]
        
        # Generate embedding for search query
        query_embedding = await generate_preference_embedding(
            search_request.query_text, 
            None, 
            openai
        )
        
        # Search for similar preferences
        result = supabase.rpc("find_similar_preferences", {
            "user_id_param": user_id,
            "query_embedding": query_embedding,
            "similarity_threshold": search_request.similarity_threshold,
            "max_results": search_request.max_results
        }).execute()
        
        preferences = []
        similarities = []
        
        for item in result.data:
            preferences.append(CodingPreferenceResponse(
                id=item["id"],
                category=item["category"],
                preference_text=item["preference_text"],
                context=item["context"],
                strength=item["strength"],
                metadata=item["metadata"],
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            ))
            similarities.append(item["similarity"])
        
        return SimilaritySearchResponse(
            preferences=preferences,
            similarities=similarities
        )
        
    except Exception as e:
        logger.error("Failed to search similar preferences", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search similar preferences: {str(e)}"
        )


@router.post("/signals")
async def create_coding_signal(
    signal: CodingSignalCreate,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase_client),
    openai=Depends(get_openai_client)
):
    """Create a coding signal (behavioral data) with automatic embedding generation."""
    try:
        user_id = current_user["id"]
        
        # Generate embedding for the signal data
        signal_text = f"{signal.signal_type}: {json.dumps(signal.signal_data)}"
        embedding = await generate_preference_embedding(signal_text, None, openai)
        
        # Insert signal into database
        result = supabase.table("coding_signals").insert({
            "user_id": user_id,
            "signal_type": signal.signal_type,
            "signal_data": signal.signal_data,
            "embedding": embedding,
            "confidence_score": signal.confidence_score
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create coding signal"
            )
        
        return {"message": "Coding signal created successfully", "id": result.data[0]["id"]}
        
    except Exception as e:
        logger.error("Failed to create coding signal", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coding signal: {str(e)}"
        )


async def generate_preference_embedding(
    text: str, 
    context: Optional[str], 
    openai_client
) -> List[float]:
    """Generate an embedding for preference text using OpenAI."""
    try:
        # Combine text and context for embedding
        combined_text = text
        if context:
            combined_text = f"{text}. Context: {context}"
        
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=combined_text
        )
        
        return response.data[0].embedding
        
    except Exception as e:
        logger.error("Failed to generate embedding", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {str(e)}"
        )
