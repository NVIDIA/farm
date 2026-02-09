# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Logs Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "logs.url_prefix",
    default="/queue/management/logs",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "logs.tags",
    default=["logs"],
    cast=list,
    description="List of tags for the logs service.",
)
@setting(
    "logs.max_tasks",
    cast=int,
    default=1_000,
    gte=1,
    description="Maximum number of tasks for MemoryLogStore.",
)
@setting(
    "logs.max_log_entries",
    cast=int,
    default=1_000,
    gte=1,
    description="Maximum number logs entries.",
)
@setting(
    "logs.store_class",
    default="nv.svc.farm.services.logs.facilities.memory.MemoryLogStore",
    description="Log store class to use.",
)
@setting(
    "logs.store_args",
    default={},
    description="Log store class args to use.",
)
def FarmLogsConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.logs configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
