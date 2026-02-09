# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import platform
import unittest

from contextlib import contextmanager
from typing import List, Optional

from nv.svc.farm.services.jobs.job_types.base import BaseJob
from nv.svc.farm.services.jobs.facilities.manager.base import BaseInstance


LOGS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Integer tincidunt lacus nec arcu malesuada, sed congue diam dignissim.",
    "In ac est at risus consectetur commodo et sit amet mauris.",
    "In eget erat a ante rutrum viverra vel quis turpis.",
]


def is_windows() -> bool:
    """
    Check if the current host environment is Windows.

    Args:
        None

    Returns:
        bool: A flag indicating whether the current host environment is Windows.

    """
    return platform.system().lower() == "windows"


class FakeProcess(object):

    def __init__(self, pid: int, returncode: int) -> None:
        self._pid = pid
        self._returncode = returncode

    @property
    def pid(self) -> int:
        return -1

    @property
    def returncode(self) -> int:
        return self._returncode


class FakeProcessWithStatus(FakeProcess):

    def __init__(self, pid: int, returncode: int, status: str) -> None:
        super().__init__(pid, returncode)
        self._status = status

    @property
    def status(self) -> str:
        return self._status


class TestJobsBaseInstance(unittest.IsolatedAsyncioTestCase):

    @contextmanager
    def _create_process_instance(self, command: Optional[str] = None) -> BaseInstance:
        if not command:
            # Use an arbitrary low-overhead executable to perform the test on a real process:
            command = "dir" if is_windows() else "ls"

        job = BaseJob(command=command, args=[])
        instance = BaseInstance(
            command=job.command,
            container=None,
            args=job.args,
            env=job.env,
        )

        try:
            yield instance
        finally:
            if instance.process_id:
                instance.stop()

    def test_logs_are_appended_to_stdout_stream(self):
        """Test logs are appended to the stdout stream."""
        container = None
        instance = BaseInstance("foo_cmd", container, [])
        for log in LOGS:
            instance._on_stdout_message(log)

        self.assertEqual(instance.get_logs(), LOGS)

    def test_logs_are_reset_after_read(self):
        """Test logs are reset after having been read."""
        container = None
        instance = BaseInstance("foo_cmd", container, [])
        for log in LOGS:
            instance._on_stdout_message(log)

        self.assertEqual(len(instance._std_output), 4)
        instance.get_logs()
        self.assertEqual(len(instance._std_output), 0)

    def test_logs_can_be_written_after_reading(self):
        """Test that logs can still be written after reading them."""
        container = None
        instance = BaseInstance("foo_cmd", container, [])
        for log in LOGS:
            instance._on_stdout_message(log)

        self.assertEqual(instance.get_logs(), LOGS)

        instance._on_stdout_message("test log")
        self.assertEqual(instance.get_logs(), ["test log"])

    @unittest.skipIf(
        condition=is_windows(),
        reason="Test will not succeed on Windows due to missing environment variables.",
    )
    async def test_spawning_a_command_creates_a_process(self):
        with self._create_process_instance() as instance:
            self.assertIsNone(instance.process_id)
            process = await instance.spawn_async()

            self.assertIsNotNone(instance)
            self.assertIsNotNone(instance.process_id)
            self.assertIsNotNone(process)
            self.assertEqual(str(process.pid), instance.process_id)

    async def test_spawning_a_command_not_found_raises_an_exception(self):
        with self._create_process_instance(command="xxxxxxxxx") as instance:
            with self.assertRaises(FileNotFoundError):
                await instance.spawn_async()

    async def test_default_status(self):
        container = None
        instance = BaseInstance("foo_cmd", container, [])
        self.assertIsNone(instance.status)

    async def test_state_is_errored_when_no_process_or_valid_returncode(self):
        container = None
        instance = BaseInstance("foo_cmd", container, [])

        instance._process = FakeProcess(-1, None)
        self.assertEqual(instance.status, "errored")

    async def test_state_is_finished_valid_returncode(self):
        container = None
        instance = BaseInstance("foo_cmd", container, [])

        instance._process = FakeProcess(-1, 0)
        self.assertEqual(instance.status, "finished")

    async def test_state_is_status_from_process(self):
        container = None
        instance = BaseInstance("foo_cmd", container, [])

        instance._process = FakeProcessWithStatus(-1, 0, "this_status")
        self.assertEqual(instance.status, "this_status")
