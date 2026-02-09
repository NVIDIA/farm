# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the ResultsService."""

from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from nv.svc.core import main

from nv.svc.farm.services.results.facilities.managers.memory import DictResultManager
from nv.svc.farm.services.results.router import router, validate_and_get_task, TaskContext

DAG_ID = "ef8fd4fc-b2ac-456e-adba-92775c2bed64"
TASK1_ID = "f411e8a2-2af4-4090-8f44-185de0e4aece"
TASK2_ID = "29aa6781-1371-4bcb-b5f0-61e6372c6b25"


class TestResultsService(IsolatedAsyncioTestCase):
    """Test cases for the ResultsService class."""

    async def asyncSetUp(self):
        await super().asyncSetUp()

        # Create memory manager for testing
        self._result_manager = DictResultManager()

        # Create a mock function to replace the task validation dependency
        async def mock_validate_and_get_task(task_id: str) -> TaskContext:
            return TaskContext(task_id=task_id, dag_id=DAG_ID, dag_node_name="test-node")

        # Create service core and register facilities
        core = main.ServicesCore(
            title="results",
            description="Farm Results Service.",
            version="0.1.0",
        )
        core.register_facility("result_manager", self._result_manager)
        core.register_router(router, prefix="/results")

        self.app = main.get_app()

        # Override the task validation dependency with our mock
        self.app.dependency_overrides[validate_and_get_task] = mock_validate_and_get_task

        self.client = TestClient(self.app)

    def tearDown(self):
        # Clear dependency overrides
        self.app.dependency_overrides.clear()
        super().tearDown()

    def test_status_endpoint(self):
        """Test the status endpoint."""
        response = self.client.get("/results/status")
        assert response.status_code == 200
        assert response.json() == "OK"

    def test_store_and_retrieve_result(self):
        """Test storing and retrieving a result."""
        test_data = "Task completed successfully! Output: test.png"

        # Store result
        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": test_data})
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True

        # Retrieve result
        response = self.client.get(f"/results/task/{TASK1_ID}")
        assert response.status_code == 200

        retrieved_result = response.json()
        assert retrieved_result["data"] == test_data

    def test_update_result(self):
        """Test updating an existing result."""
        original_data = "Original result data"
        updated_data = "Updated result data"

        # Store original result
        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": original_data})
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Update result
        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": updated_data})
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify update by retrieving
        response = self.client.get(f"/results/task/{TASK1_ID}")
        assert response.status_code == 200
        retrieved_result = response.json()
        assert retrieved_result["data"] == updated_data

    def test_get_nonexistent_result(self):
        """Test retrieving a result that doesn't exist."""
        response = self.client.get(f"/results/task/{TASK1_ID}")
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert "Result does not exist" in detail or "Not Found" in detail

    def test_invalid_data_type(self):
        """Test validation for invalid data type (object instead of string)."""
        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": {"nested": "object", "should": "fail"}})
        assert response.status_code == 422

    def test_missing_data_field(self):
        """Test validation for missing required data field."""
        response = self.client.post(f"/results/task/{TASK1_ID}", json={"wrong_field": "missing data field"})
        assert response.status_code == 422

    def test_large_data_within_limit(self):
        """Test storing data approaching the 128KB limit."""
        # Generate 64KB of data (well within 128KB limit)
        large_data = "A" * (64 * 1024)

        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": large_data})
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True

        # Verify by retrieving
        response = self.client.get(f"/results/task/{TASK1_ID}")
        assert response.status_code == 200
        retrieved_result = response.json()
        assert retrieved_result["data"] == large_data
        assert len(retrieved_result["data"]) == 64 * 1024

    def test_oversized_data_validation(self):
        """Test validation for data exceeding 128KB limit."""
        # Generate 150KB of data (exceeds 128KB limit)
        oversized_data = "B" * (150 * 1024)

        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": oversized_data})
        assert response.status_code == 422

    def test_empty_data_string(self):
        """Test storing empty string data."""

        response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": ""})
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True

        # Verify by retrieving
        response = self.client.get(f"/results/task/{TASK1_ID}")
        assert response.status_code == 200
        retrieved_result = response.json()
        assert retrieved_result["data"] == ""

    def test_dag_indexing_and_retrieval(self):
        """Test that DAG indexing works and we can retrieve results by DAG ID."""
        # Store results for two tasks (both will be indexed under the same DAG)
        response1 = self.client.post(f"/results/task/{TASK1_ID}", json={"data": "Task 1 result"})
        assert response1.status_code == 200
        assert response1.json()["success"] is True

        response2 = self.client.post(f"/results/task/{TASK2_ID}", json={"data": "Task 2 result"})
        assert response2.status_code == 200
        assert response2.json()["success"] is True

        # Retrieve all results for the DAG
        dag_response = self.client.get(f"/results/dag/{DAG_ID}")
        assert dag_response.status_code == 200

        dag_results = dag_response.json()
        assert isinstance(dag_results, list)

        # Let's also check if we can retrieve the individual tasks
        task1_response = self.client.get(f"/results/task/{TASK1_ID}")
        task2_response = self.client.get(f"/results/task/{TASK2_ID}")

        assert len(dag_results) == 2

        # Check that both results are returned (order not guaranteed)
        result_data = [result["data"] for result in dag_results]
        assert task1_response.json()["data"] in result_data
        assert task2_response.json()["data"] in result_data

    def test_invalid_dag_id_uuid_validation(self):
        """Test that invalid DAG ID format is properly rejected."""
        invalid_dag_id = "not-a-valid-uuid"

        response = self.client.get(f"/results/dag/{invalid_dag_id}")
        assert response.status_code == 422  # UUID validation error

    def test_task_without_dag_context(self):
        """Test storing a task that is not part of any DAG (empty dag_id)."""

        # Create a mock function that returns no DAG ID
        async def mock_validate_and_get_task_no_dag(task_id: str) -> TaskContext:
            return TaskContext(task_id=task_id, dag_id="", dag_node_name="")

        # Temporarily override the dependency for this test
        original_override = self.app.dependency_overrides.get(validate_and_get_task)
        self.app.dependency_overrides[validate_and_get_task] = mock_validate_and_get_task_no_dag

        try:
            test_data = "Standalone task result - not part of any DAG"

            # Store result for standalone task
            response = self.client.post(f"/results/task/{TASK1_ID}", json={"data": test_data})
            assert response.status_code == 200
            assert response.json()["success"] is True

            # Verify we can retrieve the individual task
            task_response = self.client.get(f"/results/task/{TASK1_ID}")
            assert task_response.status_code == 200
            assert task_response.json()["data"] == test_data

            # Verify that this task does NOT appear in DAG results
            dag_response = self.client.get(f"/results/dag/{DAG_ID}")
            assert dag_response.status_code == 200
            dag_results = dag_response.json()

            # Should be empty list or not contain our standalone task
            standalone_data_found = any(result.get("data") == test_data for result in dag_results)
            assert not standalone_data_found, "Standalone task should not appear in DAG results"

        finally:
            # Restore original dependency override
            if original_override:
                self.app.dependency_overrides[validate_and_get_task] = original_override
            else:
                self.app.dependency_overrides.pop(validate_and_get_task, None)
