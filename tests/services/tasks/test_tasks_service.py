# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from nv.svc.core import main

from nv.svc.farm.services.tasks.facilities.tasks.backends import TaskIdDictBackend
from nv.svc.farm.services.tasks.facilities.tasks.store import TaskStore
from nv.svc.farm.services.tasks.router import router


class TestTasksService(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

        self._backend = TaskIdDictBackend()
        self._task_store = TaskStore(self._backend)

        core = main.ServicesCore(
            title="tasks",
            description="Farm Tasks Service.",
            version="0.1.0",
        )
        core.register_facility("task_store", self._task_store)

        # Register the router with the main application.
        core.register_router(router, prefix="/tasks")

        # Populate the store with stub data for testing.
        await self._backend._save_task(userid="userId1", status="submitted", task_type="task1", task_function="forfun", task_id="abcd")
        await self._backend._save_task(userid="userId1", status="pending", task_type="task1", task_function="forfun")
        await self._backend._save_task(userid="userId2", status="submitted", task_type="task1", task_function="forfun2")
        await self._backend._save_task(userid="userId1", status="finished", task_type="task2", task_function="forfun2")

        # Update abcd task so it has history
        await self._backend.update_task(task_id="abcd", task_type="task1", task_function="forfun", userid="userId1", status="running")

        self.app = main.get_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        super().tearDown()

    def test_status_endpoint(self):
        response = self.client.get("/tasks/status")
        assert response.status_code == 200

    # tasks/list
    async def test_tasks_list_with_status(self):
        res = self.client.get("/tasks/list?status=submitted").json()

        for tasks in res.values():
            for task in tasks:
                self.assertEqual(task["status"], "submitted")

    # tasks/info
    async def test_task_info_with_status(self):
        task_id = "abcd"
        res = self.client.get(f"/tasks/info/{task_id}").json()
        self.assertEqual(res["task_id"], task_id)

    async def test_task_info_not_found(self):
        res = self.client.get("/tasks/info/i-dont-exist")
        assert res.status_code, 404

    # tasks/revision-history
    async def test_task_revision_history(self):
        res = self.client.get("/tasks/revision-history/abcd").json()

        self.assertEqual(res[0]["task_id"], "abcd")
        self.assertEqual(res[0]["status"], "running")

    # tasks/submit
    async def test_task_submit(self):
        data = dict(
            user="test_user",
            task_type="submit_task",
            task_args={},
            task_function="submit_function",
            task_function_args={},
            task_requirements={},
            task_comment="submit function test",
            priority=1,
            metadata={},
            labels=["foo", "bar"],
        )
        res = self.client.post("/tasks/submit", json=data).json()

        self.assertIsNotNone(res)
        self.assertIsNotNone(res["task_id"])

    async def test_task_submit_fields_exceed_limit(self):
        for field, max_length in [("task_function", 128), ("task_type", 512), ("user", 2048)]:
            task_kwargs = dict(
                user="test_user",
                task_type="test_type",
                task_args={},
                task_function="submit_function",
                task_function_args={},
                task_requirements={},
                task_comment="submit function test",
                priority=1,
                metadata={},
            )
            # exceed the field char limit by 1
            task_kwargs[field] = "t" * (max_length+1)
            res = self.client.post("/tasks/submit", json=task_kwargs)
            assert 422 == res.status_code

    # # tasks/update
    async def test_task_update(self):
        # Create a task to update
        task_id = "toupdate"
        await self._backend._save_task(userid="userId1", status="pending", task_type="task1", task_function="forfun", task_id=task_id)

        data = dict(
            task_id=task_id,
            userid="userId1",
            task_type="task1",
            task_function="forfun",
            status="running",
        )
        res = self.client.post("/tasks/update", json=data).json()

        self.assertIsNotNone(res)
        self.assertEqual(res["should_cancel"], False)

        res = self.client.get(f"/tasks/info/{task_id}").json()
        self.assertEqual(res["status"], "running")

    async def test_task_update_fields_exceed_limit(self):
        # Create a task to update
        await self._backend._save_task(userid="userId1", status="pending", task_type="task1", task_function="forfun", task_id="toupdate")

        for field, max_length in [("agent_id", 2048), ("task_id", 36), ("task_function", 128), ("task_type", 512), ("userid", 2048)]:
            task_kwargs = dict(
                task_id="toupdate",
                userid="userId1",
                task_type="task1",
                task_function="forfun",
                status="running",
                agent_id="123",
            )
            # exceed the field char limit by 1
            task_kwargs[field] = "t" * (max_length+1)
            res = self.client.post("/tasks/update", json=task_kwargs)
            assert 422 == res.status_code

    # # tasks/archive
    async def test_task_archive(self):
        # Create task to archive
        await self._backend._save_task(userid="userId1", status="finished", task_type="task1", task_function="forfun", task_id="toarchive")

        res = self.client.post("/tasks/archive", json=dict(task_ids=["toarchive"])).json()

        self.assertIsNotNone(res)
        self.assertEqual(res["archived_tasks_count"], 1)
        self.assertEqual(res["error_count"], 0)

    # # tasks/cancel
    async def test_task_cancel(self):
        # Create task to cancel
        await self._backend._save_task(userid="userId1", status="running", task_type="task1", task_function="forfun", task_id="tocancel")

        res = self.client.post("/tasks/cancel", json=dict(
            task_id="tocancel",
            task_type="task1",
            task_function="forfun",
            userid="userId1",
            status="running"
            )
        )
        assert 200 == res.status_code

    async def test_task_fetch(self):
        # Create task to archive
        await self._backend._save_task(userid="userId1", status="submitted", task_type="task1", task_function="forfun", task_id="taz")
        data = dict(
            task_types=[("task1", "forfun")],
            capacity={},
            agent_id="agent_a",
        )
        res = self.client.post("/tasks/fetch", json=data).json()

        self.assertEqual(res["task_id"], "taz")

    async def test_task_fetch_by_label(self):
        await self._backend._save_task(userid="userId1", status="submitted", task_type="task2", task_function="forfun2", labels=["foo", "bar"], task_id="taz")
        data = dict(
            task_types=[("task2", "forfun2")],
            capacity={},
            agent_id="agent_a",
            labels=["foo", "bar"],
        )
        res = self.client.post("/tasks/fetch", json=data).json()

        self.assertEqual(res["task_id"], "taz")

    async def test_task_fetch_not_found_without_label(self):
        await self._backend._save_task(userid="userId1", status="submitted", task_type="label", task_function="haslabel", labels=["foo", "bar"], task_id="taz")
        data = dict(task_types=[("label", "haslabel")], capacity={}, agent_id="agent_a")
        res = self.client.post("/tasks/fetch", json=data).json()

        self.assertIsNone(res)

    async def test_bulk_status(self):
        # Create test tasks in cancelled state
        task_ids = ["task1", "task2"]

        test_cases = [
            {
                "status": "archived",
                "starting_status": "cancelled",
                "expected_status": "archived"  # 1. Archive cancelled -> archived
            },
            {
                "status": "submitted",
                "starting_status": "cancelled",
                "expected_status": "submitted"  # 2. Retry cancelled -> submitted
            },
            {
                "status": "cancelling",
                "starting_status": "submitted",
                "expected_status": "cancelling"  # 3. Cancel submitted -> cancelling
            }
        ]

        for case in test_cases:
            for task_id in task_ids:
                await self._backend._save_task(
                    userid="userId1",
                    status=case["starting_status"],  # Start with cancelled
                    task_type="task1",
                    task_function="forfun",
                    task_id=task_id
                )
            request_data = {
                "userid": "admin",
                "status": case["status"],
                "task_ids": task_ids
            }

            response = self.client.post("/tasks/bulk-status", json=request_data)
            assert response.status_code == 200
            result = response.json()
            assert "errors" in result

            # Verify tasks were updated
            for task_id in task_ids:
                task = await self._backend.get_task(task_id=task_id)
                assert task["status"] == case["expected_status"]
            assert result["updated_task_count"] == 2

    async def test_bulk_status_revision_history(self):
        # Create test tasks in cancelled state

        response = self.client.post("/tasks/submit", json=dict(
            user="testuser",
            task_comment="basic test",
            task_type="test_type",
            task_args={},
            task_function="test_function",
            task_function_args={},
            task_requirements={},
            metadata={},
            status="submitted"
        ))

        response_json = response.json()
        task_id = response_json["task_id"]

        self.client.post("/tasks/bulk-status", json=dict(
            task_ids=[task_id],
            userid="admin",
            status="cancelling",
        ))

        # Verify tasks revision was updated
        revisions = await self._backend.get_task_revision_history(task_id=task_id)
        assert len(revisions) == 2
        assert revisions[0].status == "submitted"
        assert revisions[0].user_id == "testuser"
        assert revisions[1].status == "cancelling"
        assert revisions[1].user_id == "admin"

    async def test_bulk_status_validation_error(self):
        """Test that invalid requests return 422 with proper error details."""

        # Missing required fields
        request_data = {
            "task_ids": ["task1"]
        }

        response = self.client.post("/tasks/bulk-status", json=request_data)
        assert response.status_code == 422
        result = response.json()
        assert "detail" in result  # FastAPI validation error format

    async def test_bulk_status_task_store_errors(self):
        """Test that task store errors are returned correctly."""

        # Create a task in a state that can't be archived
        tasks = [{"task_id": "task1", "status": "running"}, {"task_id": "task2", "status": "cancelled"}]
        for task in tasks:
            await self._backend._save_task(
                userid="userId1",
                status=task["status"],  # Start with cancelled
                task_type="task1",
                task_function="forfun",
                task_id=task["task_id"]
            )

        request_data = {
            "status": "archived",
            "userid": "admin",
            "task_ids": [task["task_id"] for task in tasks]
        }

        response = self.client.post("/tasks/bulk-status", json=request_data)
        assert response.status_code == 200  # The endpoint still succeeds
        result = response.json()

        assert len(result["errors"]) == 1
        error = result["errors"][0]
        assert error["task_id"] == "task1"
        assert "invalid status transition" in error["error"].lower()

        # Verify task was not archived
        task = await self._backend.get_task(task_id="task1")
        assert task["status"] == "running"

        # Verify task archived
        task = await self._backend.get_task(task_id="task2")
        assert result["updated_task_count"] == 1
        assert task["status"] == "archived"

    async def test_cancel_task_revision_history(self):
        # Create test tasks in cancelled state

        response = self.client.post("/tasks/submit", json=dict(
            user="testuser",
            task_comment="basic test",
            task_type="test_type",
            task_args={},
            task_function="test_function",
            task_function_args={},
            task_requirements={},
            metadata={},
            status="submitted"
        ))

        response_json = response.json()
        task_id = response_json["task_id"]

        self.client.post("/tasks/cancel", json=dict(
            task_id=task_id,
            status="cancelling",
        ))

        # Verify tasks revision was updated
        revisions = await self._backend.get_task_revision_history(task_id=task_id)
        assert len(revisions) == 2
        assert revisions[0].status == "submitted"
        assert revisions[0].user_id == "testuser"
        assert revisions[1].status == "cancelling"
        assert revisions[1].user_id == "unknown"
