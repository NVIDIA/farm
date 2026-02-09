# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the DAG service endpoints."""

import copy
import os
import uuid
from typing import Dict
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from nv.svc.core import main
from nv.svc.farm.services.dag.facilities.dag_backend import DagDatabaseBackend
from nv.svc.farm.services.dag.facilities.dag_store import DAGStore
from nv.svc.farm.services.dag.router import router


class TestDagService(IsolatedAsyncioTestCase):
    """Test cases for the DAG service endpoints."""

    def _setup_mocks_task_completed_endpoint(self, task_ids):
        """Set up mock fetch data with the given tasks.

        Args:
            mock: The mock to configure
            tasks: Dict of task_id to task info
        """
        metadata = {"dag": {}, "_retry": {}}
        tasks = {
            task_id: {"task_id": task_id, "status": "unscheduled", "metadata": metadata}
            for task_id in task_ids
        }

        for i, task in enumerate(tasks):
            tasks[task]["metadata"] = copy.deepcopy(metadata)
            tasks[task]["metadata"]["dag"]["name"] = f"task_{i + 1}"

        async def mock_post_data(url, data=None, **kwargs):
            if "/update/bulk" in url:
                return {"updated_task_ids": data["task_ids"]}
            elif "/info/bulk" in url:
                return {"tasks": tasks}
            return {}

        self.mock_post_data.side_effect = mock_post_data

        return tasks

    def _setup_graph(self, tasks, edges):
        """Set up a graph with the given tasks and edges."""
        response = self.client.post(
            "/dag/submit",
            json={"edges": edges, "name": "test_dag"}
        )

        for task in tasks:
            tasks[task]["metadata"]["dag"]["id"] = response.json()["dag_id"]

        return tasks

    def _setup_simple_fan_out_dag(self):
        """Set up a simple fan-out DAG with the given tasks."""
        task_ids = [str(uuid.uuid4()) for _ in range(3)]
        tasks = self._setup_mocks_task_completed_endpoint(task_ids)

        task_1, task_2, task_3 = tasks.keys()
        self._setup_graph(tasks, [
            {"source_task_id": task_1, "target_task_id": task_2},
            {"source_task_id": task_1, "target_task_id": task_3}
        ])

        return task_ids, tasks

    def _setup_simple_fan_in_dag(self):
        """Set up a simple fan-out DAG with the given tasks."""
        task_ids = [str(uuid.uuid4()) for _ in range(3)]
        tasks = self._setup_mocks_task_completed_endpoint(task_ids)

        task_1, task_2, task_3 = tasks.keys()
        self._setup_graph(tasks, [
            {"source_task_id": task_1, "target_task_id": task_3},
            {"source_task_id": task_2, "target_task_id": task_3}
        ])

        return task_ids, tasks

    def _set_task_retryable(self, task: Dict, is_retryable: bool = True, done: bool = False):
        """Set the retryable for the given task."""
        task["metadata"]["_retry"]["is_retryable"] = is_retryable
        task["metadata"]["_retry"]["is_done"] = done

    def _get_bulk_update_calls(self):
        """Get the bulk update call from the mock post data."""
        return [{"task_ids": c[2]["data"]["task_ids"], "status": c[2]["data"]["status"]} for c in self.mock_post_data.mock_calls if "/update/bulk" in c[1][0]]

    def _assert_bulk_update_call(self, bulk_update_call, expected_task_ids, expected_status):
        """Assert that a bulk update was called with the expected tasks and status."""
        assert set(bulk_update_call["task_ids"]) == set(expected_task_ids)
        assert bulk_update_call["status"] == expected_status

    async def asyncSetUp(self):
        """Set up test environment."""
        await super().asyncSetUp()

        # Create a unique database file for this test
        self.db_path = f"/tmp/test_dag_backend_{uuid.uuid4()}.db"
        connection_string = f"sqlite:///{self.db_path}"

        # Set up backend and store
        self._backend = DagDatabaseBackend(connection_string)
        await self._backend.start()  # This will initialize the database

        self._dag_store = DAGStore(self._backend, "http://tasks:8000")
        await self._dag_store.start()

        # Set up core service
        core = main.ServicesCore(
            title="dag",
            description="Farm DAG Service.",
            version="0.1.0",
        )
        core.register_facility("dag_store", self._dag_store)

        # Register the router with the main application
        core.register_router(router, prefix="/dag")

        # Get the app and test client
        self.app = main.get_app()
        self.client = TestClient(self.app)

        # Mock both post_data and fetch_data to simulate task service responses
        self.post_data_patcher = patch("nv.svc.farm.services.dag.facilities.dag_store.post_data")
        self.fetch_data_patcher = patch("nv.svc.farm.services.dag.facilities.dag_store.fetch_data")
        self.mock_post_data = self.post_data_patcher.start()
        self.mock_fetch_data = self.fetch_data_patcher.start()

    async def asyncTearDown(self):
        """Clean up test environment."""
        # Stop the patchers
        self.post_data_patcher.stop()
        self.fetch_data_patcher.stop()

        await self._dag_store.stop()
        await self._backend.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        await super().asyncTearDown()

    def test_submit_endpoint_basic(self):
        """Basic test of the /submit endpoint."""
        task_id = str(uuid.uuid4())

        # Test submitting a single task
        response = self.client.post(
            "/dag/submit",
            json={
                "edges": [{"source_task_id": task_id, "target_task_id": str(uuid.uuid4())}],
                "name": "test_dag"
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "dag_id" in result
        assert "message" in result
        assert result["name"] == "test_dag"

    def test_task_completed_fan_out_finished(self):
        """Test handling task completion in a fan-out pattern."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "finished"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        # Verify that both task_2 and task_3 were submitted
        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_2, task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_out_errored(self):
        """Test handling task completion in a fan-out pattern."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "errored"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        # Verify that both task_2 and task_3 were submitted
        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_2, task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_out_unschedulable(self):
        """Test handling task completion in a fan-out pattern."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "unschedulable"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        # Verify that both task_2 and task_3 were submitted
        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_2, task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_out_retry(self):
        """Test handling task completion in a fan-out pattern with retry status."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        self._set_task_retryable(tasks[task_1], done=True)
        tasks[task_1]["status"] = "errored"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        # Verify that both task_2 and task_3 were submitted
        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_2, task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_out_dependency_resolution_always_run_errored(self):
        """Test handling task completion in a fan-out pattern with errored status and ALWAYS_RUN dependency resolution strategy."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "errored"
        tasks[task_2]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"

        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 2
        submitted_bulk_update_call = [c for c in bulk_update_calls if c["status"] == "submitted"][0]
        unschedulable_bulk_update_call = [c for c in bulk_update_calls if c["status"] == "unschedulable"][0]
        self._assert_bulk_update_call(bulk_update_call=submitted_bulk_update_call, expected_task_ids=[task_2], expected_status="submitted")
        self._assert_bulk_update_call(bulk_update_call=unschedulable_bulk_update_call, expected_task_ids=[task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_out_dependency_resolution_always_run_unschedulable(self):
        """Test handling task completion in a fan-out pattern with unschedulable status and ALWAYS_RUN dependency resolution strategy."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "unschedulable"
        tasks[task_2]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"

        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 2
        submitted_bulk_update_call = [c for c in bulk_update_calls if c["status"] == "submitted"][0]
        unschedulable_bulk_update_call = [c for c in bulk_update_calls if c["status"] == "unschedulable"][0]
        self._assert_bulk_update_call(bulk_update_call=submitted_bulk_update_call, expected_task_ids=[task_2], expected_status="submitted")
        self._assert_bulk_update_call(bulk_update_call=unschedulable_bulk_update_call, expected_task_ids=[task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_out_dependency_resolution_always_run_finished(self):
        """Test handling task completion in a fan-out pattern with finished status and ALWAYS_RUN dependency resolution strategy."""
        task_ids, tasks = self._setup_simple_fan_out_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "finished"
        tasks[task_2]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"

        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_2, task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_finished(self):
        """Test handling task completion in a fan-in pattern."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "finished"
        tasks[task_2]["status"] = "finished"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_errored(self):
        """Test handling task completion in a fan-in pattern."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "errored"
        tasks[task_2]["status"] = "finished"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_in_unschedulable(self):
        """Test handling task completion in a fan-in pattern."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "unschedulable"
        tasks[task_2]["status"] = "unschedulable"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="unschedulable")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_always_run_errored(self):
        """Test handling task completion in a fan-in pattern with errored status and ALWAYS_RUN dependency resolution strategy."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "errored"
        tasks[task_2]["status"] = "finished"
        tasks[task_3]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_always_run_unschedulable(self):
        """Test handling task completion in a fan-in pattern with unschedulable status."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "unschedulable"
        tasks[task_2]["status"] = "unschedulable"
        tasks[task_3]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_always_run_finished(self):
        """Test handling task completion in a fan-in pattern with finished status."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "finished"
        tasks[task_2]["status"] = "finished"
        tasks[task_3]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"
        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_1],
                "new_task_state": tasks[task_1]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_always_run_one_errored_one_finished(self):
        """Test handling task completion in a fan-in pattern where one dependency is errored and one is finished."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "errored"
        tasks[task_2]["status"] = "finished"
        tasks[task_3]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"

        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_2],
                "new_task_state": tasks[task_2]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_always_run_one_unschedulable_one_finished(self):
        """Test handling task completion in a fan-in pattern where one dependency is unschedulable and one is finished."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "unschedulable"
        tasks[task_2]["status"] = "finished"
        tasks[task_3]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"

        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_2],
                "new_task_state": tasks[task_2]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_always_run_one_errored_one_unschedulable(self):
        """Test handling task completion in a fan-in pattern where one dependency is errored and one is unschedulable."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        tasks[task_1]["status"] = "errored"
        tasks[task_2]["status"] = "unschedulable"
        tasks[task_3]["metadata"]["dag"]["dependency_resolution_strategy"] = "ALWAYS_RUN"

        response = self.client.post(
            "/dag/task-completed",
            json={
                "old_task_state": tasks[task_2],
                "new_task_state": tasks[task_2]
            }
        )

        bulk_update_calls = self._get_bulk_update_calls()
        assert len(bulk_update_calls) == 1
        self._assert_bulk_update_call(bulk_update_call=bulk_update_calls[0], expected_task_ids=[task_3], expected_status="submitted")
        assert response.status_code == 200

    def test_task_completed_fan_in_dependency_resolution_no_updates(self):
        """Test handling task completion in a fan-in pattern where no updates should occur due to incomplete dependencies."""
        task_ids, tasks = self._setup_simple_fan_in_dag()
        task_1, task_2, task_3 = task_ids
        statuses = ["finished", "errored", "unschedulable"]

        # should not progress with one task unscheduled
        for status in statuses:
            tasks[task_1]["status"] = status
            response = self.client.post(
                "/dag/task-completed",
                json={
                    "old_task_state": tasks[task_1],
                    "new_task_state": tasks[task_1]
                }
            )

            bulk_update_calls = self._get_bulk_update_calls()
            assert len(bulk_update_calls) == 0
            assert response.status_code == 200

        # should not progress with one task actively retrying
        self._set_task_retryable(tasks[task_1])
        tasks[task_1]["status"] = "errored"
        for status in statuses:
            tasks[task_2]["status"] = status
            response = self.client.post(
                "/dag/task-completed",
                json={
                    "old_task_state": tasks[task_2],
                    "new_task_state": tasks[task_2]
                }
            )

            bulk_update_calls = self._get_bulk_update_calls()
            assert len(bulk_update_calls) == 0
            assert response.status_code == 200

    def test_get_dag_info_success(self):
        """GET /dag/{id} returns DAG info for an existing DAG."""
        src = str(uuid.uuid4())
        dst = str(uuid.uuid4())
        submit_res = self.client.post(
            "/dag/submit",
            json={
                "edges": [{"source_task_id": src, "target_task_id": dst}],
                "name": "test_dag",
            },
        )
        assert submit_res.status_code == 200
        dag_id = submit_res.json()["dag_id"]

        res = self.client.get(f"/dag/{dag_id}")
        assert res.status_code == 200
        body = res.json()
        assert body["dag_id"] == dag_id
        assert body["name"] == "test_dag"
        assert body["version"] == 1
        assert body["edges"] == [{"source_task_id": src, "target_task_id": dst}]

    def test_get_dag_info_not_found(self):
        """GET /dag/{id} returns 404 for unknown DAG."""
        missing_id = str(uuid.uuid4())
        res = self.client.get(f"/dag/{missing_id}")
        assert res.status_code == 404

    def test_delete_dag_success(self):
        """GET /dag/{id} returns DAG info for an existing DAG."""
        src = str(uuid.uuid4())
        dst = str(uuid.uuid4())
        submit_res = self.client.post(
            "/dag/submit",
            json={
                "edges": [{"source_task_id": src, "target_task_id": dst}],
                "name": "test_dag",
            },
        )
        assert submit_res.status_code == 200
        dag_id = submit_res.json()["dag_id"]

        res = self.client.delete(f"/dag/{dag_id}")
        assert res.status_code == 200
        body = res.json()
        assert body["dag_id"] == dag_id
        assert body["message"] == "DAG deleted successfully"
