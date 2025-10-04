"""LangGraph orchestration for plan generation."""

import re
from typing import Any, Dict, List

import structlog
from langgraph.graph import StateGraph, END

from app.openai_client import analyze_intent, gpt5_plan
from app.supabase_client import get_style_profile, get_pattern

logger = structlog.get_logger(__name__)


class PlanGenerationState:
    """State for plan generation workflow."""
    
    def __init__(self):
        self.idea: str = ""
        self.project_id: str = ""
        self.user_id: str = ""
        self.intent: Dict[str, str] = {}
        self.pattern: Dict[str, Any] = {}
        self.style_profile: Dict[str, Any] = {}
        self.plan_json: Dict[str, Any] = {}
        self.error: str = ""


async def intent_parser_node(state: PlanGenerationState) -> PlanGenerationState:
    """Parse user intent to extract feature and route."""
    try:
        logger.info("Parsing intent", idea=state.idea)
        
        # Use regex as fallback, then GPT-5 for complex cases
        intent = await analyze_intent(state.idea)
        
        # Validate and set defaults
        if not intent.get("feature"):
            intent["feature"] = "general"
        if not intent.get("route"):
            intent["route"] = "/api"
        
        state.intent = intent
        logger.info("Intent parsed", intent=intent)
        
    except Exception as e:
        logger.error("Failed to parse intent", error=str(e))
        state.error = f"Intent parsing failed: {str(e)}"
    
    return state


async def pattern_loader_node(state: PlanGenerationState) -> PlanGenerationState:
    """Load development pattern template."""
    try:
        logger.info("Loading pattern", feature=state.intent.get("feature"))
        
        # Try to get pattern based on feature, fallback to default
        pattern_slug = f"{state.intent.get('feature', 'general')}-pattern"
        pattern = await get_pattern(pattern_slug)
        
        if not pattern:
            # Fallback to default pattern
            pattern = await get_pattern("api-search-pagination")
        
        if not pattern:
            # Create a minimal default pattern
            pattern = {
                "slug": "default",
                "template": {
                    "steps": [
                        {"kind": "code", "target": "main", "summary": "Implement core functionality"},
                        {"kind": "test", "target": "tests", "summary": "Add tests"},
                        {"kind": "config", "target": "config", "summary": "Update configuration"}
                    ],
                    "files": [],
                    "risks": ["Consider edge cases", "Test thoroughly"],
                    "tests": ["Unit tests", "Integration tests"],
                    "prBody": "Implementation of requested feature"
                }
            }
        
        state.pattern = pattern
        logger.info("Pattern loaded", pattern_slug=pattern.get("slug"))
        
    except Exception as e:
        logger.error("Failed to load pattern", error=str(e))
        state.error = f"Pattern loading failed: {str(e)}"
    
    return state


async def style_adapter_node(state: PlanGenerationState) -> PlanGenerationState:
    """Load and apply user's coding style preferences."""
    try:
        logger.info("Loading style profile", user_id=state.user_id)
        
        style_profile = await get_style_profile(state.user_id)
        
        if not style_profile:
            # Default style profile
            style_profile = {
                "tokens": {
                    "quotes": "double",
                    "semicolons": True,
                    "indent": "spaces",
                    "indent_size": 2,
                    "test_framework": "jest",
                    "directories": ["src", "tests"],
                    "aliases": {"@": "src"},
                    "language": "typescript"
                }
            }
        
        state.style_profile = style_profile
        logger.info("Style profile loaded", tokens=style_profile.get("tokens", {}))
        
    except Exception as e:
        logger.error("Failed to load style profile", error=str(e))
        state.error = f"Style profile loading failed: {str(e)}"
    
    return state


async def design_node(state: PlanGenerationState) -> PlanGenerationState:
    """Generate the complete plan using GPT-5."""
    try:
        logger.info("Generating plan with GPT-5")
        
        if state.error:
            return state
        
        plan_json = await gpt5_plan(
            idea=state.idea,
            route=state.intent.get("route", "/api"),
            pattern=state.pattern,
            style=state.style_profile.get("tokens", {})
        )
        
        # Convert Pydantic model to dict
        state.plan_json = plan_json.model_dump()
        logger.info("Plan generated successfully", title=plan_json.title)
        
    except Exception as e:
        logger.error("Failed to generate plan", error=str(e))
        state.error = f"Plan generation failed: {str(e)}"
    
    return state


async def style_adaptation_node(state: PlanGenerationState) -> PlanGenerationState:
    """Apply style adaptations to the generated plan."""
    try:
        logger.info("Applying style adaptations")
        
        if state.error or not state.plan_json:
            return state
        
        style_tokens = state.style_profile.get("tokens", {})
        
        # Apply style transformations to files
        for file_data in state.plan_json.get("files", []):
            content = file_data.get("content", "")
            
            # Apply quote style
            if style_tokens.get("quotes") == "single":
                content = content.replace('"', "'")
            elif style_tokens.get("quotes") == "double":
                content = content.replace("'", '"')
            
            # Apply semicolon preference
            if not style_tokens.get("semicolons", True):
                # Remove trailing semicolons (simple approach)
                content = re.sub(r';\s*\n', '\n', content)
            
            # Apply indentation
            indent_type = style_tokens.get("indent", "spaces")
            indent_size = style_tokens.get("indent_size", 2)
            
            if indent_type == "tabs":
                # Convert spaces to tabs (simplified)
                lines = content.split('\n')
                adapted_lines = []
                for line in lines:
                    if line.startswith(' ' * indent_size):
                        adapted_lines.append('\t' + line[indent_size:])
                    else:
                        adapted_lines.append(line)
                content = '\n'.join(adapted_lines)
            
            file_data["content"] = content
        
        logger.info("Style adaptations applied")
        
    except Exception as e:
        logger.error("Failed to apply style adaptations", error=str(e))
        state.error = f"Style adaptation failed: {str(e)}"
    
    return state


def create_plan_generation_graph() -> StateGraph:
    """Create the LangGraph workflow for plan generation."""
    
    # Create the state graph
    workflow = StateGraph(PlanGenerationState)
    
    # Add nodes
    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("pattern_loader", pattern_loader_node)
    workflow.add_node("style_adapter", style_adapter_node)
    workflow.add_node("design", design_node)
    workflow.add_node("style_adaptation", style_adaptation_node)
    
    # Define the flow
    workflow.set_entry_point("intent_parser")
    
    workflow.add_edge("intent_parser", "pattern_loader")
    workflow.add_edge("pattern_loader", "style_adapter")
    workflow.add_edge("style_adapter", "design")
    workflow.add_edge("design", "style_adaptation")
    workflow.add_edge("style_adaptation", END)
    
    return workflow.compile()


async def generate_plan(idea: str, project_id: str, user_id: str) -> Dict[str, Any]:
    """Generate a complete development plan."""
    try:
        # Create the workflow
        workflow = create_plan_generation_graph()
        
        # Initialize state
        initial_state = PlanGenerationState()
        initial_state.idea = idea
        initial_state.project_id = project_id
        initial_state.user_id = user_id
        
        # Run the workflow
        final_state = await workflow.ainvoke(initial_state)
        
        if final_state.error:
            raise ValueError(final_state.error)
        
        return final_state.plan_json
        
    except Exception as e:
        logger.error("Plan generation workflow failed", error=str(e))
        raise
