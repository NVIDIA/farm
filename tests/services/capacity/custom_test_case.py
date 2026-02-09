# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import IsolatedAsyncioTestCase
from dynaconf import Dynaconf

class CustomIsolatedAsyncioTestCase(IsolatedAsyncioTestCase):

    def custom_setup(self, config_name=None) -> None:
        self.path = None
        if config_name:
            self.path = os.path.join(os.path.abspath("."), "tests", "services", "capacity", "data", config_name)
            os.environ["NV__SVC__FARM__CONFIG_FILEPATH"] = self.path

    def dynaconf_setup(self, config_name=None) -> None:
        """Uses DynaConf only to load settings."""
        self.custom_setup(config_name=config_name)
        _nested_separator = "__"  # maintain the same separated used by default in applications
        self._settings = Dynaconf(
            settings_files=[self.path],
            core_loaders=["TOML"],
            load_dotenv=False,
            environments=True,
            envvar_prefix=False,
            nested_separator=_nested_separator,
            dotted_lookup=True,
            default_env="settings",
            env="settings",
            merge_enabled=True,
            apply_default_on_none=True,
        )

    def tearDown(self) -> None:
        os.environ.pop("NV__SVC__FARM__CONFIG_FILEPATH", None)
        super().tearDown()
