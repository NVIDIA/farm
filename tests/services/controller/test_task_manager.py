# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import uuid

from typing import Dict, List, Tuple
from urllib.parse import urlparse

from unittest import IsolatedAsyncioTestCase
from unittest import mock

from fastapi.testclient import TestClient

from nv.svc.core import main
from nv.svc.core.client.http import HTTPClientSession

from nv.svc.farm.services.tasks.facilities.tasks import backends, store

from nv.svc.farm.services.controller.config import FarmControllerConfig
from nv.svc.farm.services.controller.facilities.bays import OneSlotBay
from nv.svc.farm.services.controller.task_manager import TaskManager, get_utc_unixtime

from ._mocks import MockJobStore, MockProcessManager


class MockTaskManager(TaskManager):
    pass


class FakeResponse:
    def __init__(self, data=None):
        self.data = data or {}

    async def json(self):
        return self.data


class TestTaskManager(IsolatedAsyncioTestCase):

    TEST_FETCH_TASK_STATUS_ID = "0ffa-aabb-cccc-ddd"

    async def asyncSetUp(self):
        self._current_pid = 1

        self._task_update_calls = []

        def get_new_task():
            return {
                "task_id": self.TEST_FETCH_TASK_STATUS_ID,
                "task_type": "test-job",
                "task_args": [],
                "task_function": "",
                "metadata": {},
                "userid": "foo",
                "status": "creating",
                "task_requirements": {}
            }

        config = FarmControllerConfig()
        core = main.ServicesCore(
            title="controller",
            description="Farm Controller",
            version="0",
        )
        job_store = MockJobStore()
        await job_store.load_jobs()
        self._process_manager = MockProcessManager(job_store=job_store)
        core.register_facility("process_manager", self._process_manager)

        self._task_store = store.TaskStore(backends.TaskIdDictBackend())
        self._manager = MockTaskManager(
            task_store=self._task_store,
            bay_controller=OneSlotBay(),
            config=config,
            process_manager=self._process_manager,
            agent_id="test_agent",
        )

        self._client = TestClient(core._app)

        async def _fake_request(*rargs, **kwargs):
            method = rargs[1].lower()
            url_path = urlparse(rargs[2]).path
            rdata = None
            if "/tasks/fetch" in url_path:
                rdata = get_new_task()
            elif "/tasks/update" in url_path:
                self._task_update_calls.append(kwargs.get("json"))
            elif "/tasks/info" in url_path:
                rdata = {"status": "running"}
            elif "/tasks/revision-history" in url_path:
                rdata = []
            else:
                if method == "post":
                    resp = self._client.post(url_path, data=kwargs.get("json"))
                elif method == "get":
                    resp = self._client.get(url_path)
                rdata = resp.json()

            return FakeResponse(data=rdata)

        self.client_session_patcher = mock.patch.object(HTTPClientSession, "_request", _fake_request)
        self.client_session_patcher.start()

    def tearDown(self):
        self.client_session_patcher.stop()

    async def _generate_tasks(
        self,
        starting_count: int = 0,
        running_count: int = 0,
        finished_count: int = 0,
        errored_count: int = 0,
        task_function: str = "",
        task_type: str = "test-job",
        metadata: Dict = None
    ) -> Tuple[List, List, List, List]:

        metadata = metadata or {}

        starting_task_ids = [await self._create_task(status="starting", task_function=task_function, task_type=task_type, metadata=metadata) for _ in range(starting_count)]
        running_tasks_id = [await self._create_task(status="running", task_function=task_function, task_type=task_type, metadata=metadata) for _ in range(running_count)]
        finished_task_ids = [await self._create_task(status="finished", task_function=task_function, task_type=task_type, metadata=metadata) for _ in range(finished_count)]
        errored_task_ids = [await self._create_task(status="errored", task_function=task_function, task_type=task_type, metadata=metadata) for _ in range(errored_count)]

        return starting_task_ids, running_tasks_id, finished_task_ids, errored_task_ids

    async def _create_task(self, task_type: str = "test-job", status: str = "running", task_function: str = "",  metadata: Dict = None):
        """
        Create a test task

        Kwargs:
            task_type (str): Task type name.
            status (str): Status of the task
        """
        task_id = str(uuid.uuid4())

        # To simplify the test setup, if we create a task, unless it's in a starting state, it should be running.
        _status = status if status in ("starting", "running") else "running"

        # The TaskManager is meant to move them to errored or finished depending on the return code.
        await self._task_store.insert_existing_task(
            task_id, status=_status, task_function=task_function, task_type=task_type, userid="foo", metadata=metadata)

        pid = int(self._current_pid)
        self._current_pid += 1

        active = True
        returncode = None

        if status == "errored":
            active = False
            returncode = 1

        elif status == "finished":
            active = False
            returncode = 0

        self._process_manager.create_instance_from_job(
            pid, is_active=active, returncode=returncode, job_type=task_type, status=_status)

        task_function = task_function
        self._manager._task_process_map[(task_type, task_function)][task_id] = {
            "process_id": str(pid),
            "checkin_time": 0,
        }
        return task_id, str(pid)

    async def _run_checks(self):
        """
        Runs the process manager and task manager process check cycles

        These cycles check if processes are still active and if tasks have failed depending on active processes.
        """
        await self._process_manager.monitor_processes()
        await self._manager._check_tasks()

    async def test_generate_task(self):
        """Test the test task generation functions to validate their functionality"""
        await self._generate_tasks(running_count=1)
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 1)

    async def test_generate_task_multiple(self):
        """Test the test task generation functions to validate their functionality"""
        await self._generate_tasks(running_count=2, finished_count=1, errored_count=3)
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 6)

    async def test_generate_active_job(self):
        """Test the test job generation functions to validate their functionality"""
        await self._generate_tasks(running_count=1)
        res = self._process_manager.active_processes["test-job"]
        self.assertEqual(len(res), 1)

    async def test_generate_active_job_multiple(self):
        """Test the test job generation functions to validate their functionality"""
        await self._generate_tasks(running_count=3)
        res = self._process_manager.active_processes["test-job"]
        self.assertEqual(len(res), 3)

    async def test_one_running_tasks(self):
        """Test that a running task remains active after checks"""
        await self._generate_tasks(running_count=1)
        await self._run_checks()
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 1)

    async def test_one_starting_tasks(self):
        """Test that an starting task remains active after checks"""
        await self._generate_tasks(starting_count=1)
        await self._run_checks()
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 1)

    async def test_multiple_running_tasks(self):
        """Test that multiple active tasks remain active after checks"""
        await self._generate_tasks(running_count=3)
        await self._run_checks()
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 3)

    async def test_validate_starting_tasks(self):
        """Validate that the tasks reported as starting match the tasks active in the task manager"""
        starting_tasks_id, _, _, _ = await self._generate_tasks(starting_count=3)
        expected_task_ids = [task_id for task_id, _ in starting_tasks_id]

        await self._run_checks()

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["starting"])
        retrieved_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual(expected_task_ids, retrieved_task_ids)

    async def test_validate_running_tasks(self):
        """Validate that the tasks reported as active match the tasks active in the task manager"""
        _, running_tasks_id, _, _ = await self._generate_tasks(running_count=3)
        expected_task_ids = [task_id for task_id, _ in running_tasks_id]

        await self._run_checks()

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])
        retrieved_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual(expected_task_ids, retrieved_task_ids)

    async def test_validate_errored_tasks_are_active_before_checks(self):
        """Test that prior to running checks, tasks remain active, even when errored. This is expected"""
        _, running_tasks_id, _, errored_tasks_ids = await self._generate_tasks(running_count=3, errored_count=2)
        expected_running_tasks_id = [task_id for task_id, _ in running_tasks_id]
        expected_running_tasks_id.extend([task_id for task_id, _ in errored_tasks_ids])

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])

        retrieved_running_tasks_id = [task["task_id"] for task in tasks]
        self.assertEqual(expected_running_tasks_id, retrieved_running_tasks_id)

    async def test_errored_tasks(self):
        """Test that multiple active tasks remain active after checks and that the errored ones are reported as errored"""
        await self._generate_tasks(running_count=3, errored_count=2)
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 5)

        await self._run_checks()

        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 3)

    async def test_validate_errored_tasks(self):
        """Validate that the tasks reported as active and errored match the ones in the task manager"""
        _, running_tasks_id, _, errored_tasks_ids = await self._generate_tasks(running_count=3, errored_count=2)
        expected_running_tasks_id = [task_id for task_id, _ in running_tasks_id]
        expected_errored_task_ids = [task_id for task_id, _ in errored_tasks_ids]

        await self._run_checks()

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])
        retrieved_running_tasks_id = [task["task_id"] for task in tasks]

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["errored"])
        retrieved_errored_task_ids = [task["task_id"] for task in tasks]
        self.assertEqual(expected_running_tasks_id, retrieved_running_tasks_id)
        self.assertEqual(expected_errored_task_ids, retrieved_errored_task_ids)

    async def test_validate_finished_tasks_are_active_before_checks(self):
        """Test that prior to running checks, tasks remain active, even when finished. This is expected"""
        _, running_tasks_id, finished_tasks_ids, _ = await self._generate_tasks(running_count=3, finished_count=2)
        expected_running_tasks_id = [task_id for task_id, _ in running_tasks_id]
        expected_running_tasks_id.extend([task_id for task_id, _ in finished_tasks_ids])

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])

        retrieved_running_tasks_id = [task["task_id"] for task in tasks]
        self.assertEqual(expected_running_tasks_id, retrieved_running_tasks_id)

    async def test_finished_tasks(self):
        """Test that multiple active tasks remain active after checks and that the finished ones are reported as finished"""
        await self._generate_tasks(running_count=3, finished_count=2)
        res = self._manager.get_active_tasks()

        await self._run_checks()

        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 3)

    async def test_validate_finished_tasks(self):
        """Validate that the tasks reported as active and finished match the ones in the task manager"""
        _, running_tasks_id, finished_task_ids, _ = await self._generate_tasks(running_count=3, finished_count=2)
        expected_running_tasks_id = [task_id for task_id, _ in running_tasks_id]
        expected_finished_task_ids = [task_id for task_id, _ in finished_task_ids]

        await self._run_checks()

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])
        retrieved_running_tasks_id = [task["task_id"] for task in tasks]

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["finished"])
        retrieved_finished_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual(expected_running_tasks_id, retrieved_running_tasks_id)
        self.assertEqual(expected_finished_task_ids, retrieved_finished_task_ids)

    async def test_interrupt_task(self):
        """Test interrupting task"""
        _, running_tasks_id, _, _ = await self._generate_tasks(running_count=3)
        expected_running_tasks_id = [task_id for task_id, _ in running_tasks_id]

        task_id_to_cancel = expected_running_tasks_id.pop(0)
        await self._manager._interrupt_task(task_id_to_cancel)

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["cancelled"])
        retrieved_cancelled_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual([task_id_to_cancel], retrieved_cancelled_task_ids)

    async def test_interrupt_task_not_active(self):
        """Test interrupting task labels it as not running"""
        _, running_tasks_id, _, _ = await self._generate_tasks(running_count=3)
        expected_running_tasks_id = [task_id for task_id, _ in running_tasks_id]

        task_id_to_cancel = expected_running_tasks_id.pop(0)
        await self._manager._interrupt_task(task_id_to_cancel)

        await self._run_checks()

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])
        retrieved_running_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual(expected_running_tasks_id, retrieved_running_task_ids)

    async def test_non_zero_return_code(self):
        """Test that a none zero return code leads to an errored task."""
        _, running_tasks_id, _, _ = await self._generate_tasks(running_count=3)

        task_id, pid = running_tasks_id[0]
        process = self._process_manager._active_processes["test-job"][0]
        process._process.is_active = False
        process._process.returncode = 1

        await self._run_checks()
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["errored"])
        retrieved_errored_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual([task_id], retrieved_errored_task_ids)

    async def test_non_zero_approved_return_code(self):
        """Test that a none zero return code but approved returncode leads to a finished task."""
        _, running_tasks_id, _, _ = await self._generate_tasks(running_count=3)

        task_id, pid = running_tasks_id[0]
        process = self._process_manager._active_processes["test-job"][0]
        process._process.is_active = False
        process._process.returncode = 123456789

        await self._run_checks()
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["finished"])
        retrieved_finished_task_ids = [task["task_id"] for task in tasks]

        self.assertEqual([task_id], retrieved_finished_task_ids)

    async def test_timeout_does_not_apply_to_starting_tests(self):
        """Test that tasks in the starting and running state behave differently with a timeout.

        A task needs a task_function to implement the check in functionality. Only the running one should timeout.
        """
        await self._generate_tasks(starting_count=1, running_count=1, task_function="foo.bar", task_type="test-job-with-function")
        await self._run_checks()
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 1)

    async def test_evict_agent(self):
        self.assertFalse(self._manager.is_evicted)
        self._manager.process_checkin_result({"status": "evicted"})
        self.assertTrue(self._manager.is_evicted)

    async def test_enable_agent_after_eviction(self):
        self._manager._is_evicted = True
        self.assertTrue(self._manager.is_evicted)
        self._manager.process_checkin_result({"status": "idle"})
        self.assertFalse(self._manager.is_evicted)

    async def test_only_change_status_when_status_evicted(self):
        self.assertFalse(self._manager.is_evicted)
        self._manager.process_checkin_result({"status": "idle"})
        self.assertFalse(self._manager.is_evicted)

    async def test_dependants_update_status_finished(self):
        task_id = str(uuid.uuid4())
        metadata = {
            "dependants": [{
                "task_ids": [task_id],
                "task_type": "dependant-task",
                "task_function": "",
                "source_queue": "http://localhost:9090"
            }]
        }

        await self._manager._process_post_completion_tasks(metadata, "dummy_task_id", "finished", "john-doe")

        res = self._task_update_calls
        self.assertEqual(res[0]["task_id"], task_id)
        self.assertEqual(res[0]["status"], "submitted")

    async def test_dependants_update_status_errored(self):
        task_id = str(uuid.uuid4())
        metadata = {
            "dependants": [{
                "task_ids": [task_id],
                "task_type": "dependant-task",
                "task_function": "",
                "source_queue": "http://localhost:9090"
            }]
        }

        await self._manager._process_post_completion_tasks(metadata, "dummy_task_id", "errored", "john-doe")

        res = self._task_update_calls
        self.assertEqual(res[0]["task_id"], task_id)
        self.assertEqual(res[0]["status"], "cancelled")

    async def test_finished_tasks_update_dependants(self):
        """Test that finished tasks update dependants when finished"""
        task_id = str(uuid.uuid4())
        metadata = {
            "dependants": [{
                "task_ids": [task_id],
                "task_type": "dependant-task",
                "task_function": "",
                "source_queue": "http://localhost:9090"
            }]
        }

        await self._generate_tasks(finished_count=1, metadata=metadata)
        self.assertEqual(len(self._task_update_calls), 0)
        await self._run_checks()
        self.assertEqual(len(self._task_update_calls), 2)

        updated_task = None
        for task in self._task_update_calls:
            if task["task_id"] == task_id:
                updated_task = task

        self.assertEqual(updated_task["status"], "submitted")

    async def test_running_tasks_update_donot_affect_dependants(self):
        """Test that running task updates do not affect dependants"""
        task_id = str(uuid.uuid4())
        metadata = {
            "dependants": [{
                "task_ids": [task_id],
                "task_type": "dependant-task",
                "task_function": "",
                "source_queue": "http://localhost:9090"
            }]
        }

        _, running_tasks, _, _ = await self._generate_tasks(running_count=1, metadata=metadata)

        active_task_id = running_tasks[0][0]
        self.assertEqual(len(self._task_update_calls), 0)
        await self._manager._set_task_status(active_task_id, status="running", reason="Still running")
        self.assertEqual(len(self._task_update_calls), 1)

        updated_task = None
        for task in self._task_update_calls:
            if task["task_id"] == task_id:
                updated_task = task

        self.assertIsNone(updated_task)

    async def test_fetched_task_from_queue_is_in_pending(self):
        """When we fetch a task from the queue we put in a pending state while the operator hasn't looked at it"""
        _, running, _, _  = await self._generate_tasks(running_count=1)
        task_id, count = running[0]

        # Configure it so when we fetch a new task we receive the right task id.
        self.TEST_FETCH_TASK_STATUS_ID = task_id

        # Let get_capacity return a value that shows we have room to run a task.
        async def get_capacity(foo, bar, taskid_to_job_definition_map={}):
            return ("create-render", 1)
        self._manager._bay_manager.get_capacity = get_capacity

        # We no-op the set_task_status, this is called after the operator starts a process, we don't care at that point
        # for the intent of this test.
        async def set_task_status(*args, **kwargs):
            return None
        self._manager._set_task_status = set_task_status
        self._manager.set_task_errored = set_task_status

        # Once we call get_task, we receive a function with the `starting` state.
        await self._manager._get_task()

        # Ensure that it's actually on pending.
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["pending"])
        self.assertEqual(tasks[0]["task_id"], self.TEST_FETCH_TASK_STATUS_ID)

    async def test_running_tasks_update_on_errored_task_does_not_update_service(self):
        """Test that tasks on a finished are not updated back to running"""

        # Create an error task without the boiler plate for more control
        task_id = str(uuid.uuid4())
        await self._task_store.insert_existing_task(
            task_id, status="errored", task_function="", task_type="test-job", userid="foo", metadata={})
        pid = self._current_pid
        self._current_pid += 1
        active = False
        returncode = 1
        self._process_manager.create_instance_from_job(pid, is_active=active, returncode=returncode, job_type='test-job', status='errored')
        self._manager._task_process_map[('test-job', '')][task_id] = {"process_id": pid, "checkin_time": 0,}

        # Try to set it to running, verify that we're still errored.
        await self._manager._set_task_status(task_id, status="running", reason="Still running")
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["errored"])
        self.assertEqual(tasks[0]["task_id"], task_id)

        # Verify we didn't call the backend service.
        self.assertEqual(len(self._task_update_calls), 0)

    async def test_task_that_errored_on_spawn_do_not_stay_on_active_tasks(self):
        """Test that tasks that fail on start up and return an errored status do not stay in active tasks"""

        _, running, _, _ = await self._generate_tasks(running_count=1)
        task_id, count = running[0]

        # Configure it so when we fetch a new task we receive the right task id.
        self.TEST_FETCH_TASK_STATUS_ID = task_id

        # Let get_capacity return a value that shows we have room to run a task.
        async def get_capacity(foo, bar, taskid_to_job_definition_map={}):
            return ("test-job", 1)
        self._manager._bay_manager.get_capacity = get_capacity

        # Mock the launch method to return an error.
        async def launch_task(*args, **kwargs):
            return {"data": {"process_id": 999, "process_status": "errored"}}
        self._manager._launch_task = launch_task

        # Run the get_task loop
        await self._manager._get_task()

        # Ensure we have no active tasks
        res = self._manager.get_active_tasks()
        self.assertEqual(len(res), 0)

    async def test_task_process_checkin_time_timedout(self):
        """Test that a task is set to errored when checkin has expired"""
        _, running, _, _  = await self._generate_tasks(running_count=1)
        task_id, _ = running[0]

        active_process_map = {task_id: {"checkin_time": 0}}

        await self._manager._process_checkin_time(task_id, "test-job", 12345, active_process_map, status="running", task_checkin_timeout=60)
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["errored"])
        self.assertEqual(tasks[0]["task_id"], task_id)

    async def test_task_process_checkin_time_success(self):
        """Test that a task checkin does not change task status if within the timeout"""
        _, running, _, _  = await self._generate_tasks(running_count=1)
        task_id, _ = running[0]

        now = get_utc_unixtime()
        active_process_map = {task_id: {"checkin_time": now}}

        await self._manager._process_checkin_time(task_id, "test-job", 12345, active_process_map, status="running", task_checkin_timeout=60)
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])
        self.assertEqual(tasks[0]["task_id"], task_id)

    async def test_task_process_checkin_time_starting(self):
        """Test that a task in starting, remains in starting even when checkin_time is expired"""

        _, running, _, _  = await self._generate_tasks(running_count=1)
        task_id, _ = running[0]
        await self._manager._set_task_status(task_id, status="starting", reason="reset to starting")

        active_process_map = {task_id: {"checkin_time": 0}}

        await self._manager._process_checkin_time(task_id, "test-job", 12345, active_process_map, status="starting", task_checkin_timeout=60)
        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["starting"])
        self.assertEqual(tasks[0]["task_id"], task_id)

    async def test_task_not_verified_if_status_changed(self):
        """Test that a status changing does not trigger a check with upstream to see if the status has changed."""
        _, running, _, _  = await self._generate_tasks(running_count=1)
        task_id, _ = running[0]
        await self._manager._set_task_status(task_id, status="starting", reason="reset to starting")

        now = get_utc_unixtime()
        active_process_map = {task_id: {"checkin_time": now, "process_id": 12345}}

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["starting"])
        tasks_to_check = await self._manager._check_task_status(
            tasks,
            active_process_map,
            running_processes=[12345],
            errored_processes=[],
            finished_processes=[],
            active_processes=[],
            task_checkin_timeout=60
        )
        # Check that there is no tasks
        self.assertEqual(len(tasks_to_check), 0)

    async def test_task_verified_if_status_not_changed(self):
        """Test that a task is tested with upstream if the status remains the same to detect any undetected retries, crashs etc."""
        _, running, _, _  = await self._generate_tasks(running_count=1)
        task_id, _ = running[0]

        now = get_utc_unixtime()
        active_process_map = {task_id: {"checkin_time": now, "process_id": 12345}}

        tasks = await self._task_store.get_tasks(task_type="test-job", task_function="", statuses=["running"])
        tasks_to_check = await self._manager._check_task_status(
            tasks,
            active_process_map,
            running_processes=[12345],
            errored_processes=[],
            finished_processes=[],
            active_processes=[12345],
            task_checkin_timeout=60
        )
        self.assertEqual(len(tasks_to_check), 1, "Expected task search to match 1 task.")
        task_id_to_check, _ = tasks_to_check[0]
        self.assertEqual(task_id_to_check, task_id)

    async def test_task_manager_cycle(self):
        """Ensure that the TaskManager returns from the run loop when a stop is requested."""

        # attempt to stop the run loop using the method previous used
        old_behaviour = False

        print('starting first runner')
        runner1 = self._manager.run()

        print("requesting stop of first runner")
        if old_behaviour:
            self._manager.set_connected(False)
        else:
            self._manager.stop()

        print("starting second runner")
        runner2 = self._manager.run()

        print("requesting stop of second runner")
        if old_behaviour:
            self._manager.set_connected(False)
        else:
            self._manager.stop()

        print("about to await from the run loops after requesting a stop")
        await runner1
        await runner2
        print("returned from await successfully")

        self.assertTrue(True)
