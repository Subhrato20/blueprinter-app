from fastapi import APIRouter

from ...models import AskRequest

router = APIRouter()


@router.post("/ask")
def ask_copilot(req: AskRequest):
    # Placeholder advisor: produce a deterministic suggestion/patch
    target_path = req.nodePath.rstrip("/") + "/summary"
    patch = [
        {"op": "replace", "path": target_path, "value": "Refine: " + (req.selection or "Improve step")}
    ]
    return {
        "rationale": "Deterministic placeholder: prepend 'Refine:' to the selected step's summary.",
        "patch": patch,
    }

