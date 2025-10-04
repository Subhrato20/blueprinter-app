from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class StyleTokens(BaseModel):
    lang: Literal["ts", "js", "py"] = "ts"
    indent: Literal["2", "4"] = "2"
    quotes: Literal["single", "double"] = "single"
    semi: bool = False
    tests: Optional[str] = None
    routeDir: Optional[str] = None
    alias: Optional[str] = None


class PlanStep(BaseModel):
    kind: str
    target: str
    summary: str


class PlanFile(BaseModel):
    path: str
    content: str


class PlanJSON(BaseModel):
    title: str
    steps: List[PlanStep] = Field(default_factory=list)
    files: List[PlanFile] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    prBody: str = ""


class PlanCreateRequest(BaseModel):
    project_id: str
    idea: str
    pattern_slug: Optional[str] = None


class AskRequest(BaseModel):
    plan_id: str
    nodePath: str
    selection: Optional[str] = None
    question: str


class PatchOp(BaseModel):
    op: Literal["add", "remove", "replace"]
    path: str
    value: Optional[object] = None


class PlanPatchRequest(BaseModel):
    plan_id: str
    nodePath: str
    patch: List[PatchOp]


class CursorLinkRequest(BaseModel):
    plan_id: str


class PlanRecord(BaseModel):
    id: str
    project_id: str
    plan_json: PlanJSON

