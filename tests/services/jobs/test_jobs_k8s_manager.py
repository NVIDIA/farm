# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List
from unittest import mock
from unittest.mock import Mock, patch, call, AsyncMock, PropertyMock
import unittest
import asyncio
from datetime import datetime, timezone

from nv.svc.farm.services.jobs.facilities.manager.base import (
    BaseInstance,
    BaseRemoteProcess
)
from nv.svc.farm.services.jobs.facilities.manager.k8s import (
    KubernetesProcessManager,
    K8sInstance
)


LOGS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Integer tincidunt lacus nec arcu malesuada, sed congue diam dignissim.",
    "In ac est at risus consectetur commodo et sit amet mauris.",
    "In eget erat a ante rutrum viverra vel quis turpis.",
]


class _FakeInstance(BaseInstance):

    @property
    def is_active(self):
        return True

    @property
    def returncode(self):
        return 0

    @property
    def process_id(self):
        return 1234

    def stop(self):
        pass

    def kill(self):
        pass


class TestK8sInstance(unittest.IsolatedAsyncioTestCase):

    def _create_mock_k8s_instance(self, command="echo hello", container="my-docker:1.0.0", args=["echo", "hello"]):
        return K8sInstance(
            k8s_manager=mock.Mock(),
            command=command,
            container=container,
            args=args
        )

    def setUp(self):
        super().setUp()
        self.loop = asyncio.get_event_loop()
        self.k8s_manager_mock = AsyncMock()
        self.instance = K8sInstance(
            k8s_manager=self.k8s_manager_mock,
            command="echo hello",
            container="my-docker:1.0.0",
            args=["echo", "hello"]
        )
        self.instance._process = BaseRemoteProcess("some_pid", {"job": {"id": 1}})
        self.instance._active_check_delay = 0.1  # Speed up the test
        self.instance._log_check_delay = 0.1  # Speed up the test
        self.instance._latest_log_time = '2023-08-25T02:55:22.210915+00:00'

    async def test_process_return(self):
        test_instance = self._create_mock_k8s_instance()

        # Here we mock a Process being created instead of mocking too many things.
        test_instance._process = BaseRemoteProcess("1", {"job": {"id": 1}})
        self.assertTrue(test_instance.is_active)

        # Finished the process.
        test_instance._process.set_returncode(0)
        self.assertFalse(test_instance.is_active)

    @patch("datetime.datetime")
    async def test_get_latest_logs(self, mock_datetime):
        # Create a mock datetime object
        mock_now = Mock()
        mock_now.isoformat.return_value = '2023-08-25T02:55:22.210915+00:00'

        # Set the mock datetime object to be the return value of datetime.datetime.now()
        mock_datetime.now.return_value = mock_now

        self.k8s_manager_mock.get_job_logs.return_value = "some logs"

        logs = await self.instance._get_latest_logs()

        #self.k8s_manager_mock.get_job_logs.assert_called_once_with('some_pid', '2023-08-25T02:55:22.210915+00:00')
        self.assertEqual(logs, "some logs")

    async def test_retrieve_job_logs_calls_get_latest_logs(self):
        self.k8s_manager_mock.get_job_logs.return_value = "some logs"

        with patch.object(self.instance, '_get_latest_logs', new_callable=AsyncMock) as mock_get_logs:
            await self.instance._retrieve_job_logs()

        mock_get_logs.assert_called_once()


class TestKubernetesProcessManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        job_store = None
        self._manager = KubernetesProcessManager(job_store=job_store)

    def tearDown(self) -> None:
        self._manager.stop()
        self._manager = None

    def _write_logs_to_instance(self, instance: BaseInstance, logs: List[str]):
        for log in logs:
            instance._on_stdout_message(log)

    def _set_up_instance(self, write_logs=True) -> _FakeInstance:
        instance = _FakeInstance("foo_cmd", [])
        if write_logs:
            self._write_logs_to_instance(instance, LOGS)
        self._manager._active_processes["foo"].append(instance)

        return instance

    async def test_allowed_args_separator(self):
        args = {
            "foo": "bar"
        }

        allowed_args = {
            "foo": {"arg": "--foo", "default": "default", "separator": "="}
        }

        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ["--foo=bar"])

    async def test_allowed_args_separator_no_separator(self):
        args = {
            "foo": "bar"
        }

        allowed_args = {
            "foo": {"arg": "--foo", "default": "default"}
        }

        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ["--foo=bar"])

    async def test_allowed_args_separator_space_separator(self):
        args = {
            "foo": "bar"
        }

        allowed_args = {
            "foo": {"arg": "--foo", "default": "default", "separator": " "}
        }

        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ["--foo", "bar"])

    async def test_allowed_args_positional(self):
        args = {
            "foo": "bar",
        }

        allowed_args = {
            "foo": {"arg": 0, "default": "boo"}
        }

        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ["bar"])

    async def test_allowed_args_positional_mixed(self):
        args = {
            "foo": "bar",
            "sync": "now"
        }

        allowed_args = {
            "foo": {"arg": "--foo", "default": "default", "separator": "="},
            "sync": {"arg": 0, "default": "default"}
        }

        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ["now", "--foo=bar"])

    async def test_allowed_args_positional_mixed_spaces(self):
        args = {
            "foo": "bar",
            "bar": "foo",
            "sync": "now",
            "verbose": "-v"
        }

        allowed_args = {
            "foo": {"arg": "--foo", "default": "default", "separator": "="},
            "bar": {"arg": "--bar", "default": "default", "separator": "="},
            "sync": {"arg": 0, "default": "default"},
            "verbose": {"arg": 1, "default": "--verbose"},
        }

        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ['now', '-v', '--foo=bar', '--bar=foo'])

    async def test_allowed_args_positional_is_str_mixed(self):
        args = {
            'scene': 'foo',
            'frames': '5',
            'sync': 'today'
        }

        allowed_args = {
            'scene': {'arg': '--scene', 'default': 'simple'},
            'frames': {'arg': '--frames', 'default': '7'},
            'sync': {'arg': "0", 'default': 'now'}
        }


        res = self._manager._process_allowed_args(args, allowed_args)
        self.assertEqual(res, ['today', '--scene=foo', '--frames=5'])

    async def test_get_jobs_status_bulk(self):
        """Test bulk job status retrieval for all jobs in namespace."""
        # Create mock job objects that will be returned by list_namespaced_job
        mock_job_1 = Mock()
        mock_job_1.metadata.name = "job-1"
        mock_job_1.status.succeeded = 1
        mock_job_1.status.failed = None
        mock_job_1.status.active = None
        mock_job_1.status.ready = None

        mock_job_2 = Mock()
        mock_job_2.metadata.name = "job-2"
        mock_job_2.status.succeeded = None
        mock_job_2.status.failed = 1
        mock_job_2.status.active = None
        mock_job_2.status.ready = None

        mock_job_3 = Mock()
        mock_job_3.metadata.name = "job-3"
        mock_job_3.status.succeeded = None
        mock_job_3.status.failed = None
        mock_job_3.status.active = 1
        mock_job_3.status.ready = 1

        # Create mock job list response
        mock_job_list = Mock()
        mock_job_list.items = [mock_job_1, mock_job_2, mock_job_3]
        mock_job_list.metadata._continue = None  # No pagination needed

        # Mock the Kubernetes API list_namespaced_job call
        with patch.object(self._manager._k8s_client_mgr, '_initialize_clients', new_callable=AsyncMock):
            with patch.object(self._manager._k8s_client_mgr.apis, 'BatchV1Api') as mock_batch_api:
                mock_api_instance = Mock()
                mock_batch_api.return_value = mock_api_instance

                # Mock the list_namespaced_job to return a mock with .get() method
                mock_list_result = Mock()
                mock_list_result.get = AsyncMock(return_value=mock_job_list)
                mock_api_instance.list_namespaced_job.return_value = mock_list_result

                # Call the actual bulk method (no job_names arg - returns all jobs in namespace)
                result = await self._manager._k8s_client_mgr.get_jobs_status_bulk()

        # Verify results - These assertions test the REAL implementation logic
        self.assertEqual(len(result), 3)  # Tests that all 3 jobs in namespace are returned
        self.assertEqual(result["job-1"], "Succeeded")  # Tests status mapping for succeeded
        self.assertEqual(result["job-2"], "Failed")  # Tests status mapping for failed
        self.assertEqual(result["job-3"], "Running")  # Tests status mapping for active/running

        # Verify limit was set correctly (250 is the default from list_jobs_limit_per_page configuration)
        call_kwargs = mock_api_instance.list_namespaced_job.call_args[1]
        self.assertEqual(call_kwargs["limit"], 250)

    async def test_get_jobs_status_bulk_with_pagination(self):
        """Test bulk job status retrieval with pagination across multiple pages."""
        # Create mock jobs for first page
        mock_job_1 = Mock()
        mock_job_1.metadata.name = "job-1"
        mock_job_1.status.succeeded = 1
        mock_job_1.status.failed = None
        mock_job_1.status.active = None
        mock_job_1.status.ready = None

        mock_job_2 = Mock()
        mock_job_2.metadata.name = "job-2"
        mock_job_2.status.succeeded = None
        mock_job_2.status.failed = 1
        mock_job_2.status.active = None
        mock_job_2.status.ready = None

        # Create first page response with continue token
        mock_job_list_page1 = Mock()
        mock_job_list_page1.items = [mock_job_1, mock_job_2]
        mock_job_list_page1.metadata._continue = "continue-token-123"

        # Create mock jobs for second page
        mock_job_3 = Mock()
        mock_job_3.metadata.name = "job-3"
        mock_job_3.status.succeeded = None
        mock_job_3.status.failed = None
        mock_job_3.status.active = 1
        mock_job_3.status.ready = 1

        mock_job_4 = Mock()
        mock_job_4.metadata.name = "job-4"
        mock_job_4.status.succeeded = 1
        mock_job_4.status.failed = None
        mock_job_4.status.active = None
        mock_job_4.status.ready = None

        # Create second page response without continue token (last page)
        mock_job_list_page2 = Mock()
        mock_job_list_page2.items = [mock_job_3, mock_job_4]
        mock_job_list_page2.metadata._continue = None

        # Mock the Kubernetes API to return different pages
        with patch.object(self._manager._k8s_client_mgr, '_initialize_clients', new_callable=AsyncMock):
            with patch.object(self._manager._k8s_client_mgr.apis, 'BatchV1Api') as mock_batch_api:
                mock_api_instance = Mock()
                mock_batch_api.return_value = mock_api_instance

                # Create mocks for both API calls
                mock_list_result_page1 = Mock()
                mock_list_result_page1.get = AsyncMock(return_value=mock_job_list_page1)

                mock_list_result_page2 = Mock()
                mock_list_result_page2.get = AsyncMock(return_value=mock_job_list_page2)

                # Configure the mock to return different results for each call
                mock_api_instance.list_namespaced_job.side_effect = [
                    mock_list_result_page1,
                    mock_list_result_page2
                ]

                # Call the actual bulk method (returns all jobs in namespace across pages)
                result = await self._manager._k8s_client_mgr.get_jobs_status_bulk()

        # Verify that the API was called twice (pagination)
        self.assertEqual(mock_api_instance.list_namespaced_job.call_count, 2)

        # Verify the second call included the continue token
        second_call_kwargs = mock_api_instance.list_namespaced_job.call_args_list[1][1]
        self.assertEqual(second_call_kwargs["_continue"], "continue-token-123")

        # Verify all jobs from both pages are in the result
        self.assertEqual(len(result), 4)
        self.assertEqual(result["job-1"], "Succeeded")
        self.assertEqual(result["job-2"], "Failed")
        self.assertEqual(result["job-3"], "Running")
        self.assertEqual(result["job-4"], "Succeeded")

    async def test_get_jobs_status_bulk_all_jobs_retrieved(self):
        """Test that all jobs in namespace are retrieved, not filtered by job names."""
        # Create mock jobs for first page
        mock_job_1 = Mock()
        mock_job_1.metadata.name = "job-1"
        mock_job_1.status.succeeded = 1
        mock_job_1.status.failed = None
        mock_job_1.status.active = None
        mock_job_1.status.ready = None

        mock_job_2 = Mock()
        mock_job_2.metadata.name = "job-2"
        mock_job_2.status.succeeded = None
        mock_job_2.status.failed = None
        mock_job_2.status.active = 1
        mock_job_2.status.ready = 1

        # Include additional jobs in the namespace
        mock_job_other = Mock()
        mock_job_other.metadata.name = "job-other"
        mock_job_other.status.succeeded = 1
        mock_job_other.status.failed = None
        mock_job_other.status.active = None
        mock_job_other.status.ready = None

        # Create response with all jobs in namespace
        mock_job_list = Mock()
        mock_job_list.items = [mock_job_1, mock_job_other, mock_job_2]
        mock_job_list.metadata._continue = None

        # Mock the Kubernetes API
        with patch.object(self._manager._k8s_client_mgr, '_initialize_clients', new_callable=AsyncMock):
            with patch.object(self._manager._k8s_client_mgr.apis, 'BatchV1Api') as mock_batch_api:
                mock_api_instance = Mock()
                mock_batch_api.return_value = mock_api_instance

                mock_list_result = Mock()
                mock_list_result.get = AsyncMock(return_value=mock_job_list)
                mock_api_instance.list_namespaced_job.return_value = mock_list_result

                # Call the bulk method (no filtering, returns all jobs in namespace)
                result = await self._manager._k8s_client_mgr.get_jobs_status_bulk()

        # Verify that the API was called once
        self.assertEqual(mock_api_instance.list_namespaced_job.call_count, 1)

        # Verify all jobs in namespace are in the result (no filtering)
        self.assertEqual(len(result), 3)
        self.assertEqual(result["job-1"], "Succeeded")
        self.assertEqual(result["job-2"], "Running")
        self.assertEqual(result["job-other"], "Succeeded")

    def test_update_process(self):
        """Test updating a single process status."""
        # Create a mock process
        mock_process = Mock()
        mock_process._process = Mock()
        mock_process._process.pid = "test-job-1"
        mock_process.status = "starting"

        # Test Succeeded status (logs NOT retrieved in update_process)
        self._manager.update_process(mock_process, status="Succeeded")
        mock_process._process.set_returncode.assert_called_with(0)
        mock_process._process.set_status.assert_called_with("finished")

        # Reset mocks
        mock_process._process.reset_mock()

        # Test Failed status (logs NOT retrieved in update_process)
        self._manager.update_process(mock_process, status="Failed")
        mock_process._process.set_returncode.assert_called_with(-1)
        mock_process._process.set_status.assert_called_with("errored")

        # Reset mocks
        mock_process._process.reset_mock()

        # Test Running status (should update to running)
        self._manager.update_process(mock_process, status="Running")
        mock_process._process.set_status.assert_called_with("running")

        # Reset mocks
        mock_process._process.reset_mock()

        # Test Running status when already running (should NOT update, just return)
        mock_process.status = "running"
        self._manager.update_process(mock_process, status="Running")
        mock_process._process.set_status.assert_not_called()  # Should not be called
        mock_process._process.set_returncode.assert_not_called()  # Should not error out

        # Reset mocks
        mock_process._process.reset_mock()

        # Test Starting status (job just created)
        mock_process.status = "idle"  # Different from "starting"
        self._manager.update_process(mock_process, status="Starting")
        mock_process._process.set_status.assert_called_with("starting")

        # Reset mocks
        mock_process._process.reset_mock()

        # Test None status (unmapped/unexpected state - should error)
        self._manager.update_process(mock_process, status=None)
        mock_process._process.set_returncode.assert_called_with(-1)
        mock_process._process.set_status.assert_called_with("errored")

        # Reset mocks
        mock_process._process.reset_mock()

        # Test Starting status when already starting (should NOT update, just return)
        mock_process.status = "starting"
        self._manager.update_process(mock_process, status="Starting")
        mock_process._process.set_status.assert_not_called()  # Should not be called
        mock_process._process.set_returncode.assert_not_called()  # Should not error out

        # Reset mocks
        mock_process._process.reset_mock()

        # Test unmapped/unknown status (the else branch)
        self._manager.update_process(mock_process, status="UnknownStatus")
        mock_process._process.set_returncode.assert_called_with(-1)
        mock_process._process.set_status.assert_called_with("errored")

    async def test_update_processes(self):
        """Test bulk process updates (status sync only, logs handled by monitor_processes)."""
        # Create mock processes
        mock_process_1 = Mock()
        mock_process_1._process = Mock()
        mock_process_1._process.pid = "job-1"
        mock_process_1._process.returncode = None
        # Make set_returncode actually set the value
        mock_process_1._process.set_returncode = Mock(side_effect=lambda rc: setattr(mock_process_1._process, 'returncode', rc))
        mock_process_1.status = "running"
        # Make is_active return False after returncode is set
        type(mock_process_1).is_active = PropertyMock(side_effect=lambda: mock_process_1._process.returncode is None)

        mock_process_2 = Mock()
        mock_process_2._process = Mock()
        mock_process_2._process.pid = "job-2"
        mock_process_2._process.returncode = None
        mock_process_2.status = "starting"  # Different status so it gets updated
        # Make is_active return True (stays running)
        type(mock_process_2).is_active = PropertyMock(side_effect=lambda: mock_process_2._process.returncode is None)

        # Add processes to active list
        self._manager._active_processes["test-job"] = [mock_process_1, mock_process_2]

        # Create mock Kubernetes job responses
        mock_job_1 = Mock()
        mock_job_1.metadata.name = "job-1"
        mock_job_1.status.succeeded = 1
        mock_job_1.status.failed = None
        mock_job_1.status.active = None
        mock_job_1.status.ready = None

        mock_job_2 = Mock()
        mock_job_2.metadata.name = "job-2"
        mock_job_2.status.succeeded = None
        mock_job_2.status.failed = None
        mock_job_2.status.active = 1
        mock_job_2.status.ready = 1

        mock_job_list = Mock()
        mock_job_list.items = [mock_job_1, mock_job_2]
        mock_job_list.metadata._continue = None

        # Mock the Kubernetes API
        with patch.object(self._manager._k8s_client_mgr, '_initialize_clients', new_callable=AsyncMock):
            with patch.object(self._manager._k8s_client_mgr.apis, 'BatchV1Api') as mock_batch_api:
                mock_api_instance = Mock()
                mock_batch_api.return_value = mock_api_instance

                mock_list_result = Mock()
                mock_list_result.get = AsyncMock(return_value=mock_job_list)
                mock_api_instance.list_namespaced_job.return_value = mock_list_result

                # Call the real update_processes method
                await self._manager.update_processes()

        # Verify processes were updated based on the K8s job statuses
        # Note: Logs are NOT retrieved in update_processes anymore, only in monitor_processes
        mock_process_1._process.set_returncode.assert_called_with(0)
        mock_process_1._process.set_status.assert_called_with("finished")
        mock_process_2._process.set_status.assert_called_with("running")

    async def test_update_processes_batch_log_retrieval(self):
        """Test that terminal processes retrieve logs in parallel using asyncio.gather in monitor_processes."""
        # Create multiple mock processes in terminal states
        mock_process_1 = Mock()
        mock_process_1._process = Mock()
        mock_process_1._process.pid = "job-1"
        mock_process_1._process.returncode = None
        mock_process_1._process.set_returncode = Mock(side_effect=lambda rc: setattr(mock_process_1._process, 'returncode', rc))
        mock_process_1.status = "running"
        type(mock_process_1).is_active = PropertyMock(side_effect=lambda: mock_process_1._process.returncode is None)
        mock_process_1.completed = True
        mock_process_1.returncode = 0
        mock_process_1.process_id = "job-1"
        mock_process_1.get_logs = Mock(return_value=[])
        mock_process_1.shutdown = Mock()
        mock_process_1._log_check_delay = 0.01
        mock_process_1._retrieve_job_logs = AsyncMock()

        mock_process_2 = Mock()
        mock_process_2._process = Mock()
        mock_process_2._process.pid = "job-2"
        mock_process_2._process.returncode = None
        mock_process_2._process.set_returncode = Mock(side_effect=lambda rc: setattr(mock_process_2._process, 'returncode', rc))
        mock_process_2.status = "running"
        type(mock_process_2).is_active = PropertyMock(side_effect=lambda: mock_process_2._process.returncode is None)
        mock_process_2.completed = True
        mock_process_2.returncode = 0
        mock_process_2.process_id = "job-2"
        mock_process_2.get_logs = Mock(return_value=[])
        mock_process_2.shutdown = Mock()
        mock_process_2._log_check_delay = 0.01
        mock_process_2._retrieve_job_logs = AsyncMock()

        mock_process_3 = Mock()
        mock_process_3._process = Mock()
        mock_process_3._process.pid = "job-3"
        mock_process_3._process.returncode = None
        mock_process_3._process.set_returncode = Mock(side_effect=lambda rc: setattr(mock_process_3._process, 'returncode', rc))
        mock_process_3.status = "running"
        type(mock_process_3).is_active = PropertyMock(side_effect=lambda: mock_process_3._process.returncode is None)
        mock_process_3.completed = False
        mock_process_3.returncode = -1
        mock_process_3.process_id = "job-3"
        mock_process_3.get_logs = Mock(return_value=[])
        mock_process_3.shutdown = Mock()
        mock_process_3._log_check_delay = 0.01
        mock_process_3._retrieve_job_logs = AsyncMock()

        # Add processes to active list
        self._manager._active_processes["test-job"] = [mock_process_1, mock_process_2, mock_process_3]

        # Create mock Kubernetes job responses - 2 succeeded, 1 failed (all terminal)
        mock_job_1 = Mock()
        mock_job_1.metadata.name = "job-1"
        mock_job_1.status.succeeded = 1
        mock_job_1.status.failed = None
        mock_job_1.status.active = None
        mock_job_1.status.ready = None

        mock_job_2 = Mock()
        mock_job_2.metadata.name = "job-2"
        mock_job_2.status.succeeded = 1
        mock_job_2.status.failed = None
        mock_job_2.status.active = None
        mock_job_2.status.ready = None

        mock_job_3 = Mock()
        mock_job_3.metadata.name = "job-3"
        mock_job_3.status.succeeded = None
        mock_job_3.status.failed = 1
        mock_job_3.status.active = None
        mock_job_3.status.ready = None

        mock_job_list = Mock()
        mock_job_list.items = [mock_job_1, mock_job_2, mock_job_3]
        mock_job_list.metadata._continue = None

        # Mock the Kubernetes API
        with patch.object(self._manager._k8s_client_mgr, '_initialize_clients', new_callable=AsyncMock):
            with patch.object(self._manager._k8s_client_mgr.apis, 'BatchV1Api') as mock_batch_api:
                mock_api_instance = Mock()
                mock_batch_api.return_value = mock_api_instance

                mock_list_result = Mock()
                mock_list_result.get = AsyncMock(return_value=mock_job_list)
                mock_api_instance.list_namespaced_job.return_value = mock_list_result

                # Call monitor_processes which should retrieve logs in batch
                await self._manager.monitor_processes()

                # Verify all three processes had their logs retrieved in parallel
                mock_process_1._retrieve_job_logs.assert_called_once()
                mock_process_2._retrieve_job_logs.assert_called_once()
                mock_process_3._retrieve_job_logs.assert_called_once()

                # Verify all three terminal processes had their statuses updated
                mock_process_1._process.set_status.assert_called_with("finished")
                mock_process_2._process.set_status.assert_called_with("finished")
                mock_process_3._process.set_status.assert_called_with("errored")

    async def test_update_processes_empty(self):
        """Test update_processes with no active jobs."""
        # Mock the K8s client manager
        self._manager._k8s_client_mgr = AsyncMock()

        # Call update_processes with no active processes
        await self._manager.update_processes()

        # Verify bulk API was not called
        self._manager._k8s_client_mgr.get_jobs_status_bulk.assert_not_called()

    async def test_monitor_processes(self):
        """Test monitor_processes calls update_processes and processes are transitioned correctly."""
        # Create a mock process that will be marked as finished
        mock_process = Mock()
        mock_process._process = Mock()
        mock_process._process.pid = "job-1"
        mock_process.is_active = False
        mock_process.completed = True
        mock_process.returncode = 0
        mock_process.process_id = "job-1"
        mock_process.get_logs.return_value = []
        mock_process.shutdown = Mock()
        mock_process._log_check_delay = 0.01
        mock_process._retrieve_job_logs = AsyncMock()

        self._manager._active_processes["test-job"] = [mock_process]

        # Create mock Kubernetes job response (finished job)
        mock_job = Mock()
        mock_job.metadata.name = "job-1"
        mock_job.status.succeeded = 1
        mock_job.status.failed = None
        mock_job.status.active = None
        mock_job.status.ready = None

        mock_job_list = Mock()
        mock_job_list.items = [mock_job]
        mock_job_list.metadata._continue = None

        # Mock the Kubernetes API
        with patch.object(self._manager._k8s_client_mgr, '_initialize_clients', new_callable=AsyncMock):
            with patch.object(self._manager._k8s_client_mgr.apis, 'BatchV1Api') as mock_batch_api:
                mock_api_instance = Mock()
                mock_batch_api.return_value = mock_api_instance

                mock_list_result = Mock()
                mock_list_result.get = AsyncMock(return_value=mock_job_list)
                mock_api_instance.list_namespaced_job.return_value = mock_list_result

                # Call monitor_processes
                await self._manager.monitor_processes()

        # Verify final logs were retrieved
        mock_process._retrieve_job_logs.assert_called_once()
        # Verify the process was moved to finished_processes
        self.assertEqual(len(self._manager._active_processes["test-job"]), 0)
        self.assertEqual(len(self._manager._finished_processes["test-job"]), 1)
        mock_process.shutdown.assert_called_once()

    def test_map_k8s_job_status_active_and_ready(self):
        """Test that active=1 and ready=1 returns Running."""
        mock_job_status = Mock()
        mock_job_status.succeeded = None
        mock_job_status.failed = None
        mock_job_status.active = 1
        mock_job_status.ready = 1  # Pod is ready

        status = self._manager._k8s_client_mgr._map_k8s_job_status_to_string(mock_job_status)
        self.assertEqual(status, "Running")

    def test_map_k8s_job_status_active_not_ready(self):
        """Test that active=1 but ready=0 returns Starting."""
        mock_job_status = Mock()
        mock_job_status.succeeded = None
        mock_job_status.failed = None
        mock_job_status.active = 1
        mock_job_status.ready = 0  # Pod not ready yet

        status = self._manager._k8s_client_mgr._map_k8s_job_status_to_string(mock_job_status)
        self.assertEqual(status, "Starting")

    def test_map_k8s_job_status_active_ready_none(self):
        """Test that active=1 but ready=None returns Starting (K8s < 1.24)."""
        mock_job_status = Mock()
        mock_job_status.succeeded = None
        mock_job_status.failed = None
        mock_job_status.active = 1
        mock_job_status.ready = None  # Older K8s version

        status = self._manager._k8s_client_mgr._map_k8s_job_status_to_string(mock_job_status)
        self.assertEqual(status, "Starting")

