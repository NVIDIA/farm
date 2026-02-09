# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from nv.svc.core import main
from nv.svc.farm.services.controller.router import router


class TestAgentTaskService(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        _fake_data = {
            "abcd": {
                "task_id": "abcd",
                "task_function": "func_bark",
                "task_type": "type_foo",
                "userid": "userId1",
                "status": "submitted"
            }
        }

        class FakeTaskManager:
            def __init__(self, data):
                self.data = data

            async def get_task(self, task_id):
                return self.data[task_id]

            async def set_task_finished(self, task_id):
                self.data[task_id]["status"] = "finished"

            async def set_task_errored(self, task_id, reason):
                self.data[task_id]["status"] = "errored"

            async def task_checkin(self, task_id, **_kwargs):
                self.data[task_id]

            async def get_logs(self, task_id):
                self.data[task_id]
                return "fake-log-data"

        self._fake_task_manager = FakeTaskManager(_fake_data)

        core = main.ServicesCore(
            title="controller",
            description="Farm Controller",
            version="0",
        )
        core.register_facility("task_manager", self._fake_task_manager)
        # no prefix to make it simple in tests.
        core.register_router(router)
        self._client = TestClient(core._app)

    async def test_retrieve(self):
        response = self._client.get("/task/retrieve?task_id=abcd")
        self.assertEqual(response.status_code, 200)
        task = response.json()
        self.assertEqual(task["task_id"], "abcd")
        self.assertEqual(task["task_function"], "func_bark")
        self.assertEqual(task["task_type"], "type_foo")
        self.assertEqual(task["userid"], "userId1")

    async def test_retrieve_not_found(self):
        response = self._client.get("/task/retrieve?task_id=i-dont-exist")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Task does not exist.")

    async def test_finished(self):
        response = self._client.post("/task/finished", json={"task_id": "abcd"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._fake_task_manager.data["abcd"]["status"], "finished")

    async def test_finished_not_found(self):
        response = self._client.post("/task/finished", json={"task_id": "i-dont-exist"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Task does not exist.")

    async def test_errored(self):
        response = self._client.post("/task/errored", json={"task_id": "abcd"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._fake_task_manager.data["abcd"]["status"], "errored")

    async def test_errored_not_found(self):
        response = self._client.post("/task/errored", json={"task_id": "i-dont-exist"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Task does not exist.")

    async def test_checkin(self):
        response = self._client.post("/task/checkin", json={"task_id": "abcd"})
        self.assertEqual(response.status_code, 200)

    async def test_checkin_not_found(self):
        response = self._client.post("/task/checkin", json={"task_id": "i-dont-exist"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Task does not exist.")

    async def test_logs(self):
        response = self._client.get("/task/logs?task_id=abcd")
        self.assertEqual(response.status_code, 200)

    async def test_logs_not_found(self):
        response = self._client.get("/task/logs?task_id=i-dont-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No logs found for task ID i-dont-exist", response.json()["detail"])
