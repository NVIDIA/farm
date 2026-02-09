# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""CPU Capacity."""

import psutil

from typing import Union

from .base import AbstractCapacity


class CPU(AbstractCapacity):
    """CPU Capacity."""

    def __init__(self, strict: bool = False) -> None:
        super().__init__(strict=strict)
        self._identifier = "cpu"

    async def available_capacity(self) -> Union[int, None]:
        return None

    async def has_capacity(self) -> bool:
        # OV Farm currently has no portable way, across OS'es, to limit CPU resources used by a process running on baremetal.
        # This is why it will not calculate remaining CPUs after aqcuiring it as a resource.
        # To limit the amount of processes on an agent a dynamic resource can be configured.
        if await super().has_capacity():
            return True

        return True

    async def _set_initial_capacity(self):
        self._capacity = psutil.cpu_count()

    async def acquire_capacity(self) -> bool:
        # OV Farm currently has no portable way, across OS'es, to limit CPU resources used by a process running on baremetal.
        # This is why it will not calculate remaining CPUs after aqcuiring it as a resource.
        # To limit the amount of processes on an agent a dynamic resource can be configured.
        return True

    async def release_capacity(self) -> bool:
        # OV Farm currently has no portable way, across OS'es, to limit CPU resources used by a process running on baremetal.
        # This is why it will not calculate remaining CPUs after aqcuiring it as a resource.
        # To limit the amount of processes on an agent a dynamic resource can be configured.
        return True
