"""Pydantic models for Blueprint Snap API."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    """A step in the development plan."""
    kind: Literal["code", "test", "config"]
    target: str = Field(..., description="Target file or component")
    summary: str = Field(..., description="Summary of what this step does")


class PlanFile(BaseModel):
    """A file to be created or modified."""
    path: str = Field(..., description="File path relative to project root")
    content: str = Field(..., description="File content")


class PlanJSON(BaseModel):
    """Complete plan structure."""
    title: str = Field(..., description="Plan title")
    steps: List[PlanStep] = Field(..., description="Development steps")
    files: List[PlanFile] = Field(..., description="Files to create/modify")
    risks: List[str] = Field(..., description="Potential risks")
    tests: List[str] = Field(..., description="Test scenarios")
    prBody: str = Field(..., description="Pull request body")


class PlanRequest(BaseModel):
    """Request to create a new plan."""
    idea: str = Field(..., description="One-line idea description")
    projectId: str = Field(..., description="Project identifier")


class PlanResponse(BaseModel):
    """Response containing the generated plan."""
    plan: PlanJSON
    planId: str = Field(..., description="Generated plan ID")


class AskRequest(BaseModel):
    """Request to ask copilot about a plan."""
    planId: str = Field(..., description="Plan ID")
    nodePath: str = Field(..., description="Path to the node in the plan")
    selectionText: str = Field(..., description="Selected text")
    userQuestion: str = Field(..., description="User's question")


class PatchResponse(BaseModel):
    """Response containing rationale and patch operations."""
    rationale: str = Field(..., description="Explanation of the proposed changes")
    patch: List[Dict[str, Any]] = Field(..., description="RFC6902 JSON Patch operations")


class PlanPatchRequest(BaseModel):
    """Request to apply a patch to a plan."""
    planId: str = Field(..., description="Plan ID")
    patch: List[Dict[str, Any]] = Field(..., description="RFC6902 JSON Patch operations")
    messageId: Optional[str] = Field(None, description="Message ID for tracking")


class CursorLinkRequest(BaseModel):
    """Request to generate a Cursor deep link."""
    planId: str = Field(..., description="Plan ID")


class CursorPayload(BaseModel):
    """Payload for Cursor extension."""
    version: int = Field(default=1, description="Payload version")
    projectHint: Optional[str] = Field(None, description="Project hint")
    plan: Dict[str, str] = Field(..., description="Plan title and PR body")
    files: List[Dict[str, str]] = Field(..., description="Files with path and content")
    postActions: Optional[Dict[str, Any]] = Field(None, description="Post-actions to perform")


class CursorLinkResponse(BaseModel):
    """Response containing the Cursor deep link."""
    link: str = Field(..., description="vscode:// deep link URL")


class StyleProfile(BaseModel):
    """Code style profile for a user."""
    user_id: str
    tokens: Dict[str, Any] = Field(..., description="Style tokens (quotes, semis, indent, etc.)")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of style")


class Pattern(BaseModel):
    """Development pattern template."""
    slug: str = Field(..., description="Pattern identifier")
    template: Dict[str, Any] = Field(..., description="Pattern template JSON")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
