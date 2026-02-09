# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Settings Agent Capacity Manager."""

import importlib
import logging

from typing import List
from dynaconf import Dynaconf

from nv.svc.farm.services.capacity.facilities.base import BaseAgentCapacityManager

from ..capacities.base import AbstractCapacity, DynamicCapacity


class SettingsAgentCapacityManager(BaseAgentCapacityManager):
    """Settings based Capacity Manager."""

    def __init__(self, settings: Dynaconf = None, settings_roots: List[str] = None, capacity_classes: List[str] = None):
        super().__init__(capacity_classes=capacity_classes)
        self._capacities = {}
        self._settings_root = settings_roots or []
        self._settings = settings

    def updateSettings(self, settings: Dynaconf):
        self._settings = settings

    async def load_capacities(self):
        await super().load_capacities()
        await self._load_settings_capacities(self._settings_root)

    async def _load_settings_capacities(self, settings_roots: str):
        if not settings_roots:
            logging.warning("No settings root was set for the Capacity manager. No capacity settings will be loaded")
            return

        for settings_root in settings_roots:
            capacity_settings = self._settings.get(settings_root, {})
            for identifier, args in capacity_settings.items():
                capacity_dict = await DynamicCapacity.async_init(identifier, **(args.to_dict()))
                self._capacities.update(capacity_dict)

    def _resolve_cls(self, import_path: str) -> AbstractCapacity:
        """
        Return the module at the given import path.

        Args:
            import_path (str): Import path from which to resolve a module.

        Returns:
            Any: The module imported from the given path.

        """
        cls_name = import_path.split(".")[-1]
        import_path = import_path.replace(f".{cls_name}", "")
        module = importlib.import_module(import_path)
        return getattr(module, cls_name)

    async def register_capacity(self, identifier: str, capacity: AbstractCapacity):
        self._capacities[identifier] = capacity
