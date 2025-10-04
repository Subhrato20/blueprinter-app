"""Service for generating and managing embeddings for coding preferences and patterns."""

import json
from typing import List, Dict, Any, Optional
import structlog
from openai import AsyncOpenAI

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings for coding preferences and patterns."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client
    
    async def generate_preference_embedding(
        self, 
        preference_text: str, 
        context: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[float]:
        """Generate an embedding for a coding preference."""
        try:
            # Create a comprehensive text for embedding
            combined_text = preference_text
            
            if context:
                combined_text = f"{preference_text}. Context: {context}"
            
            if category:
                combined_text = f"Category: {category}. {combined_text}"
            
            # Add some structure to help with semantic understanding
            structured_text = f"Coding preference: {combined_text}"
            
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=structured_text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error("Failed to generate preference embedding", error=str(e))
            raise
    
    async def generate_signal_embedding(
        self, 
        signal_type: str, 
        signal_data: Dict[str, Any]
    ) -> List[float]:
        """Generate an embedding for a coding signal (behavioral data)."""
        try:
            # Create a structured representation of the signal
            signal_text = f"Signal type: {signal_type}. Data: {json.dumps(signal_data, sort_keys=True)}"
            
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=signal_text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error("Failed to generate signal embedding", error=str(e))
            raise
    
    async def generate_code_pattern_embedding(
        self, 
        code_content: str, 
        file_path: str,
        language: Optional[str] = None
    ) -> List[float]:
        """Generate an embedding for code patterns."""
        try:
            # Create a structured representation of the code
            structured_text = f"Code file: {file_path}"
            
            if language:
                structured_text += f". Language: {language}"
            
            structured_text += f". Content: {code_content[:2000]}"  # Limit content size
            
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=structured_text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error("Failed to generate code pattern embedding", error=str(e))
            raise
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate an embedding for a search query."""
        try:
            # Structure the query for better semantic matching
            structured_query = f"Search query: {query}"
            
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=structured_query
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error("Failed to generate query embedding", error=str(e))
            raise
    
    async def batch_generate_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        try:
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
            
            return embeddings
            
        except Exception as e:
            logger.error("Failed to generate batch embeddings", error=str(e))
            raise


def get_embedding_service(openai_client: AsyncOpenAI) -> EmbeddingService:
    """Get an instance of the embedding service."""
    return EmbeddingService(openai_client)
