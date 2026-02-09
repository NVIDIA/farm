# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm DAG Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "dag.url_prefix",
    default="/queue/management/dag",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the DAG service.",
)
@setting(
    "dag.tags",
    default=["dag"],
    cast=list,
    description="List of tags for the DAG service.",
)
@setting(
    "dag.database",
    default={
        "handle": "dag",
        "type": "sqlite",
        "connection_string": "sqlite:///dag.db"
    },
    description="DAG service database configuration.",
)
@setting(
    "dag.task_service_url",
    default="http://localhost:8222/queue/management/tasks",
    description="Base URL for the task service.",
)
def FarmDAGConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.dag configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
