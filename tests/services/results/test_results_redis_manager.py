# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the RedisResultManager using real Redis containers."""

import pytest
import sys
from unittest import IsolatedAsyncioTestCase
from testcontainers.redis import RedisContainer
import docker

from nv.svc.farm.services.results.facilities.managers.redis import RedisResultManager
from nv.svc.farm.services.results.facilities.managers.base import ResultNotFound

LINUX_DOCKER_ONLY = "this test is for linux+docker only"


def _docker_available():
    """Check if Docker is available and accessible."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


@pytest.mark.skipif(
    not hasattr(docker, 'from_env') or not _docker_available(),
    reason="Docker not available - skipping integration tests"
)
class TestRedisResultManager(IsolatedAsyncioTestCase):
    """Test cases for the RedisResultManager class using real Redis."""

    @classmethod
    def setUpClass(cls):
        """Start Redis container for all tests in this class."""
        cls.redis_container = RedisContainer("redis:7-alpine")
        cls.redis_container.start()

        # Get connection details
        cls.redis_host = cls.redis_container.get_container_host_ip()
        cls.redis_port = cls.redis_container.get_exposed_port(6379)
        cls.connection_string = f"redis://{cls.redis_host}:{cls.redis_port}"

    @classmethod
    def tearDownClass(cls):
        """Stop Redis container after all tests."""
        cls.redis_container.stop()

    def setUp(self):
        """Set up test fixtures."""
        # Create manager with real Redis connection
        self.ttl = 3600
        self.manager = RedisResultManager(connection_string=self.connection_string, result_ttl=self.ttl)

    def _assert_ttl(self, ttl: int):
        """Assert TTL is set within expected range."""
        assert self.ttl - 10 <= ttl <= self.ttl

    async def asyncTearDown(self):
        """Clean up after each test."""
        # Clean up all test data from Redis
        await self._cleanup_redis()
        await self.manager._redis.aclose()

    async def _cleanup_redis(self):
        """Remove all test keys from Redis."""
        try:
            # Get all result-related keys
            keys = await self.manager._redis.keys("result_*")
            if keys:
                await self.manager._redis.delete(*keys)
        except Exception as e:
            print(f"Warning: Failed to cleanup Redis keys: {e}")

    def _get_manager(self, connection_string: str = None, result_ttl: int = 3600) -> RedisResultManager:
        """Get a manager instance (for tests that need different configurations)."""
        if connection_string is None:
            connection_string = self.connection_string
        return RedisResultManager(connection_string=connection_string, result_ttl=result_ttl)

    @pytest.mark.skipif(sys.platform != "linux", reason=LINUX_DOCKER_ONLY)
    async def test_store_new_result(self):
        """Test storing a new result without DAG indexing."""
        task_id = "test-task-1"
        data = "Test result data"

        # Store result
        await self.manager.store_result(task_id, data)

        stored_data = await self.manager.get_result(task_id)
        assert stored_data == data

        # Verify TTL is set (should be close to 3600, allowing for small delay)
        ttl = await self.manager._redis.ttl(self.manager._get_result_key(task_id))
        self._assert_ttl(ttl)

    @pytest.mark.skipif(sys.platform != "linux", reason=LINUX_DOCKER_ONLY)
    async def test_store_result_with_dag_indexing(self):
        """Test storing a result with DAG indexing."""
        task_id = "dag-task-1"
        data = "DAG task result"
        dag_id = "taskflow-123"
        dag_key = self.manager._get_dag_index_key(dag_id)
        result_key = self.manager._get_result_key(task_id)

        # Store result with DAG indexing
        await self.manager.store_result(task_id, data, dag_id)

        # Verify result is the data itself
        stored_data = await self.manager.get_result(task_id)
        assert stored_data == data

        # Verify task result is stored
        dag_results = await self.manager.get_results_by_dag(dag_id)
        assert stored_data in dag_results

        # Verify TTL is set on both keys (should be close to 3600, allowing for small delay)
        result_ttl = await self.manager._redis.ttl(result_key)
        self._assert_ttl(result_ttl)

        dag_ttl = await self.manager._redis.ttl(dag_key)
        self._assert_ttl(dag_ttl)

    @pytest.mark.skipif(sys.platform != "linux", reason=LINUX_DOCKER_ONLY)
    async def test_get_nonexistent_result(self):
        """Test retrieving a result that doesn't exist."""
        with self.assertRaises(ResultNotFound) as context:
            await self.manager.get_result("nonexistent-task")

        assert context.exception.task_id == "nonexistent-task"

    @pytest.mark.skipif(sys.platform != "linux", reason=LINUX_DOCKER_ONLY)
    async def test_get_results_by_dag_with_results(self):
        """Test retrieving all results for a DAG that has results."""
        dag_id = "test-dag"
        tasks = [
            ("task1", "result1"),
            ("task2", "result2"),
            ("task3", "result3"),
        ]

        # Store multiple tasks for the same DAG
        for task_id, data in tasks:
            await self.manager.store_result(task_id, data, dag_id)

        # Retrieve all results by DAG
        dag_results = await self.manager.get_results_by_dag(dag_id)

        # Verify we got all results (order might vary)
        assert len(dag_results) == 3
        for _, expected_data in tasks:
            assert expected_data in dag_results

    @pytest.mark.skipif(sys.platform != "linux", reason=LINUX_DOCKER_ONLY)
    async def test_get_results_by_dag_no_tasks(self):
        """Test retrieving results for a DAG with no tasks."""
        dag_results = await self.manager.get_results_by_dag("empty-dag")
        assert dag_results == []

    @pytest.mark.skipif(sys.platform != "linux", reason=LINUX_DOCKER_ONLY)
    async def test_get_results_by_dag_with_missing_results(self):
        """Test retrieving DAG results when some tasks have missing results."""
        dag_id = "partial-dag"

        # Store tasks for the DAG
        await self.manager.store_result("task1", "result1", dag_id)
        await self.manager.store_result("task2", "result2", dag_id)
        await self.manager.store_result("task3", "result3", dag_id)

        # Manually delete one task result (simulating expiry)
        await self.manager._redis.delete(self.manager._get_result_key("task2"))

        # Get DAG results - should only return existing ones
        dag_results = await self.manager.get_results_by_dag(dag_id)

        # Should get 2 results (missing task2)
        assert len(dag_results) == 2
        assert "result1" in dag_results
        assert "result3" in dag_results
        assert "result2" not in dag_results
