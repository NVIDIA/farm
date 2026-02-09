# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the DictResultManager memory-based result storage implementation."""

from unittest import IsolatedAsyncioTestCase

from nv.svc.farm.services.results.facilities.managers.memory import DictResultManager
from nv.svc.farm.services.results.facilities.managers.base import ResultNotFound


class TestDictResultManager(IsolatedAsyncioTestCase):
    """Test cases for the DictResultManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = DictResultManager()

    async def test_store_new_result(self):
        """Test storing a new result without DAG indexing."""
        task_id = "test-task-1"
        data = "Test result data"

        # Store result
        await self.manager.store_result(task_id, data)
        stored_data = await self.manager.get_result(task_id)

        # Verify it's stored in memory
        assert stored_data == data

    async def test_store_result_with_dag_indexing(self):
        """Test storing a result with DAG indexing."""
        task_id = "dag-task-1"
        data = "DAG task result"
        dag_id = "taskflow-123"

        # Store result with DAG indexing
        await self.manager.store_result(task_id, data, dag_id)
        stored_data = await self.manager.get_result(task_id)

        # Verify task result is stored
        assert stored_data == data

        dag_results = await self.manager.get_results_by_dag(dag_id)
        assert stored_data in dag_results

    async def test_get_nonexistent_result(self):
        """Test retrieving a result that doesn't exist."""
        with self.assertRaises(ResultNotFound) as context:
            await self.manager.get_result("nonexistent-task")

        assert context.exception.task_id == "nonexistent-task"

    async def test_get_results_by_dag_with_results(self):
        """Test retrieving all results for a DAG that has results."""
        dag_id = "test-dag"
        tasks = [
            ("task1", "result1"),
            ("task2", "result2"),
            ("task3", "result3"),
        ]

        # Store multiple tasks for the same DAG
        for task_id, data in tasks:
            await self.manager.store_result(task_id, data, dag_id)

        # Retrieve all results by DAG
        dag_results = await self.manager.get_results_by_dag(dag_id)

        # Verify we got all results (order might vary)
        assert len(dag_results) == 3
        for _, expected_data in tasks:
            assert expected_data in dag_results

    async def test_get_results_by_dag_no_tasks(self):
        """Test retrieving results for a DAG with no tasks."""
        dag_results = await self.manager.get_results_by_dag("empty-dag")
        assert dag_results == []

    async def test_get_results_by_dag_with_missing_results(self):
        """Test retrieving DAG results when some tasks have missing results."""
        dag_id = "partial-dag"

        # Store tasks for the DAG
        await self.manager.store_result("task1", "result1", dag_id)
        await self.manager.store_result("task2", "result2", dag_id)
        await self.manager.store_result("task3", "result3", dag_id)

        # Manually delete one task result (simulating expiry)
        del self.manager._results["task2"]

        # Get DAG results - should only return existing ones
        dag_results = await self.manager.get_results_by_dag(dag_id)

        # Should get 2 results (missing task2)
        assert len(dag_results) == 2
        assert "result1" in dag_results
        assert "result3" in dag_results
        assert "result2" not in dag_results
