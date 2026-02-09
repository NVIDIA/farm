# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results Service Base Manager Facility."""

import abc
from typing import List

from nv.svc.core.facilities import base


class ResultNotFound(Exception):
    """Exception raised when a result is not found."""

    def __init__(self, task_id: str):
        """Initialize the ResultNotFound exception."""
        self.task_id = task_id
        super().__init__(f"Result not found for task: {task_id}")


class BaseResultManager(abc.ABC, base.Facility):
    """Base implementation for result management."""

    def __init__(self) -> None:
        """Initialize the base result manager."""
        super().__init__()

    @abc.abstractmethod
    async def store_result(self, task_id: str, data: str, dag_id: str = "") -> None:
        """
        Store or update a result with DAG indexing.

        Args:
            task_id (str): Unique identifier for the task.
            data (str): Result data string (max 128KB).
            dag_id (str): DAG ID for indexing (empty string if not part of a DAG).

        Returns:
            None: No return value.
        """
        pass

    @abc.abstractmethod
    async def get_result(self, task_id: str) -> str:
        """
        Retrieve a specific result by task ID.

        Args:
            task_id (str): Unique identifier for the task.

        Returns:
            str: The result data.

        Raises:
            ResultNotFound: If result does not exist.
        """
        pass

    @abc.abstractmethod
    async def get_results_by_dag(self, dag_id: str) -> List[str]:
        """
        Get all results for tasks in a DAG.

        Args:
            dag_id (str): Unique identifier for the DAG.

        Returns:
            List[str]: List of result data strings for all tasks in the DAG.
        """
        pass
