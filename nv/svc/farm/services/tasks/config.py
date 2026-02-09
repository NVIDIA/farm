# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Tasks Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "tasks.url_prefix",
    default="/queue/management/tasks",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "tasks.tags",
    default=["tasks"],
    cast=list,
    description="List of tags for the tasks service.",
)
@setting(
    "tasks.dbs",
    default={},
    description="Tasks database manager arguments.",
)
@setting(
    "tasks.metrics_collect_interval",
    default=60,
    gte=1,
    description="the time interval in seconds to collect task metrics",
)
@setting(
    "tasks.event_handlers",
    default=[
        "nv.svc.farm.services.tasks.facilities.task_events.status.TaskStatusEventHandler",
        "nv.svc.farm.services.dag.facilities.task_events.DAGTaskEventHandler"
    ],
    cast=list,
    description="List of event handler classes to load",
)
@setting(
    "tasks.event_handler_args",
    default={
        "TaskStatusEventHandler": {
            "retries_service_url": "http://localhost:8222/queue/management/retries"
        },
        "DAGTaskEventHandler": {
            "dag_service_url": "http://localhost:8222/queue/management/dag"
        }
    },
    description="Arguments for event handlers, keyed by handler class name",
)
@setting(
    "tasks.dag_service_url",
    default="http://localhost:8222/queue/management/dag",
    description="Base URL for the dag service.",
)
def FarmTasksConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.tasks configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
