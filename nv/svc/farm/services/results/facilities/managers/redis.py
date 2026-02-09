# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results Service Redis Manager Facility."""

from typing import List

import redis.asyncio as redis
from .base import BaseResultManager, ResultNotFound


class RedisResultManager(BaseResultManager):
    """Redis result manager with DAG indexing capabilities."""

    def __init__(self, connection_string: str = None, result_ttl: int = 432000, **kwargs) -> None:
        """Initialize the Redis result manager.

        Args:
            connection_string (str): Redis connection string (e.g., "redis://host:port")
            result_ttl (int): TTL for result keys in seconds. Default: 5 days (432000)
            **kwargs: Additional arguments (ignored for compatibility)
        """
        super().__init__()
        self._result_ttl = result_ttl  # TTL in seconds, default 5 days
        self._redis = redis.from_url(connection_string)

    def _get_result_key(self, task_id: str) -> str:
        """Get Redis key for a task result."""
        return f"result_task_{task_id}"

    def _get_dag_index_key(self, dag_id: str) -> str:
        """Get Redis key for a DAG index."""
        return f"result_dag_{dag_id}"

    async def store_result(self, task_id: str, data: str, dag_id: str = "") -> None:
        """Store result with DAG indexing using simple Redis SET.

        Args:
            task_id: The task ID to store result for
            data: The result data to store
            dag_id: DAG ID for indexing (empty string if not part of a DAG)

        Returns:
            None: No return value.
        """
        result_key = self._get_result_key(task_id)

        # Store the raw data directly at the key
        await self._redis.set(result_key, data, ex=self._result_ttl)

        # Add to DAG index if DAG ID present (idempotent operation)
        # Note: Sequential calls required for Redis HA compatibility (cross-slot keys)
        if dag_id:
            dag_index_key = self._get_dag_index_key(dag_id)
            await self._redis.sadd(dag_index_key, task_id)
            await self._redis.expire(dag_index_key, self._result_ttl)

    async def get_result(self, task_id: str) -> str:
        """Get single result by task ID."""
        key = self._get_result_key(task_id)
        data = await self._redis.get(key)

        if data is None:
            raise ResultNotFound(task_id)

        return data.decode()

    async def get_results_by_dag(self, dag_id: str) -> List[str]:
        """Get all results for tasks in a DAG."""
        # Get all task IDs for this DAG
        task_ids = await self._redis.smembers(self._get_dag_index_key(dag_id))

        if not task_ids:
            return []

        # Build result keys
        result_keys = [self._get_result_key(task_id.decode()) for task_id in task_ids]

        # Fetch results individually (required for Redis HA compatibility)
        results = []
        for key in result_keys:
            data = await self._redis.get(key)
            if data is not None:
                results.append(data.decode())

        return results
