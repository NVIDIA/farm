# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "results.url_prefix",
    default="/queue/management/results",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "results.manager_class",
    default="nv.svc.farm.services.results.facilities.managers.redis.RedisResultManager",
    description="Result manager class to use.",
)
@setting(
    "results.manager_args",
    default={},
    description="Result manager class args to use.",
)
@setting(
    "results.task_service_url",
    default="http://localhost:8222/queue/management/tasks",
    description="URL for the task service to fetch task metadata.",
)
@setting(
    "results.result_ttl",
    default=432000,  # 5 days in seconds (5 * 24 * 60 * 60)
    description="TTL for result keys in seconds. Default: 5 days.",
)
def FarmResultsConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.results configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
