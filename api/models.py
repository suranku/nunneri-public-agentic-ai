"""Pydantic models — single source of truth for DB schema and API shapes."""
from __future__ import annotations

import time
import uuid
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Core run models
# ---------------------------------------------------------------------------

class Thread(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str | None = None
    agent: str | None = None
    model: str | None = None
    last_message: str | None = None
    runs: int = 0
    created_at: float = Field(default_factory=time.time)


class RunNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    node_id: str
    label: str
    phase: int | None = None
    node_type: str = "work"
    status: Literal[
        "pending",
        "active",
        "done",
        "gate-done",
        "waiting_approval",
        "approved",
        "rejected",
        "cancelled",
        "error",
    ] = "pending"
    output: str | None = None
    entered_at: float | None = None
    exited_at: float | None = None


class Run(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str | None = None
    project_id: str | None = None
    agent: str
    kind: Literal["agent", "command"]
    model: str
    project_path: str | None = None
    message: str
    system_prompt: str | None = None
    output: str | None = None
    error_detail: str | None = None
    status: Literal["running", "waiting_approval", "done", "rejected", "cancelled", "error"] = "running"
    duration_s: float | None = None
    started_at: float = Field(default_factory=time.time)
    nodes: list[RunNode] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Multi-tenant hierarchy
# ---------------------------------------------------------------------------

RbacRole = Literal["admin", "owner", "member", "viewer"]

ROLE_RANK: dict[str, int] = {"viewer": 0, "member": 1, "owner": 2, "admin": 3}


class Org(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    created_at: float = Field(default_factory=time.time)


class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str
    name: str
    slug: str
    created_at: float = Field(default_factory=time.time)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    org_id: str
    name: str
    slug: str
    description: str | None = None
    created_at: float = Field(default_factory=time.time)


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sub: str           # OIDC subject identifier (unique per provider)
    email: str
    name: str | None = None
    picture: str | None = None
    created_at: float = Field(default_factory=time.time)


class RoutingRule(BaseModel):
    condition: Literal["contains", "starts_with", "ends_with", "regex", "always"] = "contains"
    value: str = ""           # text / pattern to match against node output
    target_node: str = ""    # node_id to route to when condition matches
    priority: int = 0         # lower = evaluated first


class NodeConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    node_id: str
    label: str | None = None
    system_prompt: str | None = None         # overrides agent-level prompt for this node
    routing_rules: list[RoutingRule] = Field(default_factory=list)
    classification_labels: list[str] = Field(default_factory=list)
    notes: str | None = None
    updated_at: float = Field(default_factory=time.time)


class Membership(BaseModel):
    """Unified membership row covering org / team / project scopes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scope_type: Literal["org", "team", "project"]
    scope_id: str
    user_id: str
    role: RbacRole = "member"
    created_at: float = Field(default_factory=time.time)
