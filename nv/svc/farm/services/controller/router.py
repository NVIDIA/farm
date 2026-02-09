# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Service router."""

import pydantic

from typing import Optional

from nv.svc.farm.services.tasks.utils import status_utils

from nv.svc.core import routers
from nv.svc.core.exceptions import ServicesBaseException

router = routers.ServiceAPIRouter()

# flake8: noqa: D103 Missing docstring in public function

class TaskModel(pydantic.BaseModel):
    """Task."""

    task_id: str = pydantic.Field(..., title="Task ID", description="Unique identifier of the task")
    status: str = pydantic.Field("", title="Task Status", description="Status of task")
    comment: str = pydantic.Field("", title="Additional data", description="Used for example for error messages")
    metrics: str = pydantic.Field("", title="Task metrics", description="Task progress metrics")


class TaskAgentModel(pydantic.BaseModel):
    """Task agent."""

    task_id: str = pydantic.Field(
        ...,
        title="Task ID",
        description="Unique identifier of the task"
    )
    agent_name: str = pydantic.Field(
        ...,
        title="Agent name",
        description="Name of agent that picked up the task",
    )


class TaskCheckinModel(TaskModel):
    """Task checkin information."""

    current_step_index: Optional[int] = pydantic.Field(
        None,
        title="Current step index",
        description="Index of the current step in the overall progress",
        ge=0,
    )
    total_step_count: Optional[int] = pydantic.Field(
        None,
        title="Total steps count",
        description="Overall number of steps in the progress",
        ge=0,
    )
    progress: Optional[float] = pydantic.Field(
        None,
        title="Progress completion",
        description="Overall progress completion of the task (between 0.0 and 1.0)",
        ge=0.0,
        le=1.0,
    )
    status_message: Optional[str] = pydantic.Field(
        None,
        title="Progress status message",
        description="Status message providing additional information about the current progress of the task",
    )
    time_remaining: Optional[float] = pydantic.Field(
        None,
        title="Estimated time remaining",
        description="Estimated time remaining in seconds"
    )


class TaskStatisticsModel(TaskModel):
    """Task statistics."""

    num_gpus: int = pydantic.Field(
        0,
        title="Number of GPU's used",
        description="Number of GPU's ran on the task",
        ge=0,
    )
    duration: float = pydantic.Field(
        0.0,
        title="Execution duration",
        description="Amount of time spent on executing the task",
        ge=0.0,
    )
    avg_gpu_utilization: float = pydantic.Field(
        0.0,
        title="Average GPU utilization",
        description="Average GPU utilization as a percentage of the total capacity",
        ge=0.0,
    )
    max_gpu_utilization: float = pydantic.Field(
        0.0,
        title="Max GPU utilization",
        description="Maximum GPU utilization as a percentage of the total capacity",
        ge=0.0,
    )
    avg_memory: float = pydantic.Field(
        0.0,
        title="Average memory utilization",
        description="Average amount of memory used in Mb",
        ge=0.0,
    )
    max_memory: float = pydantic.Field(
        0.0,
        title="Max memory utilization",
        description="Maximum amount of memory used in Mb",
        ge=0.0,
    )


@router.get(
    "/status",
    summary="Healthcheck endpoint for jobs service.",
    description="Returns 200 and OK if jobs service is available.",
)
async def status():
    """Service status endpoint."""
    return "OK"


@router.get("/task/retrieve")
async def get_task(task_id: str, task_manager=router.get_facility("task_manager")):
    try:
        return await task_manager.get_task(task_id=task_id)
    except KeyError:
        raise ServicesBaseException(status_code=404, detail="Task does not exist.")


@router.post("/task/started")
async def started(task: TaskAgentModel, task_manager=router.get_facility("task_manager")):
    try:
        await task_manager.set_task_started(task_id=task.task_id)
    except KeyError:
        raise ServicesBaseException(status_code=404, detail="Task does not exist.")


@router.post("/task/finished")
async def finished(task: TaskStatisticsModel, task_manager=router.get_facility("task_manager")):
    try:
        await task_manager.set_task_finished(task_id=task.task_id)

    except KeyError:
        raise ServicesBaseException(status_code=404, detail="Task does not exist.")


@router.post("/task/errored")
async def errored(task: TaskModel, task_manager=router.get_facility("task_manager")):
    try:
        await task_manager.set_task_errored(task_id=task.task_id, reason=task.comment)
    except KeyError:
        raise ServicesBaseException(status_code=404, detail="Task does not exist.")


@router.post("/task/checkin")
async def checkin(task: TaskCheckinModel, task_manager=router.get_facility("task_manager")):
    try:
        progress = None
        if task.progress is not None or (task.current_step_index is not None and task.total_step_count is not None):
            progress = {
                "current_step_index": task.current_step_index,
                "total_step_count": task.total_step_count,
                "progress": task.progress,
                "status_message": task.status_message,
                "time_remaining": task.time_remaining,
            }

        await task_manager.task_checkin(
            task_id=task.task_id,
            status=task.status,
            reason=task.comment,
            metrics=task.metrics,
            progress=progress,
        )
    except status_utils.StatusTransitionException as e:
        raise ServicesBaseException(status_code=400, detail=str(e))
    except KeyError:
        raise ServicesBaseException(status_code=404, detail="Task does not exist.")


@router.get("/task/logs")
async def logs(task_id: str, task_manager=router.get_facility("task_manager")):
    try:
        return await task_manager.get_logs(task_id=task_id)
    except Exception as exc:
        raise ServicesBaseException(
            status_code=404, detail=f"No logs found for task ID {task_id}: {str(exc)}"
        )
