import os
from typing import Dict, Any, List
from openai import OpenAI
from ..models import PlanJSON, PlanStep, PlanFile, StyleTokens


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-5")
    
    def generate_plan(self, idea: str, style: StyleTokens, pattern_slug: str = None) -> PlanJSON:
        """Generate a development plan using GPT-5"""
        
        system_prompt = f"""You are an expert software architect and developer. Generate a comprehensive development plan for the given feature idea.

Style preferences:
- Language: {style.lang}
- Indentation: {style.indent} spaces
- Quotes: {style.quotes}
- Semicolons: {'enabled' if style.semi else 'disabled'}
- Testing framework: {style.tests or 'standard'}
- Route directory: {style.routeDir or 'default'}
- Import alias: {style.alias or 'default'}

Generate a detailed plan with:
1. Clear, actionable steps
2. File structure with realistic code
3. Risk assessment
4. Test strategy
5. PR description

Be specific and practical. Consider the developer's coding style preferences."""

        user_prompt = f"""Create a development plan for: "{idea}"

Pattern: {pattern_slug or 'custom'}

Please provide a JSON response with this structure:
{{
  "title": "Feature Title",
  "steps": [
    {{"kind": "api", "target": "backend", "summary": "Step description"}},
    {{"kind": "ui", "target": "frontend", "summary": "Step description"}},
    {{"kind": "test", "target": "repo", "summary": "Step description"}}
  ],
  "files": [
    {{"path": "file/path", "content": "actual code content"}}
  ],
  "risks": ["Risk 1", "Risk 2"],
  "tests": ["Test 1", "Test 2"],
  "prBody": "## Feature Title\n\nDescription and checklist"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            import json
            plan_data = json.loads(content)
            
            # Convert to PlanJSON
            steps = [PlanStep(**step) for step in plan_data.get("steps", [])]
            files = [PlanFile(**file) for file in plan_data.get("files", [])]
            
            return PlanJSON(
                title=plan_data.get("title", idea),
                steps=steps,
                files=files,
                risks=plan_data.get("risks", []),
                tests=plan_data.get("tests", []),
                prBody=plan_data.get("prBody", "")
            )
            
        except Exception as e:
            # Fallback to deterministic plan if OpenAI fails
            return self._fallback_plan(idea, style)
    
    def ask_copilot(self, question: str, context: str, selection: str = None) -> Dict[str, Any]:
        """Generate copilot advice using GPT-5"""
        
        system_prompt = """You are an expert software development copilot. Provide helpful, actionable advice for improving code or development plans.

Be specific, practical, and consider best practices. If asked about a specific selection, focus your advice on that area."""

        user_prompt = f"""Context: {context}

Question: {question}

{f"Selected code/plan section: {selection}" if selection else ""}

Provide:
1. A clear rationale for your advice
2. Specific suggestions for improvement
3. A JSON patch to apply the changes (if applicable)

Format your response as JSON:
{{
  "rationale": "Your reasoning and advice",
  "patch": [
    {{"op": "replace", "path": "/path/to/field", "value": "new value"}}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            import json
            return json.loads(content)
            
        except Exception as e:
            # Fallback response
            return {
                "rationale": f"Unable to process request: {str(e)}",
                "patch": []
            }
    
    def _fallback_plan(self, idea: str, style: StyleTokens) -> PlanJSON:
        """Fallback deterministic plan if OpenAI fails"""
        title = idea.strip().capitalize()
        steps = [
            PlanStep(kind="api", target="backend", summary="Add endpoint"),
            PlanStep(kind="ui", target="frontend", summary="Add view"),
            PlanStep(kind="test", target="repo", summary="Add tests"),
        ]
        
        files = []
        if style.lang in ("ts", "js"):
            route_path = style.routeDir or "apps/api/src/routes"
            file_path = f"{route_path}/endpoint.ts"
            content = f"export default function handler(req, res) {{\n  res.status(200).json({{ ok: true }})\n}}\n"
            files.append(PlanFile(path=file_path, content=content))
        
        return PlanJSON(
            title=title,
            steps=steps,
            files=files,
            risks=["Ensure consistent code style application"],
            tests=["Add unit tests for API handler"],
            prBody=f"## {title}\n\n- Implements: {idea}\n\n### Checklist\n- [ ] API added\n- [ ] UI added\n- [ ] Tests added"
        )
