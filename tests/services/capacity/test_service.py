# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict
from .custom_test_case import CustomIsolatedAsyncioTestCase
from fastapi.testclient import TestClient
from nv.svc.farm.services.capacity.config import FarmCapacityConfig
from nv.svc.farm.services.capacity.managers.settings import SettingsAgentCapacityManager
from nv.svc.farm.services.capacity.router import router
from nv.svc.core import main


class TestCapacityService(CustomIsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()

        self._manager = SettingsAgentCapacityManager([], [])
        self._config = FarmCapacityConfig()
        self._settings = self._config.settings.nv.svc.farm.capacity
        self._url_prefix = self._settings.url_prefix

        core = main.ServicesCore(
            title="capacity",
            description="Farm Capacity Service.",
            version="0.1.0",
        )
        core.register_facility("capacity_manager", self._manager)
        core.register_router(router, prefix=self._url_prefix)
        await self._manager.load_capacities()
        self.app = main.get_app()
        self._client = TestClient(app=self.app)

    async def _configure_capacities(self, capacities: Dict[str, Dict]):
        await self._manager._load_settings_capacities(["farm.test.root"])

    async def asyncTearDown(self):
        self._client = None
        self._manager = None

    async def test_list_capacities(self):
        self.dynaconf_setup(config_name="list_capacities.toml")
        self._manager.updateSettings(self._settings)

        await self._manager._load_settings_capacities(["farm.test.root"])

        res = self._client.post(f"{self._url_prefix}/list", json={}).json()
        self.assertIn(
            {
                "identifier": "foo.bar.limit",
                'capacity': 10,
                'remaining': 10,
                'has_capacity': True,
                'strict': False
            },
            res
        )

        self.assertIn(
            {
                "identifier": "foo.bar",
                'capacity': None,
                'remaining': None,
                'has_capacity': True,
                'strict': True
            },
            res
        )

    async def test_list_capacities_no_capacity(self):
        self.dynaconf_setup(config_name="no_capacities.toml")
        self._manager.updateSettings(self._settings)
        await self._manager._load_settings_capacities(["farm.test.root"])

        res = self._client.post(f"{self._url_prefix}/list", json={"available": True}).json()

        self.assertEqual(
            res,
            [
                {
                    "identifier": "foo.bar",
                    'capacity': None,
                    'remaining': None,
                    'has_capacity': True,
                    'strict': True
                }
            ]
        )

    async def test_list_capacities_strict_no_capacity(self):
        self.dynaconf_setup(config_name="strict_no_capacities.toml")
        self._manager.updateSettings(self._settings)

        await self._manager._load_settings_capacities(["farm.test.root"])
        res = self._client.post(f"{self._url_prefix}/list", json={"available": True}).json()
        self.assertEqual(res, [])

    async def test_list_capacities_ignore_strict_no_capacity(self):
        self.dynaconf_setup(config_name="ignore_strict_no_capacities.toml")
        self._manager.updateSettings(self._settings)

        await self._manager._load_settings_capacities(["farm.test.root"])
        res = self._client.post(f"{self._url_prefix}/list", json={"available": True, "ignore_strict": True}).json()

        self.assertEqual(
            res,
            [
                {
                    "identifier": "foo.bar.limit",
                    'capacity': 10,
                    'remaining': 10,
                    'has_capacity': True,
                    'strict': False
                }
            ]
        )

    async def test_register_capacity_all_fields(self):
        self._client.post(f"{self._url_prefix}/register", json={"identifier": "foo.bar", "capacity": 10, "strict": True})
        res = self._client.post(f"{self._url_prefix}/list", json={}).json()

        self.assertEqual(
            res,
            [
                {
                    "identifier": "foo.bar",
                    'capacity': 10,
                    'remaining': 10,
                    'has_capacity': True,
                    'strict': True
                }
            ]
        )

    async def test_register_capacity_no_capacity_field(self):
        self._client.post(f"{self._url_prefix}/register", json={"identifier": "foo.bar", "strict": True})
        res = self._client.post(f"{self._url_prefix}/list", json={}).json()

        self.assertEqual(
            res,
            [
                {
                    "identifier": "foo.bar",
                    'capacity': None,
                    'remaining': None,
                    'has_capacity': True,
                    'strict': True
                }
            ]
        )

    async def test_register_capacity_no_fields(self):
        self._client.post(f"{self._url_prefix}/register", json={"identifier": "foo.bar"})
        res = self._client.post(f"{self._url_prefix}/list", json={}).json()

        self.assertEqual(
            res,
            [
                {
                    "identifier": "foo.bar",
                    'capacity': None,
                    'remaining': None,
                    'has_capacity': True,
                    'strict': False
                }
            ]
        )

    async def test_acquire_capacity(self):
        self.dynaconf_setup(config_name="list_capacities.toml")
        self._manager.updateSettings(self._settings)
        await self._manager._load_settings_capacities(["farm.test.root"])
        self._client.post(f"{self._url_prefix}/acquire", json={"capacities": ["foo.bar", "foo.bar.limit"]})
        capacity = self._manager._capacities["foo.bar.limit"]
        self.assertEqual(9, await capacity.available_capacity())

    async def test_release_capacity(self):
        self.dynaconf_setup(config_name="list_capacities.toml")
        self._manager.updateSettings(self._settings)
        await self._manager._load_settings_capacities(["farm.test.root"])

        self._client.post(f"{self._url_prefix}/acquire", json={"capacities": ["foo.bar", "foo.bar.limit"]})

        capacity = self._manager._capacities["foo.bar.limit"]
        self.assertEqual(9, await capacity.available_capacity())

        self._client.post(f"{self._url_prefix}/release", json={"capacities": ["foo.bar", "foo.bar.limit"]})

        capacity = self._manager._capacities["foo.bar.limit"]
        self.assertEqual(10, await capacity.available_capacity())
