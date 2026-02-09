# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Capacity Service Router."""

from nv.svc.core import routers

from nv.svc.farm.services.capacity import DynamicCapacity
from nv.svc.farm.services.capacity.managers.base import BaseAgentCapacityManager
from nv.svc.farm.services.capacity.models import CapacityList, DynamicCapacityModel, ListAvailable

router = routers.ServiceAPIRouter()


# Explicitely making this a post to avoid the temptation of caching this data by default.
@router.post("/list")
async def list(
    settings: ListAvailable,
    manager: BaseAgentCapacityManager = router.get_facility("capacity_manager")
):
    """List all capacities."""
    capacities = await manager.list()

    if not settings.available:
        return capacities

    filtered_data = []
    for capacity in capacities:
        if capacity["has_capacity"]:
            filtered_data.append(capacity)
            continue

        if capacity["strict"] and not settings.ignore_strict:
            return []

    return filtered_data


@router.post("/register")
async def register(
    capacity: DynamicCapacityModel,
    manager: BaseAgentCapacityManager = router.get_facility("capacity_manager")
):
    """Register new capacity."""
    new_capacity = DynamicCapacity(capacity.identifier, capacity=capacity.capacity, strict=capacity.strict)
    return await manager.register_capacity(capacity.identifier, new_capacity)


@router.post("/acquire")
async def acquire(
    data: CapacityList,
    manager: BaseAgentCapacityManager = router.get_facility("capacity_manager")
):
    """Acquire Capacity."""
    await manager.acquire_capacities(data.capacities)


@router.post("/release")
async def release(
    data: CapacityList,
    manager: BaseAgentCapacityManager = router.get_facility("capacity_manager")
):
    """Release Capacity."""
    await manager.release_capacities(data.capacities)
