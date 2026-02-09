# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Job Types Kit."""

from typing import List

from nv.svc.farm.services.jobs.config import FarmJobsConfig
from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.job_types.base import BaseJob


class KitJob(BaseJob):
    """
    Kit application job.

    Spawns an instance of kit based on a given experience and arguments.
    """

    app_name = "kit"

    @classmethod
    def from_job_definition(cls, job_definition: JobDefinition, args: List = None):
        """Create instance of KitJob with a job definition and args."""
        full_args = [
            # Set a default log level for outputs:
            "--/log/level=Info",
            "--/log/fileLogLevel=Info",
            "--/log/outputStreamLevel=Info",
            "--/log/flushStandardStreamOutput=true",

            # Ensure any Python scripting errors are printed to the output stream, and not intercepted (and silenced) by
            # other components:
            "--/app/python/logSysStdOutput=true",
            "--/app/python/interceptSysStdOutput=false",
            "--/plugins/carb.scripting-python.plugin/logScriptErrors=true",
            "--/app/fastShutdown=true"
        ]

        if job_definition.job_spec_path:
            full_args.append(f"--merge-config={job_definition.job_spec_path}")

        if args and (isinstance(args, tuple) or isinstance(args, list)):
            full_args.extend(args)

        config = FarmJobsConfig(auto_configure_logging=False)
        gpu_id = config.jobs.get("agent_assigned_gpu")
        if gpu_id is not None and gpu_id >= 0:
            full_args.extend([
                "--/renderer/multiGpu/enabled=false",
                f"--/renderer/activeGpu={gpu_id}"
            ])

        if job_definition.headless:
            full_args.append("--no-window")

        remote_agent_protocol = config.jobs.agent_controller_protocol
        remote_agent_host = config.jobs.agent_controller_host
        remote_agent_port = config.jobs.agent_controller_port
        remote_agent_path = config.jobs.agent_controller_path

        remote_agent_controller = f"{remote_agent_protocol}://{remote_agent_host}:{remote_agent_port}{remote_agent_path}"

        full_args.append(
            f"--/exts/omni.services.farm.agent.runner/controller={remote_agent_controller}"
        )

        farm_facility_extensions = config.jobs.farm_facilities_extensions
        if farm_facility_extensions:
            full_args.extend([
                "--ext-folder",
                f"{farm_facility_extensions}"
            ])

        return cls(
            command=job_definition.command,
            args=full_args,
            env=job_definition.env,
            log_to_stdout=job_definition.log_to_stdout,
            success_return_codes=job_definition.success_return_codes,
            container=job_definition.container
        )


class KitServiceJob(KitJob):
    """Kit service job."""

    allowed_args = {
        "task_id": {
            "arg": "--/exts/omni.services.farm.agent.runner/assigned_task",
            "default": ""
        },
        "task_log_file": {
            "arg": "--/log/file",
            "default": "${logs}/mytaskoutput_${start_timestamp}.log"
        },
    }

    @classmethod
    def from_job_definition(cls, job_definition: JobDefinition, args: List = None):
        """Create instance of KitJob with a job definition and args."""
        if job_definition.task_function is None:
            raise Exception(
                "No `task_function` was given, this is required for service jobs. "
                "To just run a specific Kit experience try using `kit` as process type in the toml file."
            )

        args = args or []
        args.extend([
            "--enable",
            "omni.services.farm.agent.runner",
        ])

        return super().from_job_definition(job_definition, args)
