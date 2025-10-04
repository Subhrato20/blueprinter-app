from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import os

from ..models import PlanJSON, PlanStep, PlanFile, StyleTokens
from ..openai_client import OpenAIClient


@dataclass
class Intent:
    feature: str
    route: str | None


def intent_parser(idea: str) -> Intent:
    route = None
    # naive extraction: look for /path-like token
    tokens = idea.split()
    for t in tokens:
        if t.startswith("/") and len(t) > 1:
            route = t
            break
    return Intent(feature=idea, route=route)


def pattern_loader(slug: str | None, fallback: str = "rest-endpoint") -> Dict[str, Any]:
    # In production, fetch from Supabase patterns table by slug
    # Here we return a tiny default template
    return {
        "slug": slug or fallback,
        "template": {
            "steps": [
                {"kind": "api", "target": "backend", "summary": "Add endpoint"},
                {"kind": "ui", "target": "frontend", "summary": "Add view"},
                {"kind": "test", "target": "repo", "summary": "Add tests"},
            ],
            "files": []
        },
    }


def style_adapter(tokens: StyleTokens, content: str) -> str:
    # trivial adapter for quotes/semicolons; extend as needed
    adapted = content
    if tokens.lang in ("ts", "js"):
        if tokens.quotes == "single":
            adapted = adapted.replace('"', "'")
        else:
            adapted = adapted.replace("'", '"')
        if tokens.semi is False:
            adapted = adapted.replace(";\n", "\n")
    return adapted


def plan_builder(intent: Intent, pattern: Dict[str, Any], style: StyleTokens) -> PlanJSON:
    title = intent.feature.strip().capitalize()
    steps = [PlanStep(**s) for s in pattern["template"]["steps"]]

    files: list[PlanFile] = []

    if intent.route and style.lang in ("ts", "js"):
        route_path = style.routeDir or "apps/api/src/routes"
        file_path = f"{route_path}{intent.route}.ts"
        content = f"export default function handler(req, res) {{\n  res.status(200).json({{ ok: true }})\n}}\n"
        files.append(PlanFile(path=file_path, content=style_adapter(style, content)))

    risks = [
        "Ensure consistent code style application",
        "Verify pagination logic and edge cases",
    ]
    tests = [
        "Add unit tests for API handler",
        "Add integration test for UI pagination",
    ]
    pr_body = f"""## {title}\n\n- Implements: {intent.route or 'N/A'}\n- Pattern: {pattern['slug']}\n\n### Checklist\n- [ ] API added\n- [ ] UI added\n- [ ] Tests added\n"""

    return PlanJSON(title=title, steps=steps, files=files, risks=risks, tests=tests, prBody=pr_body)


class PlanGraph:
    def __init__(self):
        self.openai_client = OpenAIClient() if os.getenv("OPENAI_API_KEY") else None
    
    def run(self, idea: str, style: StyleTokens, pattern_slug: str | None) -> PlanJSON:
        # Use OpenAI if API key is available, otherwise fallback to deterministic
        if self.openai_client:
            return self.openai_client.generate_plan(idea, style, pattern_slug)
        else:
            # Fallback to original deterministic logic
            intent = intent_parser(idea)
            pattern = pattern_loader(pattern_slug)
            return plan_builder(intent, pattern, style)

