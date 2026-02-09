# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Agents Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "agents.url_prefix",
    default="/queue/management/agents",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "agents.tags",
    default=["agents"],
    cast=list,
    description="List of tags for the agents service.",
)
@setting(
    "agents.lost_timeout",
    default=300,
    cast=int,
    description="Timeout after which a farm agent is considered lost if it has not checked in.",
)
@setting(
    "agents.check_interval",
    default=120,
    cast=int,
    description=(
        "Interval indicating how often to check if agents have checked in."
        " This value needs to be smaller than the lost_timeout"
    )
)
@setting(
    "agents.farm_tasks_address",
    default="http://127.0.0.1:8011/queue/management/tasks",
    description="Farm Tasks address.",
)
@setting(
    "agents.manager_class",
    default="nv.svc.farm.services.agents.facilities.managers.memory.DictAgentManager",
    description="Agent manager class to use.",
)
@setting(
    "agents.manager_args",
    default={},
    description="Agent manager class args to use.",
)
def FarmAgentsConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.agents configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
