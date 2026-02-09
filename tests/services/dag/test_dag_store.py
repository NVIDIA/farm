# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the DAG store facility."""

import os
import uuid
from unittest import IsolatedAsyncioTestCase
from unittest import mock

from nv.svc.farm.services.dag.facilities.dag_store import DAGStore
from nv.svc.farm.services.dag.facilities.dag_backend import DagDatabaseBackend
from nv.svc.farm.services.tasks.utils import status_utils


class FakeResponse:
    """Mock HTTP response object."""

    def __init__(self, data=None):
        self.data = data or {}

    async def json(self):
        """Return mock response data."""
        return self.data


class TestDagStore(IsolatedAsyncioTestCase):
    """Test cases for the DAG store."""

    async def asyncSetUp(self):
        """Set up test database."""
        self.db_path = f"/tmp/test_dag_backend_{uuid.uuid4()}.db"
        self.backend = DagDatabaseBackend(f"sqlite:///{self.db_path}")
        self.task_service_url = "http://tasks:8000"
        self.store = DAGStore(self.backend, self.task_service_url)
        await self.store.start()

        # Mock both post_data and fetch_data to simulate task service responses
        self.post_data_patcher = mock.patch("nv.svc.farm.services.dag.facilities.dag_store.post_data")
        self.fetch_data_patcher = mock.patch("nv.svc.farm.services.dag.facilities.dag_store.fetch_data")
        self.mock_post_data = self.post_data_patcher.start()
        self.mock_fetch_data = self.fetch_data_patcher.start()

    async def asyncTearDown(self):
        """Clean up test database."""
        await self.store.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.post_data_patcher.stop()
        self.fetch_data_patcher.stop()

    async def test_handle_task_completion_no_dag_id(self):
        """Test handling completion of task with no DAG ID."""
        task_id = str(uuid.uuid4())

        task = {
            "task_id": task_id,
            "metadata": {}
        }

        # Should log error but not raise
        await self.store.handle_task_completion(task)

        # Should have not update any statuses
        self.mock_post_data.assert_not_called()

    async def test_handle_task_completion_no_children(self):
        """Test handling completion of task with no child tasks."""
        task_id = str(uuid.uuid4())
        dag_id = str(uuid.uuid4())

        # Mock task info response
        task = {
            "task_id": task_id,
            "metadata": {"dag": {"id": dag_id}},
            "status": status_utils.Status.finished
        }

        # No edges in graph means no children
        await self.store.handle_task_completion(task)

        # Should have only tried to get task info
        self.mock_post_data.assert_not_called()

    async def test_handle_task_completion_parents_not_complete(self):
        """Test handling completion when child task's parents aren't all complete."""
        dag_id = str(uuid.uuid4())
        task_1 = str(uuid.uuid4())  # Completed task
        task_2 = str(uuid.uuid4())  # Other parent, not complete
        task_3 = str(uuid.uuid4())  # Child task

        # Add edges: task_1 -> task_3 and task_2 -> task_3
        edges = [
            {"source_task_id": task_1, "target_task_id": task_3},
            {"source_task_id": task_2, "target_task_id": task_3}
        ]
        await self.store.add_graph(dag_id, edges)

        # Mock responses for task info calls
        async def mock_post_data_impl(url, data=None, **kwargs):
            if "/info/bulk" in url:
                return {
                    "tasks": {
                        task_2: {
                            "task_id": task_2,
                            "metadata": {"dag": {"id": dag_id}},
                            "status": status_utils.Status.running  # Not complete
                        }
                    },
                    "not_found": []
                }
            return {}

        self.mock_post_data.side_effect = mock_post_data_impl
        task = {
            "task_id": task_1,
            "metadata": {"dag": {"id": dag_id}},
            "status": status_utils.Status.finished
        }

        # Handle completion of task_1
        await self.store.handle_task_completion(task)

        # Should have made 1 fetch call and 1 bulk info request
        self.assertEqual(self.mock_post_data.call_count, 1)

        # Verify no update call was made since parents weren't all complete
        update_calls = [call for call in self.mock_post_data.call_args_list if "/update/bulk" in call[0][0]]
        self.assertEqual(len(update_calls), 0)

    async def test_handle_task_completion_parents_complete(self):
        """Test handling completion when all parents are complete."""
        dag_id = str(uuid.uuid4())
        task_1 = str(uuid.uuid4())  # First parent
        task_2 = str(uuid.uuid4())  # Second parent
        task_3 = str(uuid.uuid4())  # Child task

        # Add edges: task_1 -> task_3 and task_2 -> task_3
        edges = [
            {"source_task_id": task_1, "target_task_id": task_3},
            {"source_task_id": task_2, "target_task_id": task_3}
        ]
        await self.store.add_graph(dag_id, edges)

        # Mock responses for task info and update calls
        async def mock_post_data_impl(url, data=None, **kwargs):
            if "/update/bulk" in url:
                return {"updated_task_ids": data["task_ids"]}
            elif "/info/bulk" in url:
                return {
                    "tasks": {
                        task_2: {
                            "task_id": task_2,
                            "metadata": {"dag": {"id": dag_id}},
                            "status": status_utils.Status.finished  # Complete
                        }
                    },
                    "not_found": []
                }
            return {}

        self.mock_post_data.side_effect = mock_post_data_impl
        task = {
            "task_id": task_1,
            "metadata": {"dag": {"id": dag_id}},
            "status": status_utils.Status.finished
        }

        # Handle completion of task_1
        await self.store.handle_task_completion(task)

        # Should have made 1 bulk info request, and 1 bulk update
        self.assertEqual(self.mock_post_data.call_count, 2)

        # Verify the last call was to update task_3 status
        last_call = self.mock_post_data.call_args_list[-1]
        self.assertIn("/update/bulk", last_call[0][0])
        self.assertEqual(last_call[1]["data"]["task_ids"], [task_3])
        self.assertEqual(last_call[1]["data"]["status"], status_utils.Status.submitted)

    async def test_handle_task_completion_complex_dag(self):
        """Test handling completion in a more complex DAG structure."""
        dag_id = str(uuid.uuid4())
        task_ids = [str(uuid.uuid4()) for _ in range(5)]

        # Create a diamond-shaped graph with additional edges:
        # A -> B -> D -> E
        # A -> C -> D
        edges = [
            {"source_task_id": task_ids[0], "target_task_id": task_ids[1]},  # A -> B
            {"source_task_id": task_ids[0], "target_task_id": task_ids[2]},  # A -> C
            {"source_task_id": task_ids[1], "target_task_id": task_ids[3]},  # B -> D
            {"source_task_id": task_ids[2], "target_task_id": task_ids[3]},  # C -> D
            {"source_task_id": task_ids[3], "target_task_id": task_ids[4]},  # D -> E
        ]
        await self.store.add_graph(dag_id, edges)

        # Mock responses
        task_statuses = {task_id: status_utils.Status.finished for task_id in task_ids}
        task_statuses[task_ids[3]] = status_utils.Status.unscheduled  # D is unscheduled
        task_statuses[task_ids[4]] = status_utils.Status.unscheduled  # E is unscheduled

        async def mock_post_data_impl(url, data=None, **kwargs):
            if "/update/bulk" in url:
                return {"updated_task_ids": data["task_ids"]}
            elif "/info/bulk" in url:
                tasks_info = {}
                for task_id in data["task_ids"]:
                    tasks_info[task_id] = {
                        "task_id": task_id,
                        "metadata": {"dag": {"id": dag_id}},
                        "status": task_statuses[task_id]
                    }
                return {
                    "tasks": tasks_info,
                    "not_found": []
                }
            return {}

        self.mock_post_data.side_effect = mock_post_data_impl
        task = {
            "task_id": task_ids[1],  # task B
            "metadata": {"dag": {"id": dag_id}},
            "status": task_statuses[task_ids[1]]
        }

        # When B completes (and A and C are already complete)
        # D should be submitted but not E
        await self.store.handle_task_completion(task)  # Complete B

        # Should have made 1 bulk info request, and 1 bulk update
        self.assertEqual(self.mock_post_data.call_count, 2)

        # Find the update calls
        update_calls = [
            call for call in self.mock_post_data.call_args_list 
            if "/update/bulk" in call[0][0]
        ]

        # Should have updated only D
        self.assertEqual(len(update_calls), 1)
        self.assertEqual(update_calls[0][1]["data"]["task_ids"], [task_ids[3]])  # D

    async def test_add_simple_graph(self):
        """Test adding a simple two-node graph."""
        dag_id = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        target_id = str(uuid.uuid4())

        edges = [{"source_task_id": source_id, "target_task_id": target_id}]
        await self.store.add_graph(dag_id, edges)

        # Verify dependencies
        deps = await self.store.get_task_parents(dag_id, target_id)
        self.assertEqual(deps, [source_id])

        # Verify dependents
        deps = await self.store.get_task_children(dag_id, source_id)
        self.assertEqual(deps, [target_id])

    async def test_add_complex_graph(self):
        """Test adding and querying a complex graph structure."""
        dag_id = str(uuid.uuid4())
        task_ids = [str(uuid.uuid4()) for _ in range(5)]

        # Create a diamond-shaped graph with additional edges
        edges = [
            {"source_task_id": task_ids[0], "target_task_id": task_ids[1]},  # A -> B
            {"source_task_id": task_ids[0], "target_task_id": task_ids[2]},  # A -> C
            {"source_task_id": task_ids[1], "target_task_id": task_ids[3]},  # B -> D
            {"source_task_id": task_ids[2], "target_task_id": task_ids[3]},  # C -> D
            {"source_task_id": task_ids[3], "target_task_id": task_ids[4]},  # D -> E
        ]

        await self.store.add_graph(dag_id, edges)

        # Verify dependencies for D (should have B and C as dependencies)
        deps = await self.store.get_task_parents(dag_id, task_ids[3])
        self.assertEqual(set(deps), {task_ids[1], task_ids[2]})

        # Verify dependents for A (should have B and C as dependents)
        deps = await self.store.get_task_children(dag_id, task_ids[0])
        self.assertEqual(set(deps), {task_ids[1], task_ids[2]})

        # Verify the full subgraph starting from A
        subgraph = await self.store.get_subgraph_tasks(dag_id, task_ids[0])
        self.assertEqual(subgraph, set(task_ids[1:]))  # All nodes except A

    async def test_cyclic_graph_rejection(self):
        """Test that cyclic graphs are rejected."""
        dag_id = str(uuid.uuid4())
        task_ids = [str(uuid.uuid4()) for _ in range(3)]

        # Create a cycle: A -> B -> C -> A
        edges = [
            {"source_task_id": task_ids[0], "target_task_id": task_ids[1]},
            {"source_task_id": task_ids[1], "target_task_id": task_ids[2]},
            {"source_task_id": task_ids[2], "target_task_id": task_ids[0]},
        ]

        with self.assertRaises(ValueError) as context:
            await self.store.add_graph(dag_id, edges)
        self.assertIn("cycles", str(context.exception))

    async def test_get_subgraph_tasks_single_node(self):
        """Test getting subgraph for a single node with no edges."""
        dag_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())

        subgraph = await self.store.get_subgraph_tasks(dag_id, task_id)
        self.assertEqual(subgraph, {task_id})

    async def test_get_subgraph_tasks_complex(self):
        """Test getting subgraph for a complex graph structure."""
        dag_id = str(uuid.uuid4())
        task_ids = [str(uuid.uuid4()) for _ in range(6)]

        # Create a more complex graph:
        # A -> B -> D -> F
        # A -> C -> E -> F
        edges = [
            {"source_task_id": task_ids[0], "target_task_id": task_ids[1]},  # A -> B
            {"source_task_id": task_ids[0], "target_task_id": task_ids[2]},  # A -> C
            {"source_task_id": task_ids[1], "target_task_id": task_ids[3]},  # B -> D
            {"source_task_id": task_ids[2], "target_task_id": task_ids[4]},  # C -> E
            {"source_task_id": task_ids[3], "target_task_id": task_ids[5]},  # D -> F
            {"source_task_id": task_ids[4], "target_task_id": task_ids[5]},  # E -> F
        ]

        await self.store.add_graph(dag_id, edges)

        # Get subgraph starting from A (should include all nodes except A)
        subgraph = await self.store.get_subgraph_tasks(dag_id, task_ids[0])
        self.assertEqual(subgraph, set(task_ids[1:]))

        # Get subgraph starting from B (should include D and F)
        subgraph = await self.store.get_subgraph_tasks(dag_id, task_ids[1])
        self.assertEqual(subgraph, {task_ids[3], task_ids[5]})

    async def test_delete_dag(self):
        """Test deleting a DAG."""
        dag_id = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        target_id = str(uuid.uuid4())

        edges = [{"source_task_id": source_id, "target_task_id": target_id}]
        await self.store.add_graph(dag_id, edges)

        # Verify graph exists
        deps = await self.store.get_task_parents(dag_id, target_id)
        self.assertEqual(deps, [source_id])

        # Delete the DAG
        await self.store.delete_dag(dag_id)

        # Verify graph is empty
        deps = await self.store.get_task_parents(dag_id, target_id)
        self.assertEqual(deps, [])
