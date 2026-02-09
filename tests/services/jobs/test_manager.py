# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List
from unittest import mock, IsolatedAsyncioTestCase

from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.facilities.manager.base import BaseInstance, ProcessManager
from nv.svc.farm.services.jobs.job_types.base import BaseJob


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


class RequirementsBaseInstance:
    """Test Base Instance class."""

    def __init__(self, spawn_async_mock: mock.AsyncMock, *args, **kwargs):
        self.process_id = "12345"
        self.status = "running"
        self.spawn_async_mock = spawn_async_mock

    async def spawn_async(self, requirements, metadata):
        return await self.spawn_async_mock(requirements=requirements, metadata=metadata)


class RequirementsProcessManager(ProcessManager):
    """Test Process Manager class."""

    def __init__(self):
        job_store = mock.Mock()
        job = JobDefinition(
            name="test-job",
            job_type="base",
            command="echo",  # Use a command that exists
            capacity_requirements={"env": [{"name": "OV_FARM_CAPACITY_VAR", "value": "capacity_value"}]},
        )
        job_store.job_specs = {"test-job": job}
        self.spawn_async_mock = mock.AsyncMock()
        super().__init__(job_store)

    def _create_instance_from_job(self, job: BaseJob, task_id: str = None) -> RequirementsBaseInstance:
        return RequirementsBaseInstance(self.spawn_async_mock)


class TestProcessManager(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        job_store = None
        self._manager = ProcessManager(job_store=job_store)

    def tearDown(self) -> None:
        self._manager.stop()

    def _write_logs_to_instance(self, instance: BaseInstance, logs: List[str]):
        for log in logs:
            instance._on_stdout_message(log)

    def _set_up_instance(self, write_logs=True) -> _FakeInstance:
        container = None
        instance = _FakeInstance("foo_cmd", container, [])
        if write_logs:
            self._write_logs_to_instance(instance, LOGS)
        self._manager._active_processes["foo"].append(instance)

        return instance

    async def test_logs_are_collected_from_instance(self):
        """ Make sure logs are reset after reading them for a specific task. """
        instance = self._set_up_instance()

        self.assertEqual(self._manager.get_logs(instance.process_id), [])
        await self._manager.monitor_processes()
        self.assertEqual(self._manager.get_logs(instance.process_id), LOGS)

    async def test_logs_are_cleared_after_reading(self):
        """ Make sure logs are reset after reading them for a specific task. """
        instance = self._set_up_instance()

        await self._manager.monitor_processes()
        self.assertEqual(self._manager.get_logs(instance.process_id), LOGS)
        self.assertEqual(self._manager.get_logs(instance.process_id), [])
        self.assertFalse(instance.process_id in self._manager._process_std_output.keys())

    async def test_logs_can_be_written_after_read(self):
        """ Make sure logs can be written after they have been read. """
        instance = self._set_up_instance()

        await self._manager.monitor_processes()
        self.assertEqual(self._manager.get_logs(instance.process_id), LOGS)
        self.assertEqual(self._manager.get_logs(instance.process_id), [])

        additional_logs = ["test write"]
        self._write_logs_to_instance(instance, logs=additional_logs)
        await self._manager.monitor_processes()
        self.assertEqual(self._manager.get_logs(instance.process_id), additional_logs)

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

    async def test_process_error(self):
        task_id = "1000-2000-3000-4000"
        command = "df"
        exception = Exception("exit 2")

        with mock.patch('logging.error') as mocked_carb:
            self._manager._process_error(task_id, command, exception)

        expected_error_message = [
            '(\'ERROR: Farm Agent could not start an instance of the "df" command.\',) ',
            'Additional information from the host are listed below:\n\n',
            '<class \'Exception\'>: exit 2\n'
        ]
        mocked_carb.assert_called_once_with("\n".join(expected_error_message))

        has_message_on_stdout = False
        errored_process = None
        for error_process_id, value in self._manager._process_std_output.items():
            if value == expected_error_message:
                errored_process = error_process_id
                has_message_on_stdout = True

        self.assertEqual(self._manager._taskid_process_map[errored_process], task_id)
        self.assertTrue(has_message_on_stdout)

    async def test_capacity_requirements_are_merged_with_task_requirements(self):
        process_manager = RequirementsProcessManager()
        task_requirements = {"env": [{"name": "OV_ENV_TEST", "value": "123"}]}
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {"allowed_args": {}, "metadata": {}, "task_requirements": task_requirements},
        }

        # Spawn the process
        await process_manager.spawn("test-job", payload, task_id="test-task-123")

        # Assert spawn_async was called once
        process_manager.spawn_async_mock.assert_called_once()
        assert process_manager.spawn_async_mock.call_args[1]["requirements"] == {
            "env": [
                {"name": "OV_FARM_CAPACITY_VAR", "value": "capacity_value"},
                {"name": "OV_ENV_TEST", "value": "123"},
                {"name": "OV_FARM_TASK_ID", "value": "test-task-123"},
            ]
        }

    async def test_task_requirements_overwrite_capacity_requirements(self):
        process_manager = RequirementsProcessManager()
        task_requirements = {"env": [{"name": "OV_FARM_CAPACITY_VAR", "value": "overwrite_value"}]}
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {"allowed_args": {}, "metadata": {}, "task_requirements": task_requirements},
        }

        await process_manager.spawn("test-job", payload, task_id="test-task-123")

        process_manager.spawn_async_mock.assert_called_once()
        assert process_manager.spawn_async_mock.call_args[1]["requirements"] == {
            "env": [
                {"name": "OV_FARM_CAPACITY_VAR", "value": "overwrite_value"},
                {"name": "OV_FARM_TASK_ID", "value": "test-task-123"},
            ]
        }
