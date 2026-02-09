# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Service settings facility store test case."""


from .custom_test_case import CustomIsolatedAsyncioTestCase

from nv.svc.farm.services.settings.facility import ServiceSettingsFacility
from nv.svc.farm.services.settings.stores import DynaConfSettingsStore

class TestServiceSettingsStore(CustomIsolatedAsyncioTestCase):
    """Service settings facility store test case."""

    def setUp(self) -> None:
        super().setUp()
        self.dynaconf_setup(config_name="service_setting_store.toml")
        self._facility = ServiceSettingsFacility(
            settings_store=DynaConfSettingsStore(settings=self._settings),
        )

    def tearDown(self) -> None:
        super().tearDown()
        self._settings = None
        self._facility = None

    async def test_boolean_settings_can_be_retrieved_from_carbonite(self) -> None:
        """Validate that boolean values can be retrieved from Carbonite settings."""
        bool_setting = await self._facility.get_setting("test.bool")
        self.assertIsInstance(bool_setting, bool)
        self.assertEqual(bool_setting, True)

    async def test_integer_settings_can_be_retrieved_from_carbonite(self) -> None:
        """Validate that integer values can be retrieved from Carbonite settings."""
        int_setting = await self._facility.get_setting("test.int")
        self.assertIsInstance(int_setting, int)
        self.assertEqual(int_setting, 13)

    async def test_string_settings_can_be_retrieved_from_carbonite(self) -> None:
        """Validate that string values can be retrieved from Carbonite settings."""
        string_setting = await self._facility.get_setting("test.string")
        self.assertIsInstance(string_setting, str)
        self.assertEqual(string_setting, "lorem ipsum")

    async def test_settings_return_their_value_at_the_moment_of_retrieval(self) -> None:
        """Validate that values retrieved from Carbonite settings return their latest values."""
        self._settings.test.transient_value = 23
        transient_setting = await self._facility.get_setting("test.transient_value")
        self.assertEqual(transient_setting, 23)

    async def test_settings_from_specific_root(self) -> None:
        """Validate that values can be retrieved from a sub path tree if a root is specified"""

        self._facility = ServiceSettingsFacility(
            settings_store=DynaConfSettingsStore(settings=self._settings, settings_root="test"),
        )

        transient_setting = await self._facility.get_setting("transient_value")
        self.assertEqual(transient_setting, 17)
