# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for NVCF Process Manager."""

import unittest
from unittest import mock

from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.facilities.manager.nvcf import NVCFProcessManager


class TestNVCFProcessManager(unittest.IsolatedAsyncioTestCase):
    """
    Test NVCF Process Manager.

    This test suite is designed to test the NVCFProcessManager class.
    It includes tests for both spawning and monitoring processes.
    """

    async def asyncSetUp(self) -> None:
        # Mock post_data to return a task ID
        self.post_data_patcher = mock.patch("nv.svc.farm.services.jobs.facilities.manager.nvcf.utils.post_data")
        self.mock_post_data = self.post_data_patcher.start()
        self.mock_post_data.return_value = {}
        self.fetch_data_patcher = mock.patch("nv.svc.farm.services.jobs.facilities.manager.nvcf.utils.fetch_data")
        self.mock_fetch_data = self.fetch_data_patcher.start()
        self.mock_fetch_data.return_value = {}
        self._setup_manager()

    def tearDown(self) -> None:
        self._manager.stop()
        self._manager = None
        self.post_data_patcher.stop()
        self.fetch_data_patcher.stop()

    def _create_mock_job_store(self):
        job_store = mock.Mock()
        job_store.job_specs = {
            "test-job-1": JobDefinition(
                name="test-job-1",
                job_type="base",
                command="deploy",
                job_spec_path="foo",
                args=[],
                active=True,
                success_return_codes=[0]
            ),
            "test-job-2": JobDefinition(
                name="test-job-2",
                job_type="base",
                command="deploy",
                job_spec_path="foo",
                args=[],
                active=True,
                success_return_codes=[0]
            ),
            "test-job-3": JobDefinition(
                name="test-job-3",
                job_type="base",
                command="deploy",
                job_spec_path="foo",
                args=[],
                active=True,
                success_return_codes=[0]
            ),
        }
        return job_store

    def _setup_manager(self):
        job_store = self._create_mock_job_store()
        self._manager = NVCFProcessManager(
            job_store=job_store,
            username="test_user",
            password="test_password",
            api_key="junk"
        )

    async def test_spawn_simple_job(self):
        """Test that NVCFProcessManager can spawn a simple job."""
        # Create a simple payload for the spawn method
        metadata = {
            "functionId": "1",
            "versionId": "01",
            "deploymentSpecifications": []
        }
        payload = {"jsonapi": {"version": "1.0"}, "data": {"allowed_args": {}, "metadata": metadata}}

        self.mock_post_data.return_value = {
            "deployment": {
                "functionId": "1",
                "functionVersionId": "01"
            }
        }

        # Call spawn with minimal arguments
        result = await self._manager.spawn(
            job_name="test-job-1",
            payload=payload,
            monitor=True,
            task_id="123"
        )

        # Verify the result structure
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.data)
        self.assertIsNotNone(result.data.process_id)
        self.assertIsNotNone(result.data.process_status)
        active_processes = {
            process._process.pid for processes in self._manager._active_processes.values() for process in processes
        }
        self.assertTrue(len(active_processes) == 1)
        self.assertTrue("1:01:123" in active_processes)

    async def test_monitor_processes(self):
        """Test that NVCFProcessManager can monitor a simple job."""
        # Create a simple payload for the spawn method

        nvcf_functions = [
            # active tasks
            {"id": "1", "versionId": "01", "status": "DEPLOYING"},
            {"id": "2", "versionId": "02", "status": "INACTIVE"},
            # finished tasks
            {"id": "3", "versionId": "03", "status": "ACTIVE"},
            # errored tasks
            {"id": "4", "versionId": "04", "status": "ERRORED"},
        ]

        # spawn the tasks
        for function in nvcf_functions:
            self.mock_post_data.return_value = {"deployment": {"functionId": function["id"], "functionVersionId": function["versionId"]}}
            function_metadata = {"functionId": function["id"], "versionId": function["versionId"]}
            function_payload = {"jsonapi": {"version": "1.0"}, "data": {"allowed_args": {}, "metadata": function_metadata}}
            await self._manager.spawn(job_name="test-job-1", payload=function_payload, monitor=True, task_id=function["id"])

        # set the mock bulk tasks request for nvcf
        self.mock_fetch_data.return_value = {"functions": nvcf_functions}

        # monitor process method should sort all tasks into the correct buckets
        await self._manager.monitor_processes()
        self.assertEqual(len(self._manager.active_processes.get("test-job-1")), 2)
        self.assertEqual(len(self._manager.finished_processes.get("test-job-1")), 1)
        self.assertEqual(len(self._manager.errored_processes.get("test-job-1")), 1)

    async def test_monitor_processes_multiple_job_types(self):
        """Test that NVCFProcessManager can monitor multiple job types."""
        # Create a simple payload for the spawn method

        nvcf_functions = [
            # active tasks
            {"id": "1", "versionId": "01", "status": "DEPLOYING", "job_type": "test-job-1"},
            {"id": "3", "versionId": "03", "status": "INACTIVE", "job_type": "test-job-1"},
            {"id": "4", "versionId": "04", "status": "INACTIVE", "job_type": "test-job-2"},
            # finished tasks
            {"id": "2", "versionId": "02", "status": "ACTIVE", "job_type": "test-job-1"},
            # errored tasks
            {"id": "5", "versionId": "05", "status": "ERRORED", "job_type": "test-job-3"},
        ]

        # spawn the tasks
        for function in nvcf_functions:
            self.mock_post_data.return_value = {"deployment": {"functionId": function["id"], "functionVersionId": function["versionId"]}}
            function_metadata = {"functionId": function["id"], "versionId": function["versionId"]}
            function_payload = {"jsonapi": {"version": "1.0"}, "data": {"allowed_args": {}, "metadata": function_metadata}}
            await self._manager.spawn(job_name=function["job_type"], payload=function_payload, monitor=True, task_id=function["id"])

        # set the mock bulk tasks request for nvcf
        self.mock_fetch_data.return_value = {"functions": nvcf_functions}

        # monitor process method should sort all tasks into the correct buckets
        await self._manager.monitor_processes()
        self.assertEqual(len(self._manager.active_processes.get("test-job-1")), 2)
        self.assertEqual(len(self._manager.finished_processes.get("test-job-1")), 1)
        self.assertEqual(len(self._manager.active_processes.get("test-job-2")), 1)
        self.assertEqual(len(self._manager.errored_processes.get("test-job-3")), 1)
