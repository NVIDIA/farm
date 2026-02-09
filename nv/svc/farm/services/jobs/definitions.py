# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Definitions."""

import logging

import pydantic
from pydantic.dataclasses import dataclass

from typing import Dict, List, Optional


@dataclass
class InstancePayload:
    """Data required to create an instance of a process."""

    metadata: Dict
    args: Dict
    task_requirements: Dict


@dataclass
class ProcessCreationPayload:
    """When a process gets created we get its id and the status.

    The status is particularly relevant for integrations with other job systems, for example
        starting a job in Kubernetes doesn't mean that it's running.
    """

    process_id: str
    process_status: str  # TODO: Validate the status, or make an enum.


class SpawnResponseModel(pydantic.BaseModel):
    """Response model for task submission."""

    jsonapi: dict = pydantic.Field(..., title="JSON API", description="Metadata related to the JSONAPI itself")
    data: ProcessCreationPayload = pydantic.Field(..., title="Data", description="The response from a call to spawning a process")


class JobDefinition:
    """Settings that define a Job."""

    __slots__ = (
        "name",
        "job_type",
        "command",
        "args",
        "task_function",
        "env",
        "log_to_stdout",
        "extension_paths",
        "allowed_args",
        "job_spec_path",
        "headless",
        "active",
        "unresolved_command_path",
        "success_return_codes",
        "capacity_requirements",
        "working_directory",
        "container",
    )

    def __init__(
        self,
        name: str,
        job_type: str,
        command: str,
        job_spec_path: Optional[str] = None,
        args: Optional[list] = None,
        task_function: Optional[str] = None,
        env: Optional[Dict] = None,
        log_to_stdout: Optional[bool] = True,
        extension_paths: Optional[List] = None,
        allowed_args: Optional[Dict] = None,
        headless: Optional[bool] = True,
        active: Optional[bool] = True,
        unresolved_command_path: Optional[str] = None,
        success_return_codes: Optional[List[int]] = None,
        capacity_requirements: Optional[Dict[str, int]] = None,
        working_directory: Optional[str] = None,
        container: Optional[str] = None
    ) -> None:
        """Job definition constructor."""
        # Warn Users about Job Definition potentially having `job_spec_path`
        # set to an empty string prior to changing the validity of the property
        # in version 2.4.0 of the extension:
        if job_spec_path == "":
            logging.warning(f"The 'job_spec_path' parameter for Job Definition '{name}' is empty. Consider using 'None' for clarity.")

        self.name = name
        self.job_type = job_type
        self.command = command
        self.job_spec_path = job_spec_path
        self.args = args or []
        self.task_function = task_function or ''
        self.env = env or {}
        self.log_to_stdout = log_to_stdout
        self.extension_paths = extension_paths or []
        self.allowed_args = allowed_args or {}
        self.headless = headless
        self.active = active
        self.unresolved_command_path = unresolved_command_path
        self.success_return_codes = success_return_codes or [0]
        self.capacity_requirements = capacity_requirements or {}
        # TODO: This needs to be refactored with new job definitions.
        self.container = container or ""
        self.working_directory = working_directory

    def to_dict(self):
        """Convert job definition to dict."""
        return {
            "name": self.name,
            "job_type": self.job_type,
            "command": self.command,
            "args": self.args,
            "task_function": self.task_function,
            "env": self.env,
            "log_to_stdout": self.log_to_stdout,
            "extension_paths": self.extension_paths,
            "allowed_args": self.allowed_args,
            "job_spec_path": self.job_spec_path,
            "headless": self.headless,
            "active": self.active,
            "unresolved_command_path": self.unresolved_command_path,
            "success_return_codes": self.success_return_codes,
            "capacity_requirements": self.capacity_requirements,
            "working_directory": self.working_directory,
            "container": self.container,
        }
