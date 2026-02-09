# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""GPU Capacity."""

import logging

from collections import defaultdict
from types import ModuleType
from typing import Dict, Optional

from .base import ValueCapacity

pynvml: Optional[ModuleType] = None
try:
    import pynvml
except ImportError:
    pynvml = None
    logging.warning("GpuCapacity: Missing pynvml, no GPU capacity available")


class GPU(ValueCapacity):
    """GPU Capacity."""

    @classmethod
    def _initialize_nvml(cls) -> None:
        global pynvml
        if pynvml is None:
            return

        try:
            pynvml.nvmlInit()
        except pynvml.nvml.NVMLError as err:
            # pynvml is unusable, so delete the module and fall back to no gpu support
            del pynvml
            pynvml = None  # noqa
            logging.warning(f"GpuCapacity: pynvml failed to initialize ({err}), no GPU capacity available")

    @classmethod
    def _shutdown_nvml(cls) -> None:
        if pynvml is None:
            return

        try:
            pynvml.nvmlShutdown()
        except pynvml.nvml.NVMLError:
            pass

    @classmethod
    async def async_init(cls, *args, **kwargs) -> Dict[str, ValueCapacity]:
        if pynvml is None:
            return {}

        listed_gpus: Dict[str, int] = defaultdict(int)
        gpu_capacity: Dict[str, ValueCapacity] = {}
        try:
            cls._initialize_nvml()

            if pynvml is None:
                return {}

            deviceCount = pynvml.nvmlDeviceGetCount()
            for i in range(deviceCount):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpu_id = pynvml.nvmlDeviceGetName(handle)
                try:
                    gpu_id = gpu_id.decode("utf-8")
                except Exception:
                    pass
                identifier = ".".join([chunk.lower() for chunk in gpu_id.split()])
                listed_gpus[identifier] += 1
        finally:
            cls._shutdown_nvml()

        for gpu, count in listed_gpus.items():
            gpu_capacity[gpu] = cls(identifier=gpu, capacity=count)

        return gpu_capacity
