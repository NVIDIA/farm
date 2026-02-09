# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Remote Store Facility."""

import asyncio
import logging
from typing import Awaitable, Dict, List, Optional

from .base import BaseJobStore
from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.utils import fetch_data


class RemoteJobStore(BaseJobStore):
    """Remote job store."""

    def __init__(self, jobs_load_endpoint: str, fetch_interval: int = 30, store_updated_callback: Optional[Awaitable] = None) -> None:
        """Remote job store constructor."""

        super().__init__(store_updated_callback)

        self._jobs_load_endpoint = jobs_load_endpoint.rstrip("/")
        self._fetch_interval = fetch_interval
        self._current_job_specifications = {}

    def save_job(self, job_definition: JobDefinition) -> None:
        """Save job not supported for Remote store."""
        raise NotImplementedError("The remote job store cannot save jobs. Use the remote service API directly.")

    def update_settings(self, *args, **kwargs):
        """Update settings not supported for Remote store."""
        raise NotImplementedError("The remote job store settings cannot be changed during runtime.")

    async def _fetch_from_remote(self) -> None:
        await asyncio.sleep(self._fetch_interval)
        while True:
            try:
                await self.load_jobs()
            except Exception as exc:
                logging.error(f"Failed to load remote job definitions: {str(type(exc))}, {str(exc)}")

            await asyncio.sleep(self._fetch_interval)

    async def start(self) -> None:
        try:
            logging.debug("Starting fetch_from_remote coroutine.")
            await self._fetch_from_remote()
        except asyncio.CancelledError:
            return

    async def _load_jobs(self) -> bool:
        job_specifications = await fetch_data(self._jobs_load_endpoint)
        if job_specifications == self._current_job_specifications:
            return False

        self._current_job_specifications = dict(job_specifications)

        jobs = {}
        for job_name, job_spec in job_specifications.items():
            jobs[job_name] = JobDefinition(**job_spec)

        self._jobs = jobs
        return True

    async def _generate_job_definition(self, job_name: str, params: Dict, job_spec_path: str, extension_paths: List) -> JobDefinition:

        resolved_command = params["command"]
        args = params.get("args", [])
        env = params.get("env", {})

        return JobDefinition(
            job_name,
            params["job_type"],
            resolved_command,
            job_spec_path,
            args=args,
            task_function=params.get("task_function", None),
            headless=params.get("headless", True),
            env=env,
            log_to_stdout=params.get("log_to_stdout", True),
            allowed_args=params.get("allowed_args", {}),
            unresolved_command_path=resolved_command,
            extension_paths=extension_paths,
            success_return_codes=params.get("success_return_codes", [0]),
            capacity_requirements=params.get("capacity_requirements", {}),
            working_directory=params.get("working_directory"),
            container=params.get("container")
        )
