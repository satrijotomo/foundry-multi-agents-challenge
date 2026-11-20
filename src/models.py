from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    selected_agents: list[str] = Field(default_factory=list)
    reason: str


class AgentFinding(BaseModel):
    agent_key: str
    agent_name: str
    output: str
    evidence: dict[str, Any]
    duration_ms: int


class RunResult(BaseModel):
    question: str
    routing_mode: str
    route: RouteDecision
    findings: list[AgentFinding]
    final_answer: str
    trace_file: str | None = None
