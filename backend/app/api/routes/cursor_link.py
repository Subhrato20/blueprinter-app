import json
import os
from fastapi import APIRouter, HTTPException

from ...models import CursorLinkRequest
from ...supabase_client import SupabaseAdapter
from ...security import sign_payload

router = APIRouter()


@router.post("/cursor-link")
def cursor_link(req: CursorLinkRequest):
    supa = SupabaseAdapter()
    row = supa.fetch_plan(req.plan_id)
    if not row or "plan_json" not in row:
        raise HTTPException(status_code=404, detail="Plan not found")

    payload = {
        "planId": req.plan_id,
        "files": row["plan_json"].get("files", []),
        "prBody": row["plan_json"].get("prBody", ""),
    }
    secret = os.getenv("BLUEPRINT_HMAC_SECRET", "dev-secret")
    body_b64, sig_b64 = sign_payload(secret, payload)
    uri = f"vscode://subhrato.blueprint-snap/ingest?payload={body_b64}&sig={sig_b64}"
    return {"link": uri}

