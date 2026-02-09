# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import time

from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient
from nv.svc.core import main

from nv.svc.farm.services.agents.config import FarmAgentsConfig
from nv.svc.farm.services.agents.entrypoint import configure_agents_service


class TestAgentsService(IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        self._url_prefix = FarmAgentsConfig().agents.url_prefix
        configure_agents_service()

        self.app = main.get_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        super().tearDown()

    def test_status_endpoint(self):
        """Test the status endpoint."""
        response = self.client.get(f"{self._url_prefix}/status")
        assert response.status_code == 200

    # TODO: add actual tests :)
