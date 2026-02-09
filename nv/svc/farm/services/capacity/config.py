# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Capacity Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "capacity.url_prefix",
    default="/capacity",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "capacity.manager_class",
    default="nv.svc.farm.services.capacity.managers.settings.SettingsAgentCapacityManager",
    description="Capacity manager class to use.",
)
@setting(
    "capacity.manager_args",
    default={
        "capacity_classes":
            [
                "nv.svc.farm.services.capacity.GPU",
                "nv.svc.farm.services.capacity.CPU",
                "nv.svc.farm.services.capacity.Memory",
                "nv.svc.farm.services.capacity.OS",
            ],
        "settings_roots":
            [
                "nv.svc.farm.services.capacity"
            ]
    },
    description="Arguments to pass to capacity.manager_class.",
)
@setting(
    "capacity.tags",
    default=["agents"],
    cast=list,
    description="List of tags for the capacity service.",
)
def FarmCapacityConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.capacity configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
