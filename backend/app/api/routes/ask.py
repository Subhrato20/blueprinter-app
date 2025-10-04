from fastapi import APIRouter
import os

from ...models import AskRequest
from ...openai_client import OpenAIClient

router = APIRouter()


@router.post("/ask")
def ask_copilot(req: AskRequest):
    # Use OpenAI if API key is available, otherwise fallback to deterministic
    if os.getenv("OPENAI_API_KEY"):
        openai_client = OpenAIClient()
        context = f"Plan node: {req.nodePath}"
        return openai_client.ask_copilot(req.question, context, req.selection)
    else:
        # Fallback to deterministic response
        target_path = req.nodePath.rstrip("/") + "/summary"
        patch = [
            {"op": "replace", "path": target_path, "value": "Refine: " + (req.selection or "Improve step")}
        ]
        return {
            "rationale": "Deterministic placeholder: prepend 'Refine:' to the selected step's summary.",
            "patch": patch,
        }

