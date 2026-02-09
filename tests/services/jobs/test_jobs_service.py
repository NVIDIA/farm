# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from nv.svc.core import main

from nv.svc.farm.services.jobs.config import FarmJobsConfig
from nv.svc.farm.services.jobs.entrypoint import configure_jobs_service


class TestJobsService(IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        self._url_prefix = FarmJobsConfig().jobs.url_prefix
        configure_jobs_service()
        self.app = main.get_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        super().tearDown()

    async def test_get_status_success(self):
        response = self.client.get(f"{self._url_prefix}/status")
        assert response.status_code == 200
