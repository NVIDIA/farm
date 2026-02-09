# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nv.svc.farm.services.jobs.facilities.manager.base import ProcessManager
from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore
from nv.svc.farm.services.jobs.job_types.base import BaseJob
from nv.svc.farm.services.jobs.definitions import JobDefinition


_test_job_definition = JobDefinition(
    name="test-job",
    job_type="base",
    command="foo",
    job_spec_path="foo",
    args=[],
    active=True,
    success_return_codes=[0, 123456789]
)

_test_job_definition_with_function = JobDefinition(
    name="test-job-with-function",
    job_type="base",
    command="foo",
    task_function="foo.bar",
    job_spec_path="foo",
    args=[],
    active=True,
    success_return_codes=[0]
)


class MockJobStore(BaseJobStore):

    async def _load_jobs(self) -> None:
        self._jobs = {"test-job": _test_job_definition, "test-job-with-function": _test_job_definition_with_function}


class MockProcessManager(ProcessManager):

    def create_instance_from_job(self, pid: int, is_active: bool, returncode: int = 0, job_type: str = 'test-job', status: str = "running") -> None:

        instance = self._create_instance_from_job(BaseJob.from_job_definition(_test_job_definition))
        proc = MockProcess(pid=pid, is_active=is_active, returncode=returncode, status=status)
        instance._process = proc

        self._active_processes[job_type].append(instance)
        self._process_std_output[instance.process_id] = []

        def mock_is_active():
            return proc.is_active

        instance._resolve_is_active = mock_is_active

    def stop_process(self, process_type, process_id, kill=False):
        return 0


class MockProcess(object):

    def __init__(self, pid: int, is_active: bool = True, returncode: int = 0, status: str = "running"):
        self._pid = pid
        self._is_active = is_active
        self._returncode = returncode
        self.status = status

    @property
    def pid(self):
        return self._pid

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value

    @property
    def returncode(self):
        return self._returncode

    @returncode.setter
    def returncode(self, value: int):
        self._returncode = value

    def terminate(self):
        self._is_active = False

    def kill(self):
        self._is_active = False
