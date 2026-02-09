# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Tasks service router."""

from typing import Any, AnyStr, Dict, List, Optional
import asyncio
from uuid import UUID, uuid4
import logging

from fastapi import Query, Path, Request

import pydantic
from pydantic import field_validator


from nv.svc.core import routers

from nv.svc.farm.services.tasks.config import FarmTasksConfig
from nv.svc.farm.services.tasks.facilities.tasks.backends import InvalidTaskFieldException
from nv.svc.farm.services.tasks.facilities.tasks import store
from nv.svc.farm.services.tasks.utils import status_utils
from nv.svc.farm.utils import post_data, delete_request, FarmServicesBaseException


router = routers.ServiceAPIRouter()


DEFAULT_TASK_PRIORITY = 65535
"""Default priority for tasks, if no value was supplied."""


class TaskProgressModel(pydantic.BaseModel):
    """Task progress information."""

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
        None, title="Estimated time remaining", description="Estimated time remaining in seconds"
    )


class BaseTaskModel(pydantic.BaseModel):
    """Base model for task properties."""

    task_type: str = pydantic.Field(..., max_length=512, title="Task type", description="The type of task to execute")
    task_args: Dict = pydantic.Field(..., title="Task arguments", description="Arguments to be passed to the task")
    task_function: str = pydantic.Field("", max_length=128, title="Function", description="The function to execute within the task")
    task_function_args: Dict = pydantic.Field(dict(), title="Function arguments", description="Arguments to supply to the task function")
    task_requirements: Dict = pydantic.Field(dict(), title="Task requirements", description="Indiquate memory, CPU and GPU requirements")
    task_comment: str = pydantic.Field("", title="Comment", description="User comments regarding the submitted task")
    priority: int = pydantic.Field(DEFAULT_TASK_PRIORITY, title="Task priority", description="Task priority. 0 is the highest priority.")
    metadata: Dict[str, Any] = pydantic.Field(None, title="Task metadata", description="Task metadata (ie: list of extensions, registries etc)")
    status: Optional[status_utils.Status] = pydantic.Field(None, title="Task status", description="Status of the task, submitted if not set.")
    labels: List[str] = pydantic.Field(None, title="Task labels", description="Task labels to steer tasks to specific controllers")


class TaskSubmissionModel(BaseTaskModel):
    """Request model for task submission."""

    task_id: Optional[UUID] = pydantic.Field(
        default_factory=uuid4,
        title="Task ID",
        description="Unique identifier for the task, auto-generated if not provided"
    )
    user: str = pydantic.Field(..., title="User name", max_length=2048, description="Name of the user that submitted the task")


class TaskGraphNode(pydantic.BaseModel):
    """Node in a task graph."""

    task: BaseTaskModel = pydantic.Field(..., title="Task", description="Task definition")
    depends_on: List[str] = pydantic.Field(
        default_factory=list,
        title="Dependencies",
        description="List of task names that must complete before this task can start",
    )
    name: str = pydantic.Field(..., title="Node name", description="Name of the node in the graph")


class TaskGraphSubmission(pydantic.BaseModel):
    """Model for submitting a task graph."""

    user: str = pydantic.Field(
        ...,
        title="User name",
        max_length=2048,
        description="Name of the user that submitted the task"
    )
    name: str = pydantic.Field(
        ...,
        title="DAG name",
        max_length=255,
        description="Name for the DAG (for display purposes)"
    )
    nodes: List[TaskGraphNode] = pydantic.Field(
        ...,
        title="Graph Nodes",
        description="List of tasks and their dependencies forming the graph"
    )

    @field_validator("nodes")
    @classmethod
    def validate_dependencies(cls, nodes):
        """Ensure all dependency references are valid."""
        node_names = {node.name for node in nodes}
        duplicates = len(node_names) != len(nodes)

        if duplicates:
            raise ValueError(f"Duplicate node names found: {duplicates}")

        for node in nodes:
            invalid_deps = [dep for dep in node.depends_on if dep not in node_names]
            if invalid_deps:
                raise ValueError(f"Invalid dependencies for node {node.name}: {invalid_deps}")
        return nodes


class TaskGraphSubmissionResponse(pydantic.BaseModel):
    """Response model for task graph submission."""

    dag_id: UUID = pydantic.Field(..., title="DAG ID", description="ID of the created DAG")
    task_ids: List[UUID] = pydantic.Field(..., title="Task IDs", description="List of created task IDs in order of submission")


class TaskRevisionHistoryResponseModel(pydantic.BaseModel):
    """Response model for task revision history."""

    task_id: str = pydantic.Field(..., title="Task ID", description="Unique identifier for the task")
    status: status_utils.Status = pydantic.Field(..., title="Task status", description="Status of the task")
    user_id: str = pydantic.Field(None, title="User ID", description="Unique identifier of the User which updated the task")
    agent_id: Optional[str] = pydantic.Field(None, title="Agent ID", description="Unique identifier of the Agent which updated the task")
    details: Optional[str] = pydantic.Field(None, title="Details", description="Details about the event")
    progress: Optional[TaskProgressModel] = None
    time: float = pydantic.Field(0.0, title="Timestamp", description="Unix timestamp of the event")


class TaskSubmissionResponseModel(pydantic.BaseModel):
    """Response model for task submission."""

    task_id: str = pydantic.Field(..., title="Task ID", description="Unique identifier for the task")


class TaskIdModel(pydantic.BaseModel):
    """Task ID model."""

    task_id: str = pydantic.Field(..., max_length=36, title="Task ID", description="Unique identifier for the task")
    task_type: str = pydantic.Field(..., max_length=512, title="Task type", description="The type of task to execute")
    task_function: str = pydantic.Field("", max_length=128, title="Function", description="The function to execute within the task")
    task_function_args: Dict[str, Any] = pydantic.Field(dict(), title="Function arguments", description="Arguments to supply to the task function.")
    status: status_utils.Status = pydantic.Field(..., title="Task status", description="Status of the task")
    agent_id: Optional[str] = pydantic.Field(None, max_length=2048, title="Agent ID", description="Unique identifier of the Agent which updated the task")
    task_comment: str = pydantic.Field("", title="Comment", description="User comments regarding the submitted task")
    metrics: str = pydantic.Field("", title="Task metrics", description="Any prometheus formatted metrics that might have been collected during the execution.")
    priority: int = pydantic.Field(None, title="Task priority", description="Task priority. 0 is the highest priority.")
    metadata: Dict[str, Any] = pydantic.Field(None, title="Task metadata", description="Task metadata (ie: list of extensions, registries etc)")
    labels: Optional[List[str]] = pydantic.Field(None, title="Task labels", description="Task labels to steer tasks to specific controllers")


class TaskUpdateModel(TaskIdModel):
    """Task update information."""

    task_type: Optional[str] = pydantic.Field(None, max_length=512, title="Task type", description="Type of the task to update")
    task_function: Optional[str] = pydantic.Field(None, max_length=128, title="Task function", description="Function of the task to update")
    userid: Optional[str] = pydantic.Field(None, max_length=2048, title="User ID", description="Unique identifier of the User who updated the task")
    status: Optional[str] = pydantic.Field(None, title="Status", description="New status for the task")
    agent_id: Optional[str] = pydantic.Field(None, max_length=2048, title="Agent ID", description="ID of the agent processing the task")
    details: Optional[str] = pydantic.Field(None, title="Details", description="Details about the event")
    metrics: Optional[str] = pydantic.Field(None, title="Metrics", description="Metrics to be collected for the task")
    metadata: Optional[Dict[str, Any]] = pydantic.Field(None, title="Metadata", description="Additional metadata for the task")
    labels: Optional[List[str]] = pydantic.Field(None, title="Labels", description="Labels associated with the task")
    progress: Optional[TaskProgressModel] = None


class TaskArchiveRequestModel(pydantic.BaseModel):
    """Request model for archiving tasks."""

    task_ids: List[str] = pydantic.Field([], title="Task IDs", description="List of unique identifiers of tasks to archive")


class TaskArchiveResponseModel(pydantic.BaseModel):
    """Respone model for archiving tasks."""

    archived_tasks_count: int = pydantic.Field(..., title="Archived tasks count", description="Number of tasks archived", ge=0)
    error_count: int = pydantic.Field(..., title="Error count", description="Number of exceptions raised during the archival", ge=0)
    error_details: List[str] = pydantic.Field(..., title="Erro details", description="Details of exceptions raised during the archival")


class TaskRequestModel(pydantic.BaseModel):
    """Task request model."""

    task_types: List = pydantic.Field(..., title="Task types", description="A list of task types an agent requesting work is able to process")
    capacity: Dict = pydantic.Field({}, title="Agent capacity", description="CPU, GPU and RAM availability.")
    agent_id: AnyStr = pydantic.Field(..., title="Agent ID", description="Unique identifier for the agent requesting the tasks.")
    labels: List[str] = pydantic.Field([], title="Task label filtering", description="Labels by which to further filter tasks")


class TaskDispatchModel(pydantic.BaseModel):
    """Returned as part of the fetch call."""

    task_id: str
    task_type: str
    task_args: Dict
    task_function: str
    task_function_args: Dict
    task_requirements: Dict
    userid: str
    status: status_utils.Status
    task_submission_time: float
    priority: int
    metadata: Dict
    labels: List[str]


class TaskUpdateResponseModel(pydantic.BaseModel):
    """Returned after a task update event."""

    should_cancel: bool = pydantic.Field(
        ...,
        title="Cancel task",
        description=(
            "Returns True if a task has been cancelled in the queue. "
            "It will indicate to the agent to interrupt the task."
        )
    )


# # NOTE: Commented out as unused. This further prevents legitimate Users from attempting to use this method expecting
# # to receive information about the available task types.
#
# @router.get("/list-types")
# async def list_task_types(
#     task_store: store.TaskStore = router.get_facility("task_store"),
# ):
#     return []


class TaskRevisionTailResponseModel(pydantic.BaseModel):
    """Returned when an the final task-revision index is requested."""

    revision_id: Optional[int] = pydantic.Field(None, title="Revision ID", description="Unique identifier of the task revision")


class TaskChangeRequestModel(pydantic.BaseModel):
    """A starting and ending revision_id that will be used to bound a set of revision and extract the unique list of tasks that have changed."""

    after: int = pydantic.Field(None, title="After ID", description="The lower bound for selecting revision_ids.")
    ending_with: int = pydantic.Field(None, title="Ending With ID", description="The upper bound for selecting revision_ids.")


class TaskChangeResponseModel(pydantic.BaseModel):
    """Return a list of changed tasks given a range of task-revisions."""

    task_ids: List[str] = pydantic.Field([], title="Task IDs", description="List of unique identifiers of tasks that have changed.")


class BulkUpdateRequestModel(pydantic.BaseModel):
    """Request model for bulk updating task."""

    task_ids: List[str] = pydantic.Field([], title="Task IDs", description="List of unique identifiers for updating task status")


class BulkUpdateErrorModel(pydantic.BaseModel):
    """Model for bulk update errors."""

    task_id: str = pydantic.Field(..., title="Task ID", description="ID of the task that failed")
    error: str = pydantic.Field(..., title="Error", description="Error message explaining the failure")


class BulkUpdateResponseModel(pydantic.BaseModel):
    """Response model for bulk task update."""

    updated_task_count: int = pydantic.Field(..., title="Updated tasks count", description="Number of tasks updated", ge=0)
    errors: List[BulkUpdateErrorModel] = pydantic.Field([], title="Errors", description="Details of failed operations")


class BulkUpdateStatusRequestModel(BulkUpdateRequestModel):
    """Request model for bulk updating task status."""

    status: status_utils.Status = pydantic.Field(
        ..., title="Status", description="The new status to apply to the specified tasks"
    )
    userid: str = pydantic.Field(
        ..., title="User ID", description="ID of the user performing the bulk update"
    )


@router.get(
    "/list",
    summary="Return the tasks matching the given search criteria",
    description="Return metadata information about the tasks matching the given search criteria.",
)
async def list(
    request: Request,
    task_type: Optional[str] = Query(None, title="Task type", description="The type of tasks to return."),
    task_function: Optional[str] = Query(None, title="Task function", description="The function of tasks to return."),
    status: List[status_utils.Status] = Query(None, title="Task statuses", description="List of matching task statuses to return."),
    task_store: store.TaskStore = router.get_facility("task_store"),
    field: Optional[List[str]] = Query(
        None,
        title="Task fields",
        description="If provided, will only return the minimum set of fields and the requested fields."
    )
):
    """Return tasks marching the given search criteria."""
    try:
        tasks = await task_store.get_tasks(
            task_type=task_type,
            task_function=task_function,
            statuses=status,
            fields=field
        )
    except InvalidTaskFieldException as exception:
        raise FarmServicesBaseException(status_code=400, detail=str(exception), request=request)

    # TODO: Update the format of the response to only include a flat list of tasks, instead of the
    # ``(task_type, task_function)`` mapping inherited from the in-memory database storage:
    serializable_data = {}
    for task in tasks:
        task_pair = str((task["task_type"], task["task_function"]))
        if task_pair in serializable_data:
            serializable_data[task_pair].append(task)
        else:
            serializable_data[task_pair] = [task]

    return serializable_data


@router.get(
    "/info/{task_id}",
    summary="Return information about the given task",
    description="Return metadata information about the given task.",
)
async def info_task(
    request: Request,
    task_id: str = Path(..., title="Task ID", description="Unique identifier for the task."),
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Return information about the given task."""
    try:
        return await task_store.get_task(task_id=task_id)
    except KeyError:
        raise FarmServicesBaseException(status_code=404, detail="Task does not exist.", request=request)


@router.get(
    "/revision-history/{task_id}",
    response_model=List[TaskRevisionHistoryResponseModel],
    summary="Return the revision history of the given task",
    description="Return the list of revisions recorded for the given task.",
)
async def revision_history(
    request: Request,
    task_id: str = Path(..., title="Task ID", description="Unique identifier for the task."),
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Return the revision history of the given task."""
    try:
        revision_history = await task_store.get_task_revision_history(task_id=task_id)
        response_models = []
        for revision in revision_history:
            response_models.append(
                TaskRevisionHistoryResponseModel(
                    task_id=revision.task_id,
                    status=revision.status,
                    user_id=revision.user_id,
                    agent_id=revision.agent_id,
                    details=revision.details,
                    progress=revision.progress,
                    time=revision.time,
                )
            )
        return response_models
    except KeyError:
        raise FarmServicesBaseException(status_code=404, detail=f"No task found with ID \"{task_id}\".", request=request)


@router.post(
    "/submit",
    response_model=TaskSubmissionResponseModel,
    summary="Submit the given task payload to the Queue",
    description="Submit the given task payload to the Queue, so an Agent can process it.",
)
async def submit_task(
    data: TaskSubmissionModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Submit the given task to the queue."""
    metadata = data.metadata or {}
    metadata["original_submitter"] = data.user

    task_id = await task_store.add_task(
        userid=data.user,
        task_type=data.task_type,
        task_args=data.task_args,
        task_function=data.task_function,
        task_function_args=data.task_function_args,
        task_requirements=data.task_requirements,
        task_comment=data.task_comment,
        priority=data.priority,
        metadata=metadata,
        status=data.status,
        labels=data.labels
    )

    return TaskSubmissionResponseModel(task_id=task_id)


@router.post(
    "/update",
    response_model=TaskUpdateResponseModel,
    summary="Update the given task",
    description="Update the given task using the provided information payload.",
)
async def update_status(
    data: TaskUpdateModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Update the given task."""
    progress = None
    if data.progress:
        progress = {
            "current_step_index": data.progress.current_step_index,
            "total_step_count": data.progress.total_step_count,
            "progress": data.progress.progress,
            "status_message": data.progress.status_message,
            "time_remaining": data.progress.time_remaining,
        }
    should_cancel = False
    try:
        await task_store.update_status(
            task_id=data.task_id,
            task_type=data.task_type,
            task_function=data.task_function,
            status=data.status,
            userid=data.userid,
            details=data.details,
            metrics=data.metrics,
            progress=progress,
            agent_id=data.agent_id,
            task_comment=data.task_comment,
            task_function_args=data.task_function_args,
            priority=data.priority,
            metadata=data.metadata,
            labels=data.labels
        )
    except status_utils.StatusTransitionException as e:
        logging.error(f"Status transition exception: {e}, task_id: {data.task_id}")
        should_cancel = status_utils.is_invalid_resume_transition(e.current_status, e.next_status)

    return TaskUpdateResponseModel(should_cancel=should_cancel)


@router.post(
    "/archive",
    response_model=TaskArchiveResponseModel,
    summary="Archive the given tasks",
    description=f"Archive the given tasks, if their status is either {', '.join(status_utils.get_prev_status_list(status_utils.Status.archived))}.",
)
async def archive_task(
    data: TaskArchiveRequestModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Archive the given task."""
    archived_tasks_count = 0
    error_details: List[str] = []

    for task_id in data.task_ids:
        try:
            await task_store.archive_task(task_id=task_id)
            archived_tasks_count += 1
        except Exception as exc:
            error_details.append(str(exc))

    return TaskArchiveResponseModel(
        archived_tasks_count=archived_tasks_count,
        error_count=len(error_details),
        error_details=error_details,
    )


@router.post(
    "/cancel",
    summary="Cancel the given task",
    description="Cancel the given running task.",
)
async def cancel_task(
    data: TaskUpdateModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Cancel the given task."""
    await task_store.update_status(
        task_id=data.task_id,
        task_type=data.task_type,
        task_function=data.task_function,
        status=status_utils.Status.cancelling,
        userid=data.userid,
        details="Cancelling task at the User's request.",
        # metrics=None,
        agent_id=data.agent_id,
        labels=data.labels
    )


@router.post(
    "/retry",
    summary="Retry the given task",
    description="Resubmit the given task, so it can be processed once again by an Agent.",
)
async def retry_task(
    data: TaskUpdateModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Retry the given task."""
    await task_store.update_status(
        task_id=data.task_id,
        task_type=data.task_type,
        task_function=data.task_function,
        status=status_utils.Status.submitted,
        userid=data.userid,
        details=data.details or "Restarting task at the User's request.",
        # metrics=None,
        agent_id=data.agent_id,
        metadata=data.metadata,
        labels=data.labels
    )


@router.post(
    "/fetch",
    response_model=Optional[TaskDispatchModel],
    summary="Provide an Agent with a task to process",
    description="Return the next available task that an Agent should process.",
)
async def fetch(
    data: TaskRequestModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Provide an Agent with a task to process."""
    selected_task, task_type, task_function = await task_store.get_next_task(
        data.task_types,
        data.capacity,
        data.agent_id,
        labels=data.labels
    )

    if not selected_task:
        return None

    dispatch_model = TaskDispatchModel(
        task_id=selected_task["task_id"],
        task_type=task_type,
        task_function=task_function,
        task_args=selected_task["task_args"],
        task_function_args=selected_task["task_function_args"],
        userid=selected_task["userid"],
        status=selected_task["status"],
        priority=selected_task.get("priority", DEFAULT_TASK_PRIORITY),
        task_requirements=selected_task.get("task_requirements", {}),
        task_submission_time=selected_task.get("task_submission_time", 0),
        metadata=selected_task.get("metadata", {}),
        labels=selected_task.get("labels", [])
    )

    return dispatch_model


@router.get(
    "/status",
    summary="Healthcheck endpoint for status service.",
    description="Returns 200 and OK if status service is available.",
)
async def status():
    """Tasks service status endpoint."""
    return "OK"


@router.get(
    "/revision-highest",
    response_model=TaskRevisionTailResponseModel,
    summary="Return the highest global task revision",
    description="Returns the index of the highest (most recent) task revision stored in the task revision store.",
)
async def revision_highest(
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Return the highest global task revision."""
    revision_id = await task_store.get_highest_task_revision()
    return TaskRevisionTailResponseModel(revision_id=revision_id)


@router.post(
    "/changed-between-revisions",
    response_model=TaskChangeResponseModel,
    summary="Return a list of tasks IDs that have changed between the provided list of revisions",
    description="Returns a unique list of tasks that have changed over a contiguous span of revision bound by the input arguments.",
)
async def changes(
    data: TaskChangeRequestModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Return a list of tasks IDs that have changed between the provided list of revisions."""
    task_ids: List[str] = await task_store.get_changed_tasks_between_revisions(after=data.after, ending_with=data.ending_with)
    return TaskChangeResponseModel(task_ids=task_ids)


@router.post("/bulk-status", response_model=BulkUpdateResponseModel)
async def bulk_status(
    data: BulkUpdateStatusRequestModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Perform bulk actions (cancel/retry/archive) on multiple tasks in parallel."""
    results = await asyncio.gather(*[
        task_store.process_bulk_status_update(
            task_id=task_id,
            status=data.status,
            userid=data.userid,
            details=f"Updating task status to {data.status.value} via bulk update"
        ) for task_id in data.task_ids])

    errors = [
        BulkUpdateErrorModel(task_id=r["task_id"], error=r["error"])
        for r in results
        if r["status"] == "error"
    ]

    return BulkUpdateResponseModel(
        updated_task_count=len(results) - len(errors),
        errors=errors
    )


async def _cleanup_tasks(task_store: store.TaskStore, task_ids: List[str]) -> None:
    """Clean up tasks after a failure.

    Args:
        task_store: Task store to use for cleanup
        task_ids: List of task IDs to clean up
    """
    for task_id in task_ids:
        try:
            # Set tasks to cancelled state
            await task_store.update_status(
                task_id=task_id,
                status=status_utils.Status.cancelled,
                userid="system",
                details="Cancelled due to graph submission failure",
            )
        except Exception:
            # Log but continue with other tasks
            logging.error(f"Failed to cleanup task {task_id}")


@router.post(
    "/submit-graph",
    response_model=TaskGraphSubmissionResponse,
    summary="Submit a task dependency graph",
    description="Submit multiple tasks with their dependencies as a directed acyclic graph (DAG).",
)
async def submit_task_graph(
    request: Request,
    data: TaskGraphSubmission,
    task_store: store.TaskStore = router.get_facility("task_store"),
    config: FarmTasksConfig = router.get_facility("config"),
):
    """Submit a task dependency graph.

    This endpoint:
    1. Validates the graph structure with the DAG service
    2. Creates all tasks with the DAG ID in their metadata
    3. Rolls back on failure
    """
    # Get DAG service URL from config
    dag_service_url = config.tasks.dag_service_url.rstrip("/")
    if not dag_service_url:
        raise FarmServicesBaseException(
            status_code=500,
            detail="DAG service URL not configured",
            request=request
        )

    # Create map of node names to UUIDs
    name_to_uuid = {node.name: uuid4() for node in data.nodes}

    # Build edges from dependencies
    edges = []
    for node in data.nodes:
        for dep in node.depends_on:
            edges.append({"source_task_id": str(name_to_uuid[dep]), "target_task_id": str(name_to_uuid[node.name])})

    # Submit to DAG service first to validate the graph
    try:
        dag_request = {
            "edges": edges,
            "name": data.name
        }
        dag_response = await post_data(f"{dag_service_url}/submit", data=dag_request)
        dag_id = UUID(dag_response["dag_id"])
    except Exception as e:
        raise FarmServicesBaseException(
            status_code=500,
            detail=f"Failed to validate graph with DAG service: {str(e)}",
            request=request
        )

    # Now create all tasks with the DAG ID in metadata
    created_task_ids = []
    try:
        for node in data.nodes:
            # Add DAG ID to task metadata
            status = status_utils.Status.unscheduled if node.depends_on else status_utils.Status.submitted
            metadata = node.task.metadata or {}
            dag_metadata = metadata.get("dag", {})
            dag_metadata["id"] = str(dag_id)
            dag_metadata["name"] = node.name
            metadata["dag"] = dag_metadata

            task_id = await task_store.add_task(
                task_id=str(name_to_uuid[node.name]),
                userid=data.user,
                task_type=node.task.task_type,
                task_args=node.task.task_args,
                task_function=node.task.task_function,
                task_function_args=node.task.task_function_args,
                task_requirements=node.task.task_requirements,
                task_comment=node.task.task_comment,
                priority=node.task.priority,
                metadata=metadata,
                status=status,
                labels=node.task.labels,
            )
            created_task_ids.append(task_id)
    except Exception as e:
        # Clean up any tasks we created
        await _cleanup_tasks(task_store, created_task_ids)

        # Delete the DAG
        try:
            await delete_request(f"{dag_service_url}/{dag_id}")
        except Exception as dag_e:
            logging.error(f"Failed to delete DAG {dag_id} after task creation failure: {str(dag_e)}")

        raise FarmServicesBaseException(
            status_code=500,
            detail=f"Failed to create tasks: {str(e)}",
            request=request
        )

    return TaskGraphSubmissionResponse(
        dag_id=dag_id,
        task_ids=[UUID(tid) for tid in created_task_ids]
    )


class TaskBulkInfoRequestModel(pydantic.BaseModel):
    """Request model for bulk task info retrieval."""

    task_ids: List[str] = pydantic.Field(..., title="Task IDs", description="List of unique identifiers of tasks to retrieve")
    statuses: Optional[List[status_utils.Status]] = pydantic.Field(None, title="Task statuses", description="Optional list of statuses to filter by")


class TaskBulkInfoResponseModel(pydantic.BaseModel):
    """Response model for bulk task info retrieval."""

    tasks: Dict[str, Dict[str, Any]] = pydantic.Field(..., title="Tasks", description="Map of task ID to task info")
    not_found: List[str] = pydantic.Field(..., title="Not found", description="List of task IDs that were not found")


class TaskBulkStatusUpdateRequestModel(pydantic.BaseModel):
    """Request model for bulk task status update."""

    task_ids: List[str] = pydantic.Field(..., title="Task IDs", description="List of unique identifiers of tasks to update")
    status: status_utils.Status = pydantic.Field(..., title="New status", description="The new status to set for all tasks")


class TaskBulkStatusUpdateResponseModel(pydantic.BaseModel):
    """Response model for bulk task status update."""

    updated_task_ids: List[str] = pydantic.Field(..., title="Updated task IDs", description="List of task IDs that were successfully updated")


@router.post(
    "/update/bulk",
    response_model=TaskBulkStatusUpdateResponseModel,
    summary="Update the status of multiple tasks",
    description="Update the status of multiple tasks atomically, with optional status filtering.",
)
async def update_tasks_bulk(
    request: Request,
    data: TaskBulkStatusUpdateRequestModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Update the status of multiple tasks."""
    try:
        updated_ids = await task_store.update_status_bulk(
            task_ids=data.task_ids,
            status=data.status,
        )

        return TaskBulkStatusUpdateResponseModel(
            updated_task_ids=updated_ids
        )
    except InvalidTaskFieldException as exception:
        raise FarmServicesBaseException(status_code=400, detail=str(exception), request=request)


@router.post(
    "/info/bulk",
    response_model=TaskBulkInfoResponseModel,
    summary="Return information about multiple tasks",
    description="Return metadata information about multiple tasks, with optional status filtering.",
)
async def info_tasks_bulk(
    request: Request,
    data: TaskBulkInfoRequestModel,
    task_store: store.TaskStore = router.get_facility("task_store"),
):
    """Return information about multiple tasks."""
    try:
        tasks = await task_store.get_tasks_bulk(
            task_ids=data.task_ids,
            statuses=data.statuses,
        )
        found_ids = set(task["task_id"] for task in tasks)
        not_found = [tid for tid in data.task_ids if tid not in found_ids]

        return TaskBulkInfoResponseModel(
            tasks={task["task_id"]: task for task in tasks},
            not_found=not_found
        )
    except InvalidTaskFieldException as exception:
        raise FarmServicesBaseException(status_code=400, detail=str(exception), request=request)
