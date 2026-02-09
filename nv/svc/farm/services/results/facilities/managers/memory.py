# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results Service Memory Manager."""

from typing import Dict, List, Set

from .base import BaseResultManager, ResultNotFound


class DictResultManager(BaseResultManager):
    """In-memory dictionary result manager for development and testing."""

    def __init__(self, **kwargs) -> None:
        """Initialize the memory manager."""
        super().__init__()
        self._results: Dict[str, str] = {}  # task_id -> data
        self._dag_index: Dict[str, Set[str]] = {}  # dag_id -> set of task_ids

    async def store_result(self, task_id: str, data: str, dag_id: str = "") -> None:
        """Store or update a result with DAG indexing."""
        # Store the raw data directly
        self._results[task_id] = data

        if not dag_id:
            return

        # Add to DAG index if DAG ID present
        dag_task_id_set = self._dag_index.get(dag_id, set())
        dag_task_id_set.add(task_id)
        self._dag_index[dag_id] = dag_task_id_set

    async def get_result(self, task_id: str) -> str:
        """Retrieve a specific result by task ID."""
        if task_id not in self._results:
            raise ResultNotFound(task_id)

        return self._results[task_id]

    async def get_results_by_dag(self, dag_id: str) -> List[str]:
        """Get all results for tasks in a DAG."""
        if not dag_id:
            return []

        if dag_id not in self._dag_index:
            return []

        # Get all task IDs for this DAG
        task_ids = self._dag_index[dag_id]

        # Collect results for all tasks that still exist
        results = [self._results.get(task_id) for task_id in task_ids if task_id in self._results]

        return results
