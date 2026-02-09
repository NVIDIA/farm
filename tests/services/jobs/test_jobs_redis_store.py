# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import AsyncIterator, List
import unittest
from unittest.mock import patch

from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.facilities.store.redis import RedisJobStore


class TestRedisJobStore(unittest.IsolatedAsyncioTestCase):
    fail_on_log_error = True

    def setUp(self) -> None:
        # we're not going to actually connect since we're patching execute_command ahead,
        # though we'll use a redis:// so this will not get angry on Windows which is lacking unix://.
        self._bind_address = "redis://localhost:6379/"

    def _get_job_store(self) -> RedisJobStore:
        return RedisJobStore(connection_string=self._bind_address)

    async def test_job_lifecycle(self):
        job_store = self._get_job_store()

        async def mock_execute_command(*args, **kwargs) -> List[str]:
            """our return type will depend on the caller, but for scan_iter we just need an iterable"""
            return []

        async def mock_set(*args, **kwargs) -> bool:
            return True

        async def mock_scan_iter(*args, **kwargs) -> AsyncIterator[str]:
            yield ""

        async def mock_delete(*args, **kwargs) -> int:
            return 1

        with patch("redis.asyncio.Redis.execute_command", wraps=mock_execute_command), \
             patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set, \
             patch("redis.asyncio.Redis.scan_iter", wraps=mock_scan_iter) as mock_scan_iter, \
             patch("redis.asyncio.Redis.delete", wraps=mock_delete) as mock_delete:

            job_def = JobDefinition(name="test-job", job_type="kit-service", command="foo", job_spec_path=None)
            await job_store._store_job_definition(job_def)

            mock_set.assert_called_once_with(
                "job_spec_test-job",
                json.dumps(job_def.to_dict()),
            )
            mock_scan_iter.assert_called_once_with(match="job_spec_*", _type="STRING")

            await job_store.delete_job(job_def.name)
            mock_delete.assert_called_once_with(f"job_spec_{job_def.name}")
