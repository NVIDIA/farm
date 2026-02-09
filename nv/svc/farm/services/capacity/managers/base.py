# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base Agent Capacity Manager."""

__all__ = ["BaseAgentCapacityManager"]

import abc
import logging

from typing import Dict, List


from nv.svc.core.facilities.base import Facility
from nv.svc.farm.services.capacity.capacities.base import AbstractCapacity


class BaseAgentCapacityManager(Facility, abc.ABC):
    """Manage and control available capacity."""

    def __init__(self, capacity_classes: List[str] = None):
        super().__init__()
        self._capacity_classes = capacity_classes or []
        self._capacities: Dict[str, AbstractCapacity] = {}

    @abc.abstractmethod
    async def register_capacity(self, identifier: str, capacity: AbstractCapacity):
        pass

    async def list(self):
        capacities = []
        for _, capacity in self._capacities.items():
            capacities.append(await capacity.to_dict())

        return capacities

    async def load_capacities(self):
        await self._load_capacity_classes(self._capacity_classes)

    async def _load_capacity_classes(self, capacity_classes: List[str]) -> None:
        """
        Load a list of capacity classes by import path and add them to the list of capacities for this agent.

        Args:
            capacity_classes (list[str]): List of import paths for AbstractCapity classes
        """

        for import_path in capacity_classes:
            cls = self._resolve_cls(import_path)
            try:
                self._capacities.update(await cls.async_init())
            except Exception as exc:
                logging.error(f"Failed to load capacities for {import_path}: {exc}")

    async def acquire_capacities(self, capacities: List[str]):
        """
        Acquire resources for all capacities in the list.

            Args:
                capacities (list[str]): List of capacities to acquire
        """
        for capacity in capacities:
            await self._capacities[capacity].acquire_capacity()

    async def release_capacities(self, capacities: List[str]):
        """
        Releases resources for all capacities in the list.

        Args:
            capacities (list[str]): List of capacities to release
        """

        for capacity in capacities:
            await self._capacities[capacity].release_capacity()
