# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Memory Capacity."""

import psutil

from typing import Union

from .base import AbstractCapacity


class Memory(AbstractCapacity):
    """Memory Capacity."""

    def __init__(self, strict: bool = False) -> None:
        super().__init__(strict=strict)
        self._identifier = "memory"
        self._minimum_ram_required = 1 * 1024 * 1024 * 1024  # Miminum of 1 GB required to start new jobs.

    async def available_capacity(self) -> Union[int, None]:
        return int(psutil.virtual_memory().available)

    async def _set_initial_capacity(self):
        self._capacity = psutil.virtual_memory().total

    async def has_capacity(self) -> bool:
        if await super().has_capacity():
            return True

        return psutil.virtual_memory().available > self._minimum_ram_required

    async def acquire_capacity(self) -> bool:
        # Relying on has_capacity having made sure that there is at least a minimum amount of ram available.
        return True

    async def release_capacity(self) -> bool:
        return True
