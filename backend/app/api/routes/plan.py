from fastapi import APIRouter, HTTPException

from ...models import PlanCreateRequest, PlanJSON
from ...langgraph.graph import PlanGraph
from ...supabase_client import SupabaseAdapter

router = APIRouter()


@router.post("/plan", response_model=PlanJSON)
def create_plan(req: PlanCreateRequest):
    supa = SupabaseAdapter()
    style = supa.fetch_style_for_project(req.project_id)
    graph = PlanGraph()
    plan = graph.run(idea=req.idea, style=style, pattern_slug=req.pattern_slug)

    try:
        supa.insert_plan(req.project_id, plan)
    except Exception as e:
        # Non-fatal in dev mode; surface as warning field in prBody
        plan.prBody += f"\n\n> Warning: plan not persisted ({e})\n"

    return plan

