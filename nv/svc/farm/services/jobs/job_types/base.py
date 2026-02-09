# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Job Types Base."""

import asyncio
import importlib
import logging
import os
import platform
import subprocess
from typing import Any, Callable, Dict, List, Optional

from nv.svc.farm.services.jobs.definitions import JobDefinition


class BaseJob:
    """The BaseJob sits at the base of all jobs.

    It defines the mimimum requirements for a job to be executed on Agents.
    """

    app_name = "base"

    allowed_args = {}

    def __init__(
        self,
        command: str,
        args: List[str],
        env: Dict[str, Any] = None,
        subprocess_kwargs: Dict[str, Any] = None,
        log_to_stdout: bool = True,
        on_stdout_message: Callable[[str], None] = None,
        on_stderr_message: Callable[[str], None] = None,
        success_return_codes: List[int] = None,
        working_directory: Optional[str] = None,
        container: Optional[str] = None
    ) -> None:
        """Job constructor."""

        if not env:
            env = {}
        if not subprocess_kwargs:
            subprocess_kwargs = {}

        self._farm_version = importlib.metadata.distribution("nv.svc.farm").version
        self._command = command
        self._args = args
        self._working_directory = working_directory if working_directory else None
        self._env = self._resolve_environment_variables(env)
        self._subprocess_kwargs = self._resolve_subprocess_kwargs(subprocess_kwargs)
        self._success_return_codes = success_return_codes or [0]
        self._container = container

        self._stdin = subprocess.DEVNULL
        self._stdout = subprocess.DEVNULL
        self._stderr = subprocess.DEVNULL
        if log_to_stdout:
            # TODO, allow this to be configurable to a file path
            self._stdin = asyncio.subprocess.PIPE
            self._stdout = asyncio.subprocess.PIPE
            self._stderr = asyncio.subprocess.STDOUT

        self._stdout_output: List[str] = []
        self._stderr_output: List[str] = []
        self._stdall_output: List[str] = []
        self._on_stdout_message = self._handle_stdout_buffer
        self._on_stderr_message = self._handle_stderr_buffer

    @property
    def command(self):
        """Command property."""
        return self._command

    @property
    def container(self):
        """Container property."""
        return self._container

    @property
    def args(self):
        """Args property."""
        return self._args

    @property
    def working_directory(self):
        """Working directory property."""
        return self._working_directory

    @property
    def env(self):
        """Env property."""
        return self._env

    @property
    def success_return_codes(self):
        """Success return codes property."""
        return self._success_return_codes

    @property
    def subprocess_kwargs(self):
        """Subprocess kwargs property."""
        return self._subprocess_kwargs

    @property
    def stdin(self):
        """Stdin property."""
        return self._stdin

    @property
    def stdout(self):
        """Stdout property."""
        return self._stdout

    @property
    def stderr(self):
        """Stderr property."""
        return self._stderr

    @property
    def on_stdout_message(self) -> Callable[[str], None]:
        """On stdout message property."""
        return self._on_stdout_message

    @property
    def on_stderr_message(self) -> Callable[[str], None]:
        """On stderr message property."""
        return self._on_stderr_message

    def _resolve_subprocess_kwargs(self, subprocess_kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve and marge the User-supplied and host kwargs variables so they can be supplied to the job instance.

        Args:
            subprocess_kwargs (Dict[str, Any]): Key-value pair of User-supplied kwargs variables to supply to the job
                instance.

        Returns:
            Dict[str, Any]: The key-value pair of kwargs variables to supply to the job instance.

        """
        if not subprocess_kwargs:
            subprocess_kwargs = {}
        if self._is_windows() and "creationflags" not in subprocess_kwargs:
            # Detach process from parent process in Windows (without this flag, CTRL+C will be sent to the subprocess):
            subprocess_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        return subprocess_kwargs

    def _resolve_environment_variables(self, job_definition_env: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Resolve and merge the User-supplied and host environment variables so they can be supplied to the job instance.

        Args:
            job_definition_env (Dict[str, Any]): Key-value pair of User-supplied environment variables to supply to the
             job instance.

        Returns:
            Dict[str, Any]: The key-value pair of environment variables to supply to the job instance.

        """
        if not job_definition_env:
            job_definition_env = {}
        os_environment_variables = ["HOME"]
        if self._is_windows():
            # TODO: Tidy this up.
            #
            # Adding all environment variables from parent process can lead to issues when different versions of Python
            # are used.
            # variables.extend(["SYSTEMROOT", "TEMP", "TMP", "APPDATA", "USERNAME", "LOCALAPPDATA", "USERPROFILE"])
            os_environment_variables.extend(dict(os.environ).keys())

        for variable in os_environment_variables:
            if variable in job_definition_env:
                continue
            value = os.environ.get(variable, None)
            if value is not None:
                job_definition_env[variable] = value
            else:
                logging.warning(
                    f"\"{variable}\" environment variable not set. Kit applications might not work as expected."
                )

        if "OV_FARM_VERSION" not in job_definition_env:
            job_definition_env["OV_FARM_VERSION"] = self._farm_version

        return job_definition_env

    def _handle_stdout_buffer(self, line) -> None:
        """Handle an incoming message buffer from ``stdout``."""
        self._stdout_output.append(str(line))
        self._stdall_output.append(str(line))

    def _handle_stderr_buffer(self, line) -> None:
        """Handle an incoming message buffer from ``stderr``."""
        self._stderr_output.append(str(line))
        self._stdall_output.append(str(line))

    def _is_windows(self) -> bool:
        """
        Check if the current platform is Windows.

        Args:
            None

        Returns:
            bool: A flag indicating if the current platform is Windows.

        """
        return platform.system().lower() == "windows"

    def get_logs(self) -> List[str]:
        """
        Return the list of log entries appended to both the ``stdout`` and ``stderr`` streams.

        Note that the rationale for maintaining a list of messages is that capturing the output from ``stdout`` and
        ``stderr` of the process can later be reassembled in a chronological fashion using an incrementing index. While
        this is currently not implemented, this can be implemented in the future to allow better reconstruction of the
        timeline of events which happened during the execution of a task.

        Args:
            None

        Returns:
            The list of log entries appended to the ``stdout`` stream.

        """
        return self._stdall_output

    def get_out_logs(self) -> List[str]:
        """
        Return the list of log entries appended to the ``stdout` stream.

        Note that the rationale for maintaining a list of messages is that capturing the output from ``stdout`` and
        ``stderr` of the process can later be reassembled in a chronological fashion using an incrementing index. While
        this is currently not implemented, this can be implemented in the future to allow better reconstruction of the
        timeline of events which happened during the execution of a task.

        Args:
            None

        Returns:
            The list of log entries appended to the ``stdout`` stream.

        """
        return self._stdout_output

    def get_error_logs(self) -> List[str]:
        """
        Return the list of log entries appended to the ``stderr`` stream.

        Args:
            None

        Returns:
            The list of log entries appended to the ``stderr`` stream.

        """
        return self._stderr_output

    @classmethod
    def from_job_definition(cls, job_definition: JobDefinition, args: List = None):
        """
        Create a Job from the given definition.

        Args:
            job_definition (JobDefinition): Job definition from which to create a job model for the environment where it
                will be executed.
            args (List): List of arguments to supply to the job.

        Returns:
            BaseJob: An instance of a job built from the given definition.

        """

        return cls(
            command=job_definition.command,
            args=args or [],
            env=job_definition.env,
            log_to_stdout=job_definition.log_to_stdout,
            success_return_codes=job_definition.success_return_codes,
            working_directory=job_definition.working_directory,
            container=job_definition.container,
        )
