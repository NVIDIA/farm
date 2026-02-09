# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Dynaconf store settings interface."""

from typing import Any
from functools import reduce
from dynaconf import LazySettings
from .base import BaseReadOnlySettingStore


class DynaConfSettingsStore(BaseReadOnlySettingStore):
    """Dynaconf store settings interface."""

    def __init__(self, settings: LazySettings = None, settings_root: str = None):
        """Initialize Dynaconf Settings Store.

        Args:
            settings (dynaconf.LazySettings): A dependency-injectable instance of Carbonite's settings store to use.

        Kwargs:
            settings_root (str): Root from which to start retrieving settings

        Returns:
            None

        """
        self._settings = settings
        self._settings_root = settings_root

    async def get_setting(self, path: str) -> Any:
        """
        Return the setting at the given path.

        Args:
            path (str): Path of the setting to return.

        Returns:
            Any: The setting at the given path.

        """

        if not self._settings_root:
            return reduce(lambda a, b: getattr(a, b), path.split("."), self._settings)

        path = f"{self._settings_root}.{path}"
        return reduce(lambda a, b: getattr(a, b), path.split("."), self._settings)

    @property
    def store(self) -> LazySettings:
        """
        Returns a reference to the underlying DynaConf settings store used by the facility.

        Args:
            None

        Returns:
            dynaconf.LazySettings: A reference to the underlying Dynaconf settings store used by the facility.

        """
        return self._settings
