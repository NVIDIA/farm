# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import time

from unittest import mock
from unittest import IsolatedAsyncioTestCase

from nv.svc.core.client.http import HTTPClientSession

from nv.svc.farm.services.retries.facilities import RetryManager
from nv.svc.farm.services.retries.config import FarmRetriesConfig


class TestRetryManager(IsolatedAsyncioTestCase):

    def setUp(self):

        self.retry_endpoint_call_count = 0
        self.retry_endpoint_data = None
        self.update_endpoint_call_count = 0
        self.update_endpoint_data = None

        class FakeResponse:
            async def json(self):
                return {}

        async def _request_spy(*args, **kwargs):
            endpoint = args[2].split("/tasks")[-1]
            if endpoint == "/retry":
                self.retry_endpoint_call_count += 1
                self.retry_endpoint_data = kwargs["json"]
            elif endpoint == "/update":
                self.update_endpoint_call_count += 1
                self.update_endpoint_data = kwargs["json"]
            return FakeResponse()

        self.client_session_patcher = mock.patch.object(HTTPClientSession, "_request", _request_spy)
        self.client_session_patcher.start()

        config = FarmRetriesConfig()
        self._manager = RetryManager(
            farm_tasks_address=config.retries.farm_tasks_address,
            retry_limit=config.retries.retry_limit,
            task_max_age=config.retries.task_max_age,
            task_type_blocklist=config.retries.task_type_blocklist,
            task_function_blocklist=config.retries.task_function_blocklist,
        )

    def tearDown(self):
        self.client_session_patcher.stop()

    def _create_errored_task(self, task_type="test-type", task_function=None, metadata=None):
        return {
            "task_id": "1234",
            "user": "john-doe",
            "task_type": task_type,
            "task_args": {},
            "task_function": task_function or "",
            "task_function_args": {},
            "task_requirements": {},
            "task_comment": "errored task for testing",
            "priority": 65535,
            "status": "errored",
            "metadata": metadata or {},
            "task_submission_time": time.time(),
            "userid": "test-user",
        }

    async def test_run_check_once(self):
        task = self._create_errored_task()
        await self._manager.retry_task(task)

        expected_task_called_with = task.copy()
        expected_metadata = {
            "_retry": {
                "count": 1,
                "limit": self._manager._retry_limit,
                "is_retryable": True,
                "is_done": False,
            }
        }
        expected_task_called_with["details"] = f"Task errored. Retry attempt 1 of {self._manager._retry_limit}"
        expected_task_called_with["metadata"] = expected_metadata

        assert self.retry_endpoint_call_count == 1
        assert self.retry_endpoint_data == expected_task_called_with

    async def test_no_retries_left(self):
        metadata_1 = {
            "_retry": {
                "is_retryable": True,
                "count": self._manager._retry_limit,
                "limit": self._manager._retry_limit,
            }
        }
        task_1 = self._create_errored_task(metadata=metadata_1)

        # test task with retry count exceeded
        metadata_2 = metadata_1.copy()
        metadata_2["_retry"]["count"] = self._manager._retry_limit + 1
        task_2 = self._create_errored_task(metadata=metadata_2)

        await self._manager.retry_task(task_1)
        assert self.retry_endpoint_call_count == 0

        await self._manager.retry_task(task_2)
        assert self.retry_endpoint_call_count == 0

    async def test_is_retryable_disabled_is_skipped(self):
        # ensure task with is_retryable=False does not retry.
        metadata = {
            "_retry": {
                "is_retryable": False
            }
        }
        task = self._create_errored_task(metadata=metadata)

        await self._manager.retry_task(task)
        assert self.retry_endpoint_call_count == 0

    async def test_blocklisted_task_type_is_skipped(self):
        task_type = "create-render"
        self._manager._task_type_blocklist = [task_type]
        task = self._create_errored_task(task_type=task_type)

        await self._manager.retry_task(task)
        assert self.retry_endpoint_call_count == 0

    async def test_blocklisted_task_function_is_skipped(self):
        task_function = "render-it"
        self._manager._task_function_blocklist = [task_function]
        task = self._create_errored_task(task_function=task_function)

        await self._manager.retry_task(task)
        assert self.retry_endpoint_call_count == 0

    async def fixme_test_task_max_age_exceeded_is_skipped(self):
        self._manager._task_max_age = 1
        task = self._create_errored_task()
        await asyncio.sleep(1.5)

        await self._manager.retry_task(task)
        assert self.retry_endpoint_call_count == 0
