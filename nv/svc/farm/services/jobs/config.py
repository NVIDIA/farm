# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "jobs.url_prefix",
    default="/queue/management/jobs",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "jobs.tags",
    default=["jobs"],
    cast=list,
    description="List of tags for the jobs service.",
)
@setting(
    "jobs.api_key",
    default="change-me",
    description="Jobs Store ApiKey.",
)
@setting(
    "jobs.store_class",
    default="nv.svc.farm.services.jobs.facilities.store.base.BaseJobStore",
    description="Jobs store class to use.",
)
@setting(
    "jobs.store_args",
    default={},
    description="Jobs store class args to use.",
)
@setting(
    "jobs.new_job_definition_save_location",
    default="",
    description="Specify a new job definition save location for DirectoryJobStore.",
)
@setting(
    "jobs.supported_instance_payload_versions",
    default=[],
    cast=list,
    description="Supported instance payload versions.",
)
@setting(
    "jobs.agent_assigned_gpu",
    cast=int,
    description="Agent assigned GPU ID.",
)
@setting(
    "jobs.farm_facilities_extensions",
    default="",
    description="List of farm facilities extensions.",
)
@setting(
    "jobs.agent_controller_protocol",
    default="http",
    description="The agent controller protocol.",
)
@setting(
    "jobs.agent_controller_host",
    default="localhost",
    description="The agent controller host.",
)
@setting(
    "jobs.agent_controller_port",
    cast=int,
    default=8011,
    description="The agent controller port.",
)
@setting(
    "jobs.agent_controller_path",
    default="/agent",
    description="The agent controller path.",
)
@setting(
    "jobs.k8s_manager.active_check_delay",
    default=30,
    cast=int,
    description="KubernetesProcessManager: active instances check delay.",
)
@setting(
    "jobs.k8s_manager.log_check_delay",
    default=15,
    cast=int,
    description="KubernetesProcessManager: log interval check delay.",
)
@setting(
    "jobs.k8s_manager.jobs_namespace",
    default="ov-farm",
    description="KubernetesProcessManager: namespace to use for k8s jobs.",
)
@setting(
    "jobs.k8s_manager.request_timeout_in_seconds",
    default=60,
    cast=int,
    description="KubernetesProcessManager: Client request timeout in seconds.",
)
@setting(
    "jobs.k8s_manager.ttl_seconds_after_finished",
    cast=int,
    description="KubernetesProcessManager: adds ttlSecondsAfterFinished to the Kubernetes job spec.",
)
@setting(
    "jobs.k8s_manager.job_template_spec_overrides_file",
    description="KubernetesProcessManager: job template spec fields overrides file.",
)
@setting(
    "jobs.k8s_manager.container_spec_overrides_file",
    description="KubernetesProcessManager: container spec fields overrides file.",
)
@setting(
    "jobs.k8s_manager.log_upload_interval",
    default=10,
    cast=int,
    description="KubernetesProcessManager: Log upload interval.",
)
@setting(
    "jobs.k8s_manager.log_upload_endpoint",
    description="KubernetesProcessManager: Log upload endpoint.",
)
@setting(
    "jobs.k8s_manager.list_jobs_limit_per_page",
    default=250,
    cast=int,
    gte=1,
    description="KubernetesProcessManager: Maximum number of jobs to return per page when listing jobs.",
)
def FarmJobsConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.jobs configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
