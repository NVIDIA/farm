# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Agents service router."""

import enum
from typing import Dict, List, Optional
import pydantic

from fastapi import Query

from nv.svc.core import routers, exceptions

from nv.svc.farm.services.agents.facilities.managers.base import BaseAgentManager


router = routers.ServiceAPIRouter()


class AgentStatus(str, enum.Enum):
    """AgentStatus used in farm."""

    active = "active"
    idle = "idle"
    lost = "lost"
    evicted = "evicted"


class AgentModel(pydantic.BaseModel):
    """AgentModel for specifying agent data."""

    agent_id: str = pydantic.Field(..., title="Agent ID", description="Unique agent identifier.")
    task_types: List = pydantic.Field([], title="Available task types", description="List of tasks the agent can handle.")
    active_tasks: List = pydantic.Field([], title="Active tasks", description="List of active tasks.")
    resources: Dict = pydantic.Field({}, title="Available resources", description="List of available resources.")
    errored_task_count: int = pydantic.Field(None, title="Accumulated errors", description="Accumulated amount of errored tasks on this agent.")
    labels: List = pydantic.Field([], title="Agent labels", description="List of labels associated with the agent.")


class AgentTaskLog(AgentModel):
    """AgentTaskLog for specifying agent logs."""

    agent_id: str = pydantic.Field(..., title="Agent ID", description="Unique agent identifier.")
    task_id: str = pydantic.Field(title="Task ID", description="Unique task identifier.")
    logs: str = pydantic.Field(title="Log", description="Logs of the task.")


@router.get(
    "/list",
    summary="Return the list of connected Agents",
    description="Return the list of Agents which have connected to the Queue.",
)
async def list_agents(
    status: Optional[AgentStatus] = Query(None, title="Agent status", description="Status of the Agent by which to filter the search query."),
    agent_manager: BaseAgentManager = router.get_facility("agent_manager"),
):
    """List of connected agents to the farm queue."""
    if isinstance(status, AgentStatus):
        status = status.value
    return await agent_manager.list(status=status)


@router.post(
    "/checkin",
    summary="Checkin endpoint for Agents",
    description="Endpoint through which Agents can perform checkins at regular intervals to inform the Queue about their status.",
)
async def checkin(
    agent: AgentModel,
    agent_manager: BaseAgentManager = router.get_facility("agent_manager"),
):
    """Checkin endpoint for the farm agents."""

    return await agent_manager.update(
        agent.agent_id,
        active_tasks=agent.active_tasks,
        task_types=agent.task_types,
        resources=agent.resources,
        errored_task_count=agent.errored_task_count,
        labels=agent.labels
    )


@router.post(
    "/remove",
    summary="Remove the given Agent",
    description="Remove the given Agent from the pool of available Agents.",
)
async def remove(
    agent: AgentModel,
    agent_manager: BaseAgentManager = router.get_facility("agent_manager"),
):
    """Remove the given agent from the farm."""

    agents = await agent_manager.list()

    if agent.agent_id not in agents:
        raise exceptions.ServicesBaseException(status_code=404, detail="Agent does not exist.")

    # Use the retrieved agent model with the latest
    # snapshot of tasks associated with the agent.
    found_agent = agents[agent.agent_id]
    active_tasks = found_agent.get("active_tasks", {})

    return await agent_manager.remove(agent.agent_id, active_tasks=active_tasks)


@router.post(
    "/evict",
    summary="Evict the given Agent",
    description="Evicting an agent will prevent it from taking on new work.",
)
async def evict(
    agent: AgentModel,
    agent_manager: BaseAgentManager = router.get_facility("agent_manager"),
):
    """Evict an endpoint from farm."""
    return await agent_manager.evict(agent.agent_id)


@router.post(
    "/enable",
    summary="Enable the given Agent",
    description="Enabling an agent will allow it to take on new work after an eviction.",
)
async def enable(
    agent: AgentModel,
    agent_manager: BaseAgentManager = router.get_facility("agent_manager"),
):
    """Enable an agent on the farm."""
    return await agent_manager.enable(agent.agent_id)


@router.get(
    "/status",
    summary="Healthcheck endpoint for agents service.",
    description="Returns 200 and OK if agents service is available.",
)
async def status():
    """Agents service status endpoint."""
    return "OK"
