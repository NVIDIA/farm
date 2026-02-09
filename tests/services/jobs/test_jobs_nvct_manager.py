# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for NVCT Process Manager."""

import unittest
from unittest import mock

from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.facilities.manager.nvct import NVCTProcessManager


class TestNVCTProcessManager(unittest.IsolatedAsyncioTestCase):
    """
    Test NVCT Process Manager.

    This test suite is designed to test the NVCTProcessManager class.
    It includes tests for both spawning and monitoring processes.
    """

    async def asyncSetUp(self) -> None:
        # Mock post_data to return a task ID
        self.post_data_patcher = mock.patch("nv.svc.farm.services.jobs.facilities.manager.nvct.utils.post_data")
        self.mock_post_data = self.post_data_patcher.start()
        self.mock_post_data.return_value = {}
        self._setup_manager()

    def tearDown(self) -> None:
        self._manager.stop()
        self._manager = None

    def _create_mock_job_store(self):
        job_store = mock.Mock()
        job_store.job_specs = {
            "test-job-1": JobDefinition(
                name="test-job-1",
                job_type="base",
                command="echo",
                job_spec_path="foo",
                args=[],
                active=True,
                success_return_codes=[0],
            ),
            "test-job-2": JobDefinition(
                name="test-job-2",
                job_type="base",
                command="echo",
                job_spec_path="foo",
                args=[],
                active=True,
                success_return_codes=[0],
            ),
            "test-job-3": JobDefinition(
                name="test-job-3",
                job_type="base",
                command="echo",
                job_spec_path="foo",
                args=[],
                active=True,
                success_return_codes=[0],
            ),
        }
        return job_store

    def _setup_manager(self):
        job_store = self._create_mock_job_store()
        self._manager = NVCTProcessManager(
            job_store=job_store,
            username="test_user",
            password="test_password",
            disable_authn=True  # Disable auth for testing
        )

    async def test_spawn_simple_job(self):
        """Test that NVCTProcessManager can spawn a simple job."""
        # Create a simple payload for the spawn method
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "allowed_args": {},
                "metadata": {}
            }
        }

        self.mock_post_data.return_value = {"task": {"id": "1"}}

        # Call spawn with minimal arguments
        result = await self._manager.spawn(
            job_name="test-job-1",
            payload=payload,
            monitor=True,
            task_id="test-task-123"
        )

        # Verify the result structure
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.data.process_id)
        self.assertIsNotNone(result.data.process_status)
        active_processes = {process._process.pid for processes in self._manager._active_processes.values() for process in processes}
        self.assertTrue(len(active_processes) == 1)
        self.assertTrue("1" in active_processes)

    async def test_monitor_processes(self):
        """Test that NVCTProcessManager can monitor a simple job."""
        # Create a simple payload for the spawn method
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "allowed_args": {},
                "metadata": {}
            }
        }

        nvct_tasks = [
            # active tasks
            {
                "id": "1",
                "status": "QUEUED"
            },
            {
                "id": "2",
                "status": "RUNNING"
            },
            {
                "id": "3",
                "status": "LAUNCHED"
            },
            # finished tasks
            {
                "id": "4",
                "status": "COMPLETED"
            },
            # errored tasks
            {
                "id": "5",
                "status": "ERRORED"
            },
            {
                "id": "6",
                "status": "EXCEEDED_MAX_RUNTIME_DURATION"
            },
            {
                "id": "7",
                "status": "EXCEEDED_MAX_QUEUED_DURATION"
            },
            {
                "id": "8",
                "status": "UNKNOWN"
            },
            {
                "id": "9",
                "status": "CANCELED"
            },
        ]

        # spawn the tasks
        for task in nvct_tasks:
            self.mock_post_data.return_value = {"task": task}

            await self._manager.spawn(
                job_name="test-job-1",
                payload=payload,
                monitor=True,
                task_id="test-task-123"
            )

        # set the mock bulk tasks request for nvct
        self.mock_post_data.return_value = {"tasks": nvct_tasks}

        # monitor process method should sort all tasks into the correct buckets
        await self._manager.monitor_processes()
        self.assertEqual(len(self._manager.active_processes.get("test-job-1")), 3)
        self.assertEqual(len(self._manager.finished_processes.get("test-job-1")), 1)
        self.assertEqual(len(self._manager.errored_processes.get("test-job-1")), 5)

    async def test_monitor_processes_multiple_job_types(self):
        """Test that NVCTProcessManager can monitor multiple job types."""
        # Create a simple payload for the spawn method
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "allowed_args": {},
                "metadata": {}
            }
        }

        nvct_tasks = [
            # active tasks
            {
                "id": "1",
                "status": "QUEUED",
                "job_type": "test-job-1"
            },
            {
                "id": "2",
                "status": "RUNNING",
                "job_type": "test-job-1"
            },
            {
                "id": "3",
                "status": "LAUNCHED",
                "job_type": "test-job-1"
            },
            # finished tasks
            {
                "id": "4",
                "status": "COMPLETED",
                "job_type": "test-job-2"
            },
            # errored tasks
            {
                "id": "5",
                "status": "ERRORED",
                "job_type": "test-job-3"
            },
            {
                "id": "6",
                "status": "EXCEEDED_MAX_RUNTIME_DURATION",
                "job_type": "test-job-3"
            },
            {
                "id": "7",
                "status": "EXCEEDED_MAX_QUEUED_DURATION",
                "job_type": "test-job-3"
            },
            {
                "id": "8",
                "status": "UNKNOWN",
                "job_type": "test-job-3"
            },
            {
                "id": "9",
                "status": "CANCELED",
                "job_type": "test-job-3"
            },
        ]

        # spawn the tasks
        for task in nvct_tasks:
            self.mock_post_data.return_value = {"task": task}

            await self._manager.spawn(
                job_name=task["job_type"],
                payload=payload,
                monitor=True,
                task_id="test-task-123"
            )

        # set the mock bulk tasks request for nvct
        tasks = [{"id": task["id"], "status": task["status"]} for task in nvct_tasks]
        self.mock_post_data.return_value = {"tasks": tasks}

        # monitor process method should sort all tasks into the correct buckets
        await self._manager.monitor_processes()
        self.assertEqual(len(self._manager.active_processes.get("test-job-1")), 3)
        self.assertEqual(len(self._manager.finished_processes.get("test-job-2")), 1)
        self.assertEqual(len(self._manager.errored_processes.get("test-job-3")), 5)
