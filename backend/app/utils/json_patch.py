"""JSON Patch utilities for plan modifications."""

from typing import Any, Dict, List

import fastjsonpatch
import structlog

logger = structlog.get_logger(__name__)

# Allowed paths for JSON Patch operations
ALLOWED_PATHS = {
    "/title",
    "/steps/*",
    "/files/*/content",
    "/tests/*",
    "/risks/*",
    "/prBody"
}


def validate_patch_path(path: str) -> bool:
    """Validate that a patch path is allowed."""
    # Check exact matches
    if path in ALLOWED_PATHS:
        return True
    
    # Check wildcard patterns
    for allowed_path in ALLOWED_PATHS:
        if "*" in allowed_path:
            # Convert wildcard pattern to regex-like matching
            pattern = allowed_path.replace("*", ".*")
            if path.startswith(pattern.split(".*")[0]):
                return True
    
    return False


def validate_patch_operations(patch: List[Dict[str, Any]]) -> bool:
    """Validate all patch operations."""
    for operation in patch:
        if "path" not in operation:
            logger.error("Patch operation missing 'path' field", operation=operation)
            return False
        
        if not validate_patch_path(operation["path"]):
            logger.error("Patch operation has invalid path", path=operation["path"])
            return False
        
        # Validate operation type
        op = operation.get("op")
        if op not in ["add", "remove", "replace", "move", "copy", "test"]:
            logger.error("Invalid patch operation", op=op)
            return False
    
    return True


def apply_patch(plan_json: Dict[str, Any], patch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply JSON patch to plan JSON."""
    try:
        if not validate_patch_operations(patch):
            raise ValueError("Invalid patch operations")
        
        # Apply the patch using fastjsonpatch
        patched_plan = fastjsonpatch.apply_patch(plan_json, patch)
        
        logger.info("Successfully applied patch", operations_count=len(patch))
        return patched_plan
        
    except Exception as e:
        logger.error("Failed to apply patch", error=str(e))
        raise


def create_patch_diff(original: Dict[str, Any], modified: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create a JSON patch diff between original and modified plans."""
    try:
        patch = fastjsonpatch.make_patch(original, modified)
        return patch.patch
        
    except Exception as e:
        logger.error("Failed to create patch diff", error=str(e))
        raise


def preview_patch(plan_json: Dict[str, Any], patch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Preview the result of applying a patch without modifying the original."""
    try:
        if not validate_patch_operations(patch):
            raise ValueError("Invalid patch operations")
        
        # Create a deep copy and apply the patch
        import copy
        preview_plan = copy.deepcopy(plan_json)
        return apply_patch(preview_plan, patch)
        
    except Exception as e:
        logger.error("Failed to preview patch", error=str(e))
        raise
