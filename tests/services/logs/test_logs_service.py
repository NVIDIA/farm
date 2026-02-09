# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from nv.svc.core import main
from nv.svc.farm.services.logs.config import FarmLogsConfig
from nv.svc.farm.services.logs.entrypoint import configure_logs_service


class FakeStore:
    def __init__(self, *args, **kwargs):
        pass

    async def get_logs(self, *args, **kwargs):
        return {"logs": "foobar"}

    async def set_logs(self, *args, **kwargs):
        pass


class TestLogsService(IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        self._url_prefix = FarmLogsConfig().logs.url_prefix

        self.store_patcher = patch("nv.svc.farm.services.logs.facilities.memory.MemoryLogStore", FakeStore)
        self.store_patcher.start()

        configure_logs_service()

        self.app = main.get_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.store_patcher.stop()
        super().tearDown()

    async def test_get_status_success(self):
        response = self.client.get(f"{self._url_prefix}/status")
        assert response.status_code == 200

    async def test_download_logs(self):
        response = self.client.get(f"{self._url_prefix}/download/123456")
        assert response.status_code == 200

    async def test_get_logs(self):
        response = self.client.get(f"{self._url_prefix}/123456")
        assert response.status_code == 200

    async def test_upload_logs(self):
        payload = {"agent_id": "foo-bar", "task_id": "123", "logs": "INFO: hello."}
        response = self.client.post(f"{self._url_prefix}/upload", json=payload)
        assert response.status_code == 200
