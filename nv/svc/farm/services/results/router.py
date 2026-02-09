# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results service router."""

import logging
from typing import List
from uuid import UUID
import pydantic
from fastapi import Path, Depends, HTTPException

from nv.svc.core import routers
from nv.svc.core.exceptions import ServicesBaseException
from nv.svc.farm.utils import fetch_data
from nv.svc.farm.services.results.config import FarmResultsConfig
from nv.svc.farm.services.results.facilities.managers.base import BaseResultManager, ResultNotFound

router = routers.ServiceAPIRouter()


class TaskContext(pydantic.BaseModel):
    """Context information extracted from a task for result storage.

    All fields are guaranteed to be strings (never None) with proper defaults.
    """

    task_id: str
    dag_id: str = ""  # Always string, empty if task not part of DAG
    dag_node_name: str = ""  # Always string, empty if no node name


async def validate_and_get_task(
    task_id: str,
    config: FarmResultsConfig = router.get_facility("config")
) -> TaskContext:
    """Dependency to validate task exists and return relevant task context.

    This function will:
    1. Fetch task information from the task service
    2. Extract and parse DAG metadata with proper defaults
    3. Return a clean TaskContext object with guaranteed types
    4. FAIL with 400 Bad Request if task ID is invalid

    Args:
        task_id: The task ID to validate and fetch context for
        config: The results service configuration (injected dependency)

    Returns:
        TaskContext: Clean context object with parsed task and DAG information

    Raises:
        HTTPException: 400 Bad Request if task ID is invalid
    """

    try:
        # Attempt to fetch task from task service
        task_service_url = config.results.task_service_url
        task_info = await fetch_data(f"{task_service_url}/info/{task_id}")

        # Extract and parse DAG information with proper defaults
        dag_metadata = task_info.get("metadata", {}).get("dag", {})

        # Parse DAG information with proper defaults and type safety
        dag_id = dag_metadata.get("id", "")
        dag_uuid = UUID(dag_id) if dag_id else ""
        dag_node_name = dag_metadata.get("name", "")

        return TaskContext(
            task_id=task_id,
            dag_id=str(dag_uuid),
            dag_node_name=dag_node_name
        )
    except Exception as e:
        logging.info(f"Task validation failed for {task_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task ID: {task_id}"
        )


@router.get(
    "/status",
    summary="Healthcheck endpoint for results service.",
    description="Returns 200 and OK if results service is available.",
)
async def status():
    """Results service status endpoint."""
    return "OK"


class ResultRequestModel(pydantic.BaseModel):
    """Model for storing a result."""

    data: str = pydantic.Field(..., title="Result Data", description="The actual result data (max 128KB string)", max_length=131072)


class ResultResponseModel(pydantic.BaseModel):
    """Simplified response model for result data."""

    data: str = pydantic.Field(..., title="Result data", description="The result data string")


class ResultSuccessModel(pydantic.BaseModel):
    """Response model for successful result operations."""

    success: bool = pydantic.Field(True, title="Success", description="Indicates the operation was successful")


# Task-based endpoints
@router.post(
    "/task/{task_id}",
    response_model=ResultSuccessModel,
    summary="Store or update a result for a task",
    description="Store or update a result by task ID.",
)
async def store_task_result(
    request: ResultRequestModel,
    task_id: UUID = Path(..., title="Task ID", description="Unique identifier for the task"),
    task_context: TaskContext = Depends(validate_and_get_task),  # Only POST needs task validation and DAG parsing
    result_manager: BaseResultManager = router.get_facility("result_manager"),
):
    """Store or update a result for a task."""
    await result_manager.store_result(str(task_id), request.data, task_context.dag_id)
    return ResultSuccessModel()


@router.get(
    "/task/{task_id}",
    response_model=ResultResponseModel,
    summary="Retrieve a result for a task",
    description="Retrieve a result by task ID.",
)
async def get_task_result(
    task_id: UUID = Path(..., title="Task ID", description="Unique identifier for the task"),
    result_manager: BaseResultManager = router.get_facility("result_manager"),
):
    """Retrieve a result by task ID."""
    try:
        result_data = await result_manager.get_result(str(task_id))
        return ResultResponseModel(data=result_data)
    except ResultNotFound:
        raise ServicesBaseException(status_code=404, detail="Result does not exist.")


# DAG-based endpoints
@router.get(
    "/dag/{dag_id}",
    response_model=List[ResultResponseModel],
    summary="Get all results for a DAG",
    description="Retrieve all results associated with tasks in the specified DAG.",
)
async def get_dag_results(
    dag_id: UUID = Path(..., title="DAG ID", description="Unique identifier for the DAG"),
    result_manager: BaseResultManager = router.get_facility("result_manager"),
):
    """Get all results for tasks in a DAG."""
    results_data = await result_manager.get_results_by_dag(str(dag_id))
    return [ResultResponseModel(data=data) for data in results_data]
