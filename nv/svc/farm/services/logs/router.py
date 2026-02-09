# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Logs Service router."""

from typing import Optional

from fastapi import Path, Query, Response
import pydantic

from nv.svc.core.exceptions import ServicesBaseException
from nv.svc.core import routers

from nv.svc.farm.services.logs.facilities.base import BaseLogStore


router = routers.ServiceAPIRouter()


class AgentTaskLog(pydantic.BaseModel):
    """AgentTaskLog model."""

    agent_id: str = pydantic.Field(..., title="Agent ID", description="Unique agent identifier.")
    task_id: str = pydantic.Field(title="Task ID", description="Unique task identifier.")
    logs: str = pydantic.Field(title="Log", description="Logs of the task.")


@router.get(
    "/status",
    summary="Healthcheck endpoint for logs service.",
    description="Returns 200 and OK if logs service is available.",
)
async def status():
    """Service status endpoint."""
    return "OK"


@router.get(
    "/download/{task_id}",
    summary="Download the log of the given task",
    description="Download the log of the given task so it can be inspected, stored or shared.",
)
async def download_logs(
    task_id: str = Path(..., title="Task ID", description="Unique identifier of the task for which to download the log."),
    agent_id: Optional[str] = Query(None, title="Agent ID", description="Unique identifier of the Agent which executed the given task."),
    log_store: BaseLogStore = router.get_facility("log_store"),
):
    """Download logs endpoint."""
    try:
        log_data = await log_store.get_logs(task_id=task_id, agent_id=agent_id, log_entries=0)
    except KeyError:
        raise ServicesBaseException(status_code=404, detail=f"No logs found for task {task_id}.")

    response = Response(content=log_data["logs"], media_type="text/plain")
    response.headers["Content-Disposition"] = f"attachment; filename={task_id}.txt"
    return response


@router.get(
    "/{task_id}",
    summary="Return the log of the given task",
    description="Return the log produced by the execution of the given task.",
)
async def get_logs(
    task_id: str = Path(..., title="Task ID", description="Unique identifier of the task for which to return the logs."),
    agent_id: str = Query(None, title="Agent ID", description="Unique identifier of the Agent which executed the task."),
    latest_only: bool = Query(True, title="Latest only?",
                              description="In the case where the task ran on multiple agents, only return the log issued by the most recent run."),
    log_store: BaseLogStore = router.get_facility("log_store"),
):
    """Get logs from a task."""
    try:
        return await log_store.get_logs(task_id=task_id, agent_id=agent_id, latest_only=latest_only, log_entries=0)
    except Exception as exc:
        raise ServicesBaseException(
            status_code=404, detail=f"No logs found for task {task_id} on agent {agent_id}: {str(exc)}"
        )


@router.post(
    "/upload",
    summary="Log upload endpoint for Agents",
    description="Endpoint through which Agents can upload the log of the task they are executing.",
)
async def post_logs(
    agent: AgentTaskLog,
    log_store: BaseLogStore = router.get_facility("log_store"),
):
    """Upload logs for a task."""

    return await log_store.set_logs(agent_id=agent.agent_id, task_id=agent.task_id, logs=agent.logs)
