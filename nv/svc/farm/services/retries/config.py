# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Retries Service Settings."""

from nv.svc.core.utils.config import Config, setting

DEFAULT_MAX_TASK_AGE = 259200
DEFAULT_RETRY_LIMIT = 3


@setting(
    "retries.url_prefix",
    default="/queue/management/retries",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "retries.tags",
    default=["retries"],
    cast=list,
    description="List of tags for the retries service.",
)
@setting(
    "retries.farm_tasks_address",
    default="http://127.0.0.1:8080/queue/management/tasks",
    description="Farm Tasks service address.",
)
@setting(
    "retries.retry_limit",
    cast=int,
    default=DEFAULT_RETRY_LIMIT,
    gte=0,
    description="Maximum number of retries for errored task.",
)
@setting(
    "retries.task_max_age",
    cast=int,
    default=DEFAULT_MAX_TASK_AGE,
    gte=0,
    description="Tasks that exceed this age will be skipped. To disable this check use 0.",
)
@setting(
    "retries.task_type_blocklist",
    cast=list,
    default=[],
    description="Tasks containing blocklisted task types are skipped.",
)
@setting(
    "retries.task_type_blocklist",
    cast=list,
    default=[],
    description="tasks containing blocklisted task functions are skipped.",
)
def FarmRetriesConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.retries configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
