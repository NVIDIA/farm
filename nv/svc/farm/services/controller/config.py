# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "controller.url_prefix",
    default="/agent",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "controller.tags",
    default=["controller"],
    cast=list,
    description="List of tags for the controller service.",
)
@setting(
    "controller.task_backend_class",
    default="nv.svc.farm.services.tasks.facilities.tasks.backends.TaskIdDictBackend",
    description="Task backend store class to use.",
)
@setting(
    "controller.task_backend_args",
    default={},
    description="Task backend args to use.",
)
@setting(
    "controller.bay_controller_class",
    default="nv.svc.farm.services.controller.facilities.bays.OneSlotBay",
    description="Bay controller class to use.",
)
@setting(
    "controller.bay_controller_args",
    default={},
    description="Bay controller class args to use.",
)
@setting(
    "controller.agent_checkin_interval",
    default=60,
    cast=int,
    gte=1,
    description="Agent checkin interval.",
)
@setting(
    "controller.fetch_task_idle_delay",
    default=10,
    cast=int,
    gte=1,
    description="Task idle delay.",
)
@setting(
    "controller.fetch_task_delay",
    default=0.5,
    cast=float,
    gte=0.0,
    description="Task fetch delay.",
)
@setting(
    "controller.task_checkin_interval",
    default=10,
    cast=int,
    gte=1,
    description="Task checkin interval.",
)
@setting(
    "controller.task_checkin_timeout",
    default=30,
    cast=int,
    gte=0,
    description="Task checkin timeout.",
)
@setting(
    "controller.reconcile_task_state",
    default=False,
    cast=bool,
    description="Reconcile the task state upon startup.",
)
@setting(
    "controller.task_reconcile_interval",
    default=3600,
    cast=int,
    gte=1,
    description="Task reconcile interval.",
)
@setting(
    "controller.public_to_private_source_queue_hostnames",
    default=[],
    cast=list,
    description="List of service host mappings between public to private hostname for farm.",
)
@setting(
    "controller.service_host_url_format_str",
    default="{service_host}/queue/management",
    description="Farm service base url format string. Used for resolving public to private source queue hostname.",
)
@setting(
    "controller.agents_service_url",
    default="http://127.0.0.1:8011/queue/management/agents",
    description="The Agents service url.",
)
@setting(
    "controller.tasks_service_url",
    default="http://127.0.0.1:8011/queue/management/tasks",
    description="The Tasks service url.",
)
@setting(
    "controller.labels",
    default=[],
    cast=list,
    description=(
        "Labels by which to select tasks. "
        "Only tasks with the given labels, at submission, will be selected by the controller.",
    )
)
@setting(
    "controller.job_store_class",
    default="nv.svc.farm.services.jobs.facilities.store.base.BaseJobStore",
    description="Jobs store class to use.",
)
@setting(
    "controller.job_store_args",
    default={},
    description="Jobs store class args to use.",
)
@setting(
    "controller.job_manager_class",
    default="nv.svc.farm.services.jobs.facilities.manager.base.ProcessManager",
    description="Jobs manger class to use.",
)
@setting(
    "controller.job_manager_args",
    default={},
    description="Jobs manager class args to use.",
)
def FarmControllerConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.controller configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
