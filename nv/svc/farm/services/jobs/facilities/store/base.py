# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Base Store Facility."""

from typing import Awaitable, Dict, Optional

from nv.svc.farm.services.jobs.config import FarmJobsConfig
from nv.svc.farm.services.jobs.definitions import JobDefinition


class BaseJobStore:
    """Job Store for managing job definitions."""

    def __init__(self, store_updated_callback: Optional[Awaitable] = None) -> None:
        """Job store constructor."""
        self._jobs: Dict[str, JobDefinition] = {}

        self._config = FarmJobsConfig(auto_configure_logging=False)
        self._store_updated_callback = store_updated_callback

    @property
    def job_specs(self):
        """Return all loaded jobs."""
        return self._jobs

    def update_settings(self, **kwargs):
        """Reconfigure the job store instance with new settings."""
        raise NotImplementedError

    def save_job(self, job_definition: JobDefinition) -> None:
        """Save the job for a given job definition."""
        raise NotImplementedError

    async def delete_job(self, job_definition_name: str) -> None:
        """Delete the job for a given job definition name."""
        raise NotImplementedError

    async def load_jobs(self) -> None:
        """Load a list of jobs and notify upon completion."""
        changed = await self._load_jobs()
        if changed and self._store_updated_callback is not None:
            await self._store_updated_callback(self)

    async def _load_jobs(self) -> bool:
        """
        Load a list of jobs.

        Implement this function for any subclasses to implement the specific way jobs should be loaded.
        """
        raise NotImplementedError

    async def start(self):
        """To start the job store."""
        pass

    async def stop(self):
        """To stop the store."""
        pass
