# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Service settings facility test case."""

from typing import Any


from unittest import IsolatedAsyncioTestCase
from nv.svc.farm.services.settings.facility import BaseReadOnlySettingStore, ServiceSettingsFacility


class InMemoryMockTestSettingsStore(BaseReadOnlySettingStore):
    """In-memory test settings store."""

    async def get_setting(self, path: str) -> Any:
        return None


class TestServiceSettingsFacility(IsolatedAsyncioTestCase):
    """Service settings facility test case."""

    def setUp(self) -> None:
        super().setUp()
        self._facility = ServiceSettingsFacility(settings_store=InMemoryMockTestSettingsStore())

    def tearDown(self) -> None:
        super().tearDown()
        self._facility = None

    async def test_getting_a_reference_to_the_settings_store_returns_its_actual_instance(self) -> None:
        """Validate that getting a reference to the settings store of the facility returns its actual instance."""
        self.assertIsInstance(obj=self._facility.settings_store, cls=InMemoryMockTestSettingsStore)
        self.assertIsInstance(obj=self._facility.settings_store, cls=BaseReadOnlySettingStore)
