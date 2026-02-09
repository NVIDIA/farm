# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Settings service test case."""
from unittest.mock import patch
from fastapi.testclient import TestClient
from .custom_test_case import CustomIsolatedAsyncioTestCase
from nv.svc.farm.services.settings.utils import get_exposed_settings_key
from nv.svc.farm.services.settings.config import FarmSettingsConfig
from nv.svc.farm.services.settings.entrypoint import main as settings_main
from nv.svc.core import main

class TestServiceSettingsFacility(CustomIsolatedAsyncioTestCase):
    """Settings service test case."""

    def setUp(self) -> None:
        super().setUp()
        self.custom_setup(config_name="service_settings_facility.toml")
        self._config = FarmSettingsConfig()
        self._settings = self._config.settings.nv.svc.farm.settings
        self._url_prefix = self._settings.url_prefix

        settings_main()
        self.app = main.get_app()
        self._client = TestClient(app=self.app)

        self._settings_key = get_exposed_settings_key(package_name=self._config.package_name, service_name="settings")

    def tearDown(self) -> None:
        super().tearDown()

    def test_response_contains_expected_fields(self) -> None:
        """Validate that the response from the service contains the expected model fields."""
        settings_response = self._client.get(f"{self._url_prefix}/settings").json()

        self.assertIn(member="settings", container=settings_response)
        self.assertIsInstance(obj=settings_response["settings"], cls=dict)

    def test_boolean_settings_exposed_can_be_retrieved(self) -> None:
        """Validate that the response contains the boolean settings exposed under the Carbonite's root key."""
        settings_response = self._client.get(f"{self._url_prefix}/settings").json()

        self.assertIn(member="bool", container=settings_response["settings"])
        self.assertIsInstance(obj=settings_response["settings"]["bool"], cls=bool)
        self.assertEqual(
            first=settings_response["settings"]["bool"],
            second=self._settings.exposed_settings.bool,
        )

    def test_integer_settings_exposed_can_be_retrieved(self) -> None:
        """Validate that the response contains the integer settings exposed under the Carbonite's root key."""
        settings_response = self._client.get(f"{self._url_prefix}/settings").json()

        self.assertIn(member="integer", container=settings_response["settings"])
        self.assertIsInstance(obj=settings_response["settings"]["integer"], cls=int)
        self.assertEqual(
            first=settings_response["settings"]["integer"],
            second=self._settings.exposed_settings.integer
        )

    def test_string_settings_exposed_can_be_retrieved(self) -> None:
        """Validate that the response contains the string settings exposed under the Carbonite's root key."""
        settings_response = self._client.get(f"{self._url_prefix}/settings").json()

        self.assertIn(member="string", container=settings_response["settings"])
        self.assertIsInstance(obj=settings_response["settings"]["string"], cls=str)
        self.assertEqual(
            first=settings_response["settings"]["string"],
            second=self._settings.exposed_settings.string
        )

    def test_dictionary_settings_exposed_can_be_retrieved(self) -> None:
        """Validate that the response contains the dictionary settings exposed under the Carbonite's root key."""
        settings_response = self._client.get(f"{self._url_prefix}/settings").json()
        self.assertIn(member="dict", container=settings_response["settings"])
        self.assertIn(member="key", container=settings_response["settings"]["dict"])
        self.assertIsInstance(obj=settings_response["settings"]["dict"], cls=dict)
        self.assertIsInstance(obj=settings_response["settings"]["dict"]["key"], cls=str)
        self.assertEqual(
            first=settings_response["settings"]["dict"],
            second=self._settings.exposed_settings.dict,
        )

    def test_array_settings_exposed_can_be_retrieved(self) -> None:
        """Validate that the response contains the array settings exposed under the Carbonite's root key."""
        settings_response = self._client.get(f"{self._url_prefix}/settings").json()

        self.assertIn(member="string_array", container=settings_response["settings"])
        self.assertIsInstance(obj=settings_response["settings"]["string_array"], cls=list)
        self.assertEqual(
            first=settings_response["settings"]["string_array"],
            second=self._settings.exposed_settings.string_array,
        )
