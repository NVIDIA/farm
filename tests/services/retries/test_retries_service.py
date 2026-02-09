# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import time

from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from nv.svc.core import main

from nv.svc.farm.services.retries.config import FarmRetriesConfig
from nv.svc.farm.services.retries.entrypoint import configure_retries_service


class FakeRetryManager:
    def __init__(self, *args, **kwargs):
        pass

    async def retry_task(self, task):
        pass


class TestRetriesService(IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        self._url_prefix = FarmRetriesConfig().retries.url_prefix

        self.retry_manager_patcher = patch("nv.svc.farm.services.retries.facilities.RetryManager", FakeRetryManager)
        self.retry_manager_patcher.start()

        configure_retries_service()

        self.app = main.get_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.retry_manager_patcher.stop()
        super().tearDown()

    def test_submit_endpoint(self):
        """Test the submit endpoint."""
        task = {
            "task_id": "1234",
            "user": "john-doe",
            "task_type": "test-type",
            "task_args": {},
            "task_function": "",
            "task_function_args": {},
            "task_requirements": {},
            "task_comment": "errored task for testing",
            "priority": 65535,
            "status": "errored",
            "metadata": {},
            "task_submission_time": time.time(),
            "userid": "test-user",
        }

        payload = {
            "new_task_state": task,
            "old_task_state": task,
        }
        response = self.client.post(f"{self._url_prefix}/submit", json=payload)
        assert response.status_code == 200
