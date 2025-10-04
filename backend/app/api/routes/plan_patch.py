from fastapi import APIRouter, HTTPException

from ...models import PlanPatchRequest, PlanJSON
from ...supabase_client import SupabaseAdapter
from ...utils.json_patch import apply_patch

router = APIRouter()


@router.post("/plan/patch", response_model=PlanJSON)
def patch_plan(req: PlanPatchRequest):
    supa = SupabaseAdapter()
    row = supa.fetch_plan(req.plan_id)
    if not row or "plan_json" not in row:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan_json = row["plan_json"]
    try:
        updated = apply_patch(plan_json, [op.model_dump() for op in req.patch], allowed_prefix=req.nodePath)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    supa.update_plan(req.plan_id, updated)
    supa.insert_revision(req.plan_id, [op.model_dump() for op in req.patch], rationale=None)
    supa.broadcast_update(req.plan_id, {"type": "plan_updated", "plan": updated})
    return updated

