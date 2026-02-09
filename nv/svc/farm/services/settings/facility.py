# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Service settings facility."""

from typing import Any

import nv.svc.core.facilities.base as _facilities

from .stores import BaseReadOnlySettingStore


class ServiceSettingsFacility(_facilities.Facility):
    """Service settings facility."""

    def __init__(self, settings_store: BaseReadOnlySettingStore) -> None:
        """Initialize Service Settings Facility.

        Args:
            settings_store (BaseReadOnlySettingStore): Settings store from which to retrieve settings.

        Returns:
            None

        """
        self._settings_store = settings_store

    async def get_setting(self, path: str) -> Any:
        """
        Return the setting at the given path.

        Args:
            path (str): Path of the setting to return.

        Returns:
            Any: The setting at the given path.

        """
        return await self._settings_store.get_setting(path=path)

    @property
    def settings_store(self) -> BaseReadOnlySettingStore:
        """
        Returns a reference to the underlying settings store used by the facility.

        Args:
            None

        Returns:
            BaseReadOnlySettingStore: A reference to the underlying settings store used by the facility.

        """
        return self._settings_store
