"""Service for learning coding patterns from signals and providing intelligent suggestions."""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from supabase import Client

from .embedding_service import EmbeddingService

logger = structlog.get_logger(__name__)


class PatternLearningService:
    """Service for learning coding patterns from user signals and providing suggestions."""
    
    def __init__(self, supabase_client: Client, embedding_service: EmbeddingService):
        self.supabase = supabase_client
        self.embedding_service = embedding_service
    
    async def learn_from_signals(
        self, 
        user_id: str, 
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Learn patterns from recent coding signals."""
        try:
            # Get recent signals
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            signals_result = self.supabase.table("coding_signals").select("*").eq(
                "user_id", user_id
            ).gte("created_at", cutoff_date.isoformat()).execute()
            
            if not signals_result.data:
                logger.info("No recent signals found for pattern learning", user_id=user_id)
                return []
            
            # Group signals by type
            signals_by_type = {}
            for signal in signals_result.data:
                signal_type = signal["signal_type"]
                if signal_type not in signals_by_type:
                    signals_by_type[signal_type] = []
                signals_by_type[signal_type].append(signal)
            
            # Learn patterns from each signal type
            learned_patterns = []
            for signal_type, signals in signals_by_type.items():
                patterns = await self._learn_patterns_from_signals(signal_type, signals)
                learned_patterns.extend(patterns)
            
            # Store learned patterns
            for pattern in learned_patterns:
                await self._store_learned_pattern(user_id, pattern)
            
            return learned_patterns
            
        except Exception as e:
            logger.error("Failed to learn from signals", error=str(e), user_id=user_id)
            raise
    
    async def _learn_patterns_from_signals(
        self, 
        signal_type: str, 
        signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Learn patterns from a specific type of signals."""
        patterns = []
        
        if signal_type == "file_created":
            patterns.extend(await self._learn_file_creation_patterns(signals))
        elif signal_type == "code_pattern_used":
            patterns.extend(await self._learn_code_patterns(signals))
        elif signal_type == "refactor_applied":
            patterns.extend(await self._learn_refactoring_patterns(signals))
        elif signal_type == "test_written":
            patterns.extend(await self._learn_testing_patterns(signals))
        
        return patterns
    
    async def _learn_file_creation_patterns(
        self, 
        signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Learn patterns from file creation signals."""
        patterns = []
        
        # Group by file extension/type
        file_types = {}
        for signal in signals:
            file_path = signal["signal_data"].get("file_path", "")
            if "." in file_path:
                ext = file_path.split(".")[-1].lower()
                if ext not in file_types:
                    file_types[ext] = []
                file_types[ext].append(signal)
        
        # Create patterns for common file types
        for ext, ext_signals in file_types.items():
            if len(ext_signals) >= 3:  # Minimum threshold for pattern recognition
                pattern = {
                    "pattern_name": f"frequent_{ext}_file_creation",
                    "pattern_description": f"Frequently creates {ext} files",
                    "pattern_data": {
                        "file_extension": ext,
                        "frequency": len(ext_signals),
                        "common_paths": self._extract_common_paths(ext_signals)
                    },
                    "confidence_score": min(len(ext_signals) / 10.0, 1.0)
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _learn_code_patterns(
        self, 
        signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Learn patterns from code pattern usage signals."""
        patterns = []
        
        # Group by pattern type
        pattern_types = {}
        for signal in signals:
            pattern_type = signal["signal_data"].get("pattern_type", "unknown")
            if pattern_type not in pattern_types:
                pattern_types[pattern_type] = []
            pattern_types[pattern_type].append(signal)
        
        # Create patterns for frequently used code patterns
        for pattern_type, type_signals in pattern_types.items():
            if len(type_signals) >= 2:
                pattern = {
                    "pattern_name": f"preferred_{pattern_type}_pattern",
                    "pattern_description": f"Prefers {pattern_type} pattern",
                    "pattern_data": {
                        "pattern_type": pattern_type,
                        "frequency": len(type_signals),
                        "contexts": [s["signal_data"].get("context", "") for s in type_signals]
                    },
                    "confidence_score": min(len(type_signals) / 5.0, 1.0)
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _learn_refactoring_patterns(
        self, 
        signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Learn patterns from refactoring signals."""
        patterns = []
        
        # Group by refactoring type
        refactor_types = {}
        for signal in signals:
            refactor_type = signal["signal_data"].get("refactor_type", "unknown")
            if refactor_type not in refactor_types:
                refactor_types[refactor_type] = []
            refactor_types[refactor_type].append(signal)
        
        # Create patterns for common refactoring approaches
        for refactor_type, type_signals in refactor_types.items():
            if len(type_signals) >= 2:
                pattern = {
                    "pattern_name": f"common_{refactor_type}_refactoring",
                    "pattern_description": f"Commonly applies {refactor_type} refactoring",
                    "pattern_data": {
                        "refactor_type": refactor_type,
                        "frequency": len(type_signals),
                        "triggers": [s["signal_data"].get("trigger", "") for s in type_signals]
                    },
                    "confidence_score": min(len(type_signals) / 3.0, 1.0)
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _learn_testing_patterns(
        self, 
        signals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Learn patterns from testing signals."""
        patterns = []
        
        # Group by test type
        test_types = {}
        for signal in signals:
            test_type = signal["signal_data"].get("test_type", "unknown")
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(signal)
        
        # Create patterns for testing preferences
        for test_type, type_signals in test_types.items():
            if len(type_signals) >= 2:
                pattern = {
                    "pattern_name": f"preferred_{test_type}_testing",
                    "pattern_description": f"Prefers {test_type} testing approach",
                    "pattern_data": {
                        "test_type": test_type,
                        "frequency": len(type_signals),
                        "frameworks": [s["signal_data"].get("framework", "") for s in type_signals]
                    },
                    "confidence_score": min(len(type_signals) / 3.0, 1.0)
                }
                patterns.append(pattern)
        
        return patterns
    
    def _extract_common_paths(self, signals: List[Dict[str, Any]]) -> List[str]:
        """Extract common directory paths from file creation signals."""
        paths = []
        for signal in signals:
            file_path = signal["signal_data"].get("file_path", "")
            if "/" in file_path:
                dir_path = "/".join(file_path.split("/")[:-1])
                paths.append(dir_path)
        
        # Count path frequencies
        path_counts = {}
        for path in paths:
            path_counts[path] = path_counts.get(path, 0) + 1
        
        # Return most common paths
        return sorted(path_counts.keys(), key=lambda x: path_counts[x], reverse=True)[:5]
    
    async def _store_learned_pattern(
        self, 
        user_id: str, 
        pattern: Dict[str, Any]
    ) -> None:
        """Store a learned pattern in the database."""
        try:
            # Generate embedding for the pattern
            pattern_text = f"{pattern['pattern_name']}: {pattern['pattern_description']}"
            embedding = await self.embedding_service.generate_preference_embedding(pattern_text)
            
            # Check if pattern already exists
            existing = self.supabase.table("preference_patterns").select("*").eq(
                "user_id", user_id
            ).eq("pattern_name", pattern["pattern_name"]).execute()
            
            if existing.data:
                # Update existing pattern
                self.supabase.table("preference_patterns").update({
                    "pattern_description": pattern["pattern_description"],
                    "pattern_data": pattern["pattern_data"],
                    "embedding": embedding,
                    "confidence_score": pattern["confidence_score"],
                    "signal_count": pattern["pattern_data"].get("frequency", 0)
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Insert new pattern
                self.supabase.table("preference_patterns").insert({
                    "user_id": user_id,
                    "pattern_name": pattern["pattern_name"],
                    "pattern_description": pattern["pattern_description"],
                    "pattern_data": pattern["pattern_data"],
                    "embedding": embedding,
                    "confidence_score": pattern["confidence_score"],
                    "signal_count": pattern["pattern_data"].get("frequency", 0)
                }).execute()
                
        except Exception as e:
            logger.error("Failed to store learned pattern", error=str(e), pattern=pattern["pattern_name"])
            raise
    
    async def get_suggestions_for_context(
        self, 
        user_id: str, 
        context: str,
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """Get coding suggestions based on learned patterns and preferences."""
        try:
            # Generate embedding for the context
            context_embedding = await self.embedding_service.generate_query_embedding(context)
            
            # Find similar preferences
            similar_prefs = self.supabase.rpc("find_similar_preferences", {
                "user_id_param": user_id,
                "query_embedding": context_embedding,
                "similarity_threshold": 0.6,
                "max_results": max_suggestions
            }).execute()
            
            # Find similar patterns
            similar_patterns = self.supabase.table("preference_patterns").select("*").eq(
                "user_id", user_id
            ).execute()
            
            # Calculate similarities for patterns
            pattern_similarities = []
            for pattern in similar_patterns.data:
                if pattern["embedding"]:
                    # Calculate cosine similarity
                    similarity = self._calculate_cosine_similarity(
                        context_embedding, 
                        pattern["embedding"]
                    )
                    if similarity > 0.6:
                        pattern_similarities.append({
                            "pattern": pattern,
                            "similarity": similarity
                        })
            
            # Sort by similarity
            pattern_similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Combine suggestions
            suggestions = []
            
            # Add preference-based suggestions
            for pref in similar_prefs.data:
                suggestions.append({
                    "type": "preference",
                    "title": f"Follow your preference: {pref['preference_text']}",
                    "description": pref.get("context", ""),
                    "strength": pref["strength"],
                    "similarity": pref["similarity"],
                    "category": pref["category"]
                })
            
            # Add pattern-based suggestions
            for item in pattern_similarities[:max_suggestions]:
                pattern = item["pattern"]
                suggestions.append({
                    "type": "pattern",
                    "title": f"Based on your pattern: {pattern['pattern_name']}",
                    "description": pattern["pattern_description"],
                    "confidence": pattern["confidence_score"],
                    "similarity": item["similarity"],
                    "data": pattern["pattern_data"]
                })
            
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error("Failed to get suggestions", error=str(e), user_id=user_id)
            raise
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)


def get_pattern_learning_service(
    supabase_client: Client, 
    embedding_service: EmbeddingService
) -> PatternLearningService:
    """Get an instance of the pattern learning service."""
    return PatternLearningService(supabase_client, embedding_service)
