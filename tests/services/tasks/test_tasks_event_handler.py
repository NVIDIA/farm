# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
from unittest import mock, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from nv.svc.farm.services.tasks.facilities.task_events.status import TaskStatusEventHandler


class AsyncMagicMock(mock.MagicMock):
    """Async equivalent of MagicMock class"""
    def __call__(self, *args, **kwargs):
        sup = super(AsyncMagicMock, self)
        async def coro():
            return sup.__call__(*args, **kwargs)
        return coro()

    def __await__(self):
        return self().__await__()


async def async_noop():
    # helper for triggering next event on asyncio loop
    await asyncio.sleep(0)


class TestTaskEventHandler(IsolatedAsyncioTestCase):

    def setUp(self):
        mock_response = AsyncMock(name="mock-response")
        mock_response.post.return_value = AsyncMock(name="mock-data")

        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_response

        self.client_session_patcher = patch("nv.svc.core.client.http.HTTPClientSession", return_value=mock_session)
        self.client_session_patcher.start()

        self._handler = TaskStatusEventHandler(
            retries_service_url="http://localhost:1234/queue/management/retries",
        )
        self._handler_future = asyncio.ensure_future(self._handler.start())

    async def asyncTearDown(self):
        if self._handler_future:
            await self._handler.stop()
            self._handler_future.cancel()
        self.client_session_patcher.stop()

    def _create_task(self, status):
        return {
            "metadata": {},
            "priority": 1,
            "status": status,
            "task_type": "test-task-type",
            "task_args": {},
            "task_function": "",
            "task_function_args": {},
            "task_requirements": {},
            "task_comment": "task for testing",
            "userid": "test-user",
        }

    async def test_push_event(self):
        status = "errored"
        event_type = f"status_{status}"
        task = self._create_task(status=status)

        self._handler.push_event(event_type, old_task_state=task, new_task_state=task)
        # noop to help with moving async loop to executing the underlying call to TaskStatusEventHandler._event_queue.get()
        await async_noop()

        self.assertTrue(self._handler.event_handler_exists(event_type))
        self.assertTrue(self._handler._event_queue.empty())

    async def test_no_event_handler_exists(self):
        status = "test_foobar"
        event_type = f"status_{status}"
        task = self._create_task(status=status)

        self._handler.push_event(event_type, old_task_state=task, new_task_state=task)
        await async_noop()

        self.assertFalse(self._handler.event_handler_exists(event_type))
        self.assertTrue(self._handler._event_queue.empty())
