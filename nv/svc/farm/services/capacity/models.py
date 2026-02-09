# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Capacity Model Representations."""

from typing import List
import pydantic


class DynamicCapacityModel(pydantic.BaseModel):
    """Dynamic Capacity Model."""

    identifier: str = pydantic.Field(...,
                                     title="Capacity identifier",
                                     description="Dotnotation capacity identifier. ie: os.linux.ubuntu.18_04")
    capacity: int = pydantic.Field(None,
                                   title="Capacity value",
                                   description="Optional capacity value. If None, tasks will be selected for this capacity but will not be limited by.")
    strict: bool = pydantic.Field(False,
                                  title="Strict capacity",
                                  description="When set to True only tasks requiring this capacity will be selected by the agent. "
                                  "This can be used to assign an agent to a specific user for example.")


class CapacityList(pydantic.BaseModel):
    """List Capacity Model."""

    capacities: List[str] = pydantic.Field(...,
                                           title="Capacity keys",
                                           description="List of capacities")


class ListAvailable(pydantic.BaseModel):
    """List Available Capacity Model."""

    available: bool = pydantic.Field(False,
                                     title="List available",
                                     description="Limit returned value to available capacity only")
    ignore_strict: bool = pydantic.Field(False,
                                         title="Ignore strict",
                                         description="When False (default) if there is no availability for strict capacities then no capacity is available.")
