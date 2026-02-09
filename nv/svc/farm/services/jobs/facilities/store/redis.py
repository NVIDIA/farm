# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Redis Store Facility."""

import asyncio
import json
import logging
from typing import Awaitable, List, Optional, Set

import redis.asyncio as redis

from nv.svc.core.exceptions import ServicesBaseException

from .base import BaseJobStore
from nv.svc.farm.services.jobs.definitions import JobDefinition


class RedisJobStore(BaseJobStore):
    """Redis Job store configuration."""

    def __init__(self, connection_string: str, store_updated_callback: Optional[Awaitable] = None) -> None:
        """Redis store constructor."""
        super().__init__(store_updated_callback)

        self._job_prefix = "job_spec_"
        self._redis = redis.from_url(connection_string)

    def save_job(self, job_definition: JobDefinition) -> None:
        """Save the job definition to redis."""
        asyncio.ensure_future(self._store_job_definition(job_definition))

    async def delete_job(self, job_definition_name: str) -> None:
        """Delete the job definition from the backend redis store, but leave the in-memory cleanup to load_jobs()."""

        job_spec_key = f"{self._job_prefix}{job_definition_name}"
        deleted_jobs_count: int = await self._redis.delete(job_spec_key)

        if deleted_jobs_count == 0:
            raise ServicesBaseException(status_code=404, detail="Job does not exist.")

        # reload the jobs so we refresh our in-memory store
        await self.load_jobs()

    async def _store_job_definition(self, job_definition: JobDefinition) -> None:
        job_spec_key = f"{self._job_prefix}{job_definition.name}"

        job_stored: bool = await self._redis.set(
            job_spec_key,
            json.dumps(job_definition.to_dict()),
        )
        if not job_stored:
            raise ServicesBaseException(status_code=500, detail="Job could not be stored.")

        await self.load_jobs()

    def update_settings(self, *args, **kwargs):
        """Skip updating settings, not supported."""
        raise NotImplementedError("The redis job store settings cannot be changed during runtime.")

    async def _load_jobs(self) -> bool:
        job_list_current: Set[str] = set(self._jobs.keys())

        # use a non-blocking scan to retrieve all the job keys
        job_keys: List[str] = []
        async for job_name in self._redis.scan_iter(match=f"{self._job_prefix}*", _type="STRING"):
            job_keys.append(job_name)

        logging.debug(f"Loading {len(job_keys)} job definitions from redis")

        job_specifications: List[Optional[str]] = []
        for job_key in job_keys:
            data = await self._redis.get(job_key)
            job_specifications.append(data)

        job_list_new: Set[str] = set()

        for job_key, job_spec in zip(job_keys, job_specifications):
            try:
                data = json.loads(job_spec)
            except (TypeError, json.decoder.JSONDecodeError):
                logging.warning(f"skipped loading damaged job definition from redis: {job_key}")
                continue
            job_definition = JobDefinition(**data)
            job_list_new.add(job_definition.name)
            self._jobs[job_definition.name] = job_definition

        # remove old jobs that didn't get loaded from redis
        for job_definition_to_delete in job_list_current - job_list_new:
            logging.info(f"Removing job definition from memory that no longer exists in redis: {job_definition_to_delete}")
            del self._jobs[job_definition_to_delete]

        return True
