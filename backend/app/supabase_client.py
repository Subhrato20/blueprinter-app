from __future__ import annotations
import os
from typing import Any, Optional

from .models import StyleTokens, PlanJSON


MEM_STORE: dict[str, dict[str, Any]] = {}


class SupabaseAdapter:
    """Thin adapter; replace with real supabase client calls.

    This default implementation is a no-op that returns sensible defaults
    so the API can run without Supabase during early development.
    """

    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # --- style profiles ---
    def fetch_style_for_project(self, project_id: str) -> StyleTokens:
        # TODO: fetch from style_profiles by project owner; fallback to defaults
        return StyleTokens()

    # --- patterns ---
    def fetch_pattern(self, slug: Optional[str]) -> dict[str, Any]:
        # TODO: fetch from patterns table; fallback handled in graph
        return {"slug": slug}

    # --- plans ---
    def insert_plan(self, project_id: str, plan: PlanJSON) -> str:
        # Dev store: keep a single in-memory plan under id 'dev'
        plan_id = "dev"
        MEM_STORE[plan_id] = {"project_id": project_id, "plan_json": plan.model_dump()}
        return plan_id

    def update_plan(self, plan_id: str, plan: PlanJSON | dict[str, Any]) -> None:
        row = MEM_STORE.get(plan_id)
        if row is None:
            return
        row["plan_json"] = plan if isinstance(plan, dict) else plan.model_dump()

    def fetch_plan(self, plan_id: str) -> dict[str, Any] | None:
        return MEM_STORE.get(plan_id)

    # --- revisions ---
    def insert_revision(self, plan_id: str, patch: list[dict], rationale: str | None) -> str:
        # TODO: insert into plan_revisions
        return "rev_" + plan_id[-6:]

    # --- realtime ---
    def broadcast_update(self, plan_id: str, payload: dict[str, Any]) -> None:
        # TODO: use Realtime to broadcast plan update
        return None
