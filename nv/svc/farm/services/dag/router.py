# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm DAG Service Router."""

from typing import Dict, List, Optional
from uuid import UUID, uuid4

import pydantic

from nv.svc.core import exceptions
from nv.svc.core import routers
from nv.svc.farm.services.tasks.utils import status_utils
from nv.svc.farm.services.dag.facilities.dag_backend import DAGNotFound
router = routers.ServiceAPIRouter()


class DagEdge(pydantic.BaseModel):
    """Edge in a task dependency graph."""

    source_task_id: str = pydantic.Field(..., title="Source Task ID", description="ID of the source task")
    target_task_id: str = pydantic.Field(..., title="Target Task ID", description="ID of the target task")


class DagSubmission(pydantic.BaseModel):
    """Model for submitting a DAG."""

    edges: List[Dict[str, str]] = pydantic.Field(
        ...,
        title="Task Edges",
        description="List of edges defining task dependencies"
    )
    name: str = pydantic.Field(
        ...,
        title="DAG name",
        max_length=255,
        description="Name for the DAG (for display purposes)"
    )


class DagResponse(pydantic.BaseModel):
    """Response model for DAG operations."""

    dag_id: UUID = pydantic.Field(..., title="DAG ID", description="Unique identifier for the DAG")
    message: str = pydantic.Field(..., title="Message", description="Description of the operation result")
    name: Optional[str] = pydantic.Field(None, title="DAG name", description="Name of the DAG if provided")


class TaskCompletionModel(pydantic.BaseModel):
    """Model for task completion notification."""

    old_task_state: Dict = pydantic.Field(..., title="Old Task State", description="The task state before the status change")
    new_task_state: Dict = pydantic.Field(..., title="New Task State", description="The task state after the status change")


class DagInfoResponse(pydantic.BaseModel):
    """Response model for DAG information."""

    dag_id: UUID = pydantic.Field(..., title="DAG ID", description="Unique identifier for the DAG")
    name: str = pydantic.Field(..., title="DAG name", description="Name of the DAG")
    version: int = pydantic.Field(..., title="DAG version", description="Version of the DAG")
    edges: List[DagEdge] = pydantic.Field(..., title="DAG Edges", description="List of edges defining DAG dependencies")


@router.post(
    "/task-completed",
    response_model=DagResponse,
    summary="Handle task completion",
    description="Process task completion and update dependent tasks if their dependencies are satisfied.",
)
async def handle_task_completion(
    data: TaskCompletionModel,
    dag_store=router.get_facility("dag_store"),
) -> DagResponse:
    """Handle task completion.

    This endpoint:
    1. Gets notified when a task completes
    2. Checks all tasks that depend on the completed task
    3. If all dependencies of a dependent task are complete, marks it as ready
    """
    try:
        task_id = data.new_task_state.get("task_id")
        dag_id = data.new_task_state.get("metadata", {}).get("dag", {}).get("id")
        status = data.new_task_state.get("status")

        if not dag_id:
            raise exceptions.ServicesBaseException(
                status_code=400,
                detail=f"Unable to process task: {task_id} without a DAG ID"
            )

        if not status_utils.is_processed(status):
            raise exceptions.ServicesBaseException(
                status_code=400,
                detail=f"Unable to process task: {task_id} with status: {status}"
            )

        await dag_store.handle_task_completion(data.new_task_state)
        return DagResponse(
            dag_id=UUID(dag_id),
            message=f"Task completion processed successfully with status {status}"
        )
    except Exception as e:
        raise exceptions.ServicesBaseException(
            status_code=500,
            detail=f"Failed to process task completion: {str(e)}"
        )


@router.post(
    "/submit",
    response_model=DagResponse,
    summary="Submit a task dependency graph",
    description="Submit a new task dependency graph and validate its structure.",
)
async def submit_dag(
    data: DagSubmission,
    dag_store=router.get_facility("dag_store"),
) -> DagResponse:
    """Submit a task dependency graph.

    This endpoint:
    1. Validates that the graph is acyclic
    2. Creates a new DAG with the dependencies
    """
    try:
        # Generate a new DAG ID
        dag_id = uuid4()

        # Add the graph to the store
        await dag_store.add_graph(str(dag_id), data.edges, data.name)

        return DagResponse(
            dag_id=dag_id,
            message="Task graph submitted successfully",
            name=data.name
        )
    except ValueError as e:
        # Graph validation errors (e.g., cycles)
        raise exceptions.ServicesBaseException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise exceptions.ServicesBaseException(
            status_code=500,
            detail=f"Failed to submit task graph: {str(e)}"
        )


@router.get(
    "/status",
    summary="Healthcheck endpoint for DAG service.",
    description="Returns 200 and OK if DAG service is available.",
)
async def status():
    """DAG service status endpoint."""
    return "OK"


@router.get(
    "/{dag_id}",
    response_model=DagInfoResponse,
    summary="Get DAG info",
    description="Get information about a DAG.",
)
async def get_dag_info(
    dag_id: UUID,
    dag_store=router.get_facility("dag_store"),
) -> DagInfoResponse:
    """Get information about a DAG.

    This endpoint returns information about a DAG.
    """
    try:
        dag_info = await dag_store.get_dag_info(str(dag_id))
        return DagInfoResponse(
            dag_id=dag_id,
            name=dag_info["name"],
            version=dag_info["version"],
            edges=[DagEdge(**edge) for edge in dag_info["edges"]]
        )
    except DAGNotFound:
        raise exceptions.ServicesBaseException(
            status_code=404,
            detail=f"DAG {dag_id} not found"
        )
    except Exception as e:
        raise exceptions.ServicesBaseException(
            status_code=500,
            detail=f"Failed to get DAG info: {str(e)}"
        )


@router.delete(
    "/{dag_id}",
    response_model=DagResponse,
    summary="Delete a DAG",
    description="Delete a DAG and all its dependencies.",
)
async def delete_dag(
    dag_id: UUID,
    dag_store=router.get_facility("dag_store"),
) -> DagResponse:
    """Delete a DAG.

    This endpoint removes a DAG and all its dependencies from the store.
    """
    try:
        await dag_store.delete_dag(str(dag_id))
        return DagResponse(
            dag_id=dag_id,
            message="DAG deleted successfully"
        )
    except Exception as e:
        raise exceptions.ServicesBaseException(
            status_code=500,
            detail=f"Failed to delete DAG: {str(e)}"
        )
