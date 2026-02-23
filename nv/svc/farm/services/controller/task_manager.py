# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Task Manager."""

import asyncio
import collections
import datetime
import logging
import os
import socket
from typing import Dict, List, Optional, Tuple, Any
import urllib.parse

from nv.svc.core.exceptions import ServicesBaseException

from nv.svc.farm.services.controller.config import FarmControllerConfig
from nv.svc.farm.services.controller.facilities import bays
from nv.svc.farm.services.jobs.facilities.manager.base import ProcessManager
from nv.svc.farm.services.jobs.facilities.manager.nvct import NVCTProcessManager
from nv.svc.farm.services.jobs.facilities.manager.nvcf import NVCFProcessManager
from nv.svc.farm.services.tasks.facilities.tasks import store
from nv.svc.farm.services.tasks.utils import status_utils
from nv.svc.farm.utils import fetch_data, post_data


def get_utc_unixtime() -> float:
    """Return the current time as a unix epoch timestamp in the UTC timezone."""
    return datetime.datetime.now(datetime.timezone.utc).timestamp()


def _to_url_params(data: Dict):
    """Convert dict to url params."""
    params = []
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                params.append((key, item))
        else:
            params.append((key, value))
    return urllib.parse.urlencode(params, doseq=True)


def _strip_path_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    stripped_url = urllib.parse.urlunparse(
        (parsed_url.scheme, parsed_url.netloc, "", "", "", "")
    )
    return stripped_url


class TaskManager:
    """Agent Task Manager for the Controller."""

    def __init__(
        self,
        task_store: store.TaskStore,
        bay_controller: bays.BaseBays,
        config: FarmControllerConfig,
        process_manager: ProcessManager,
        agent_id: Optional[str] = None,
    ) -> None:
        """
        Task Manager constructor.

        Args:
            task_store (store.TaskStore): Interface to the persistence layer to use to store task information.
            bay_controller (bays.BaseBays): Bay controller.
            config (FarmControllerConfig): The controller config.
            agent_id (str): Unique identifier of the Agent operating the tasks.
        """
        self._should_stop = asyncio.Event()
        self._is_connected = False
        self._is_evicted = False
        self._task_process_map = collections.defaultdict(dict)
        self._taskid_to_job_definition_map: Dict[int, str] = {}

        self._task_store = task_store
        self._bay_manager = bay_controller
        self._process_manager = process_manager

        self._agent_id = agent_id or f"{socket.getfqdn()}-{os.getpid()}"

        self._service_host_url_format_str = (
            config.controller.service_host_url_format_str
        )

        self._agents_service_url = config.controller.agents_service_url.rstrip("/")
        self._tasks_service_url = config.controller.tasks_service_url.rstrip("/")

        self._labels = config.controller.labels.to_list()
        self._public_to_private_source_queue_hostnames = (
            config.controller.public_to_private_source_queue_hostnames.to_list()
        )
        self._agent_checkin_interval = config.controller.agent_checkin_interval
        self._reconcile_task_state = config.controller.reconcile_task_state
        self._task_reconcile_interval = config.controller.task_reconcile_interval
        self._task_checkin_interval = config.controller.task_checkin_interval
        self._task_checkin_timeout = config.controller.task_checkin_timeout
        self._fetch_task_idle_delay = config.controller.fetch_task_idle_delay
        self._fetch_task_delay = config.controller.fetch_task_delay
        self._is_nvct = isinstance(self._process_manager, NVCTProcessManager)
        self._is_nvcf = isinstance(self._process_manager, NVCFProcessManager)

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def is_evicted(self):
        return self._is_evicted

    def set_connected(self, value: bool):
        self._is_connected = value

    async def list_available_job_types(self):
        """Retrieve available jobs types that this operator knows how to process."""
        available = []
        for task_type, task_function in self._process_manager.available_process_keys:
            available.append({"task_type": task_type, "task_function": task_function})
        return available

    async def get_job_type_definitions(self) -> List[Dict]:
        """Retrieve the job definitions for available job types that this operator knows how to process as a dict."""
        job_definitions = self._process_manager.available_job_specs
        return [job_def.to_dict() for job_def in job_definitions]

    async def list_active_processes(self):
        active = self._process_manager.active_processes
        result = {}
        for proc_type, procs in active.items():
            result[proc_type] = [process.process_id for process in procs]
        return result

    async def list_running_processes(self):
        running = self._process_manager.active_processes
        result = {}
        for proc_type, procs in running.items():
            result[proc_type] = [
                process.process_id for process in procs if process.is_running
            ]
        return result

    async def list_finished_processes(self):
        finished = self._process_manager.finished_processes
        result = {}
        for proc_type, procs in finished.items():
            result[proc_type] = [process.process_id for process in procs]
        return result

    async def list_errored_processes(self):
        """List process IDs of errored processes."""
        errored = self._process_manager.errored_processes
        result = {}
        for proc_type, procs in errored.items():
            result[proc_type] = [process.process_id for process in procs]
        return result

    async def interrupt_running_process(self, process_id: str, process_type: str):
        """Interrupt a given process."""
        try:
            # Ensure that on interruption we force terminate the process rather than shutting down gracefully.
            # TODO: see if this is too much of a sledgehammer at which point
            #   this will need to have a terminate followed by a kill if the process did not shutdown.
            exit_code = await self._process_manager.stop_process_async(
                process_type, process_id, kill=True
            )
            return {
                "process_id": process_id,
                "process_type": process_type,
                "exit_code": exit_code,
            }
        except KeyError:
            raise ServicesBaseException(
                status_code=404, detail=f"Process of type {process_type} not found."
            )
        except Exception as exc:
            raise ServicesBaseException(
                status_code=500,
                detail=f"Error shutting down process: {process_type}-{process_id}: {str(exc)}",
            )

    def get_agent_status(self):
        """Get the agent status."""
        active_tasks = self.get_active_tasks()
        return {
            "agent_id": self._agent_id,
            "is_connected": self.is_connected,
            "active_tasks": active_tasks,
        }

    def get_labels(self) -> List[str]:
        """Return list of active labels."""
        return self._labels

    def get_active_tasks(self) -> List:
        """Return the list of active tasks."""
        tasks = []
        for task in self._task_process_map.values():
            tasks.extend(task.keys())
        return tasks

    async def _agent_checkin(self) -> None:
        """Checkin loop allowing the agent to ping the Agents service to notify it is still alive."""
        await asyncio.sleep(self._agent_checkin_interval)
        while True:
            try:
                active_tasks = self.get_active_tasks()
                labels = self.get_labels()
                task_types = await self.get_task_types()

                data = dict(
                    agent_id=self._agent_id,
                    active_tasks=active_tasks,
                    labels=labels,
                    task_types=task_types,
                )
                result = await post_data(f"{self._agents_service_url}/checkin", data)
                self.set_connected(True)
                if result:
                    self.process_checkin_result(result)
            except Exception as exc:
                logging.error(
                    f"Unable to perform agent checkin with the Farm queue {str(type(exc))}: {str(exc)}"
                )
                self.set_connected(False)

            await asyncio.sleep(self._agent_checkin_interval)

    async def agent_checkin(self) -> None:
        """Checkin loop allowing the agent to ping the Agents service to notify it is still alive."""
        try:
            await self._agent_checkin()
        except asyncio.exceptions.CancelledError:
            logging.debug("TaskManager.agent_checkin coroutine has been cancelled.")

    async def unregister_agent(self):
        """Unregister the current agent from the pool."""
        active_tasks = self.get_active_tasks()
        data = {
            "agent_id": self._agent_id,
            "active_tasks": active_tasks,
        }
        await post_data(f"{self._agents_service_url}/remove", data)
        logging.info(f"Unregisted agent {self._agent_id}")

    async def reconcile(self) -> None:
        if not self._reconcile_task_state:
            return

        logging.info("Task state reconciling is enabled.")
        try:
            while not self._should_stop.is_set():
                await self._reconcile()
                await asyncio.sleep(self._task_reconcile_interval)
        except asyncio.exceptions.CancelledError:
            logging.debug("TaskManager.reconcile coroutine has been cancelled.")

    async def get_task_types(self) -> List[Tuple[str, str]]:
        """Retrieve list of available definitions with tuples of ("task_type", "task_function")."""
        task_types = await self.list_available_job_types()
        return [
            (task_type["task_type"], task_type["task_function"])
            for task_type in task_types
        ]

    async def _reconcile(self) -> bool:
        """
        Reconcile tasks on startup.

        Indicates whether the reconciliation successfully completed, which means all tasks currently reported
        as running in dashboard have an associated job in kubernetes and controller is able to track the progress.

        Returns:
            bool: True if the reconciliation successfully completed, False otherwise.
        """
        task_types = await self.get_task_types()

        active_tasks = {}
        for task_type, task_function in task_types:
            try:
                params = dict(
                    task_type=task_type,
                    task_function=task_function,
                    status=["running", "starting"],
                )
                url_params = _to_url_params(params)
                active_tasks = await fetch_data(
                    f"{self._tasks_service_url}/list?{url_params}"
                )
            except Exception as exc:
                logging.error(
                    f"Problem fetching tasks to execute from the remote Tasks service: {str(type(exc))}: {str(exc)}"
                )
                return False

            for tasks in active_tasks.values():
                for data in tasks:
                    task_id = data["task_id"]
                    task_type = data["task_type"]
                    task_args = data["task_args"]
                    task_function = data["task_function"]
                    task_metadata = data["metadata"]

                    # If we're already executing a process id within that task, interrupt the task.
                    if self._task_process_map[(task_type, task_function)].get(task_id):
                        logging.debug(
                            f"No need to reconcile the task {task_id} (status: {data['status']})"
                        )
                        continue
                    else:
                        logging.info(f"Reconciling the task {task_id}")

                    # insert into our task store in controller
                    try:
                        args = {}
                        args["task_id"] = data["task_id"]
                        args["status"] = data["status"]
                        args["task_type"] = data["task_type"]
                        args["userid"] = data["userid"]
                        args["task_args"] = data["task_args"]
                        args["task_function"] = data["task_function"]
                        args["task_function_args"] = data["task_function_args"]
                        args["task_requirements"] = data["task_requirements"]
                        args["task_comment"] = data["task_comment"]
                        args["task_submission_time"] = data["task_submission_time"]
                        args["priority"] = data["priority"]
                        args["metadata"] = data["metadata"]
                        args["labels"] = data["labels"]
                        await self._task_store.insert_existing_task(**args)
                    except Exception as exc:
                        logging.error(
                            f"Problem inserting {task_id} into local task store {str(exc)}"
                        )
                        return False

                    if task_function:
                        task_args["task_id"] = task_id
                        task_args["task_log_file"] = (
                            "${logs}/" + f"{task_type}_{task_function}_{task_id}_" + "${start_timestamp}.log"
                        )

                    try:
                        task_payload = {
                            "jsonapi": {"version": "1.0"},
                            "data": {
                                "allowed_args": task_args,
                                "metadata": task_metadata,
                            },
                        }
                        # When using NVCT or NVCF, the task id may be the NVCT/NVCF task id, otherwise use the Farm task id.
                        # use the selected_task_id to retrieve the task which will create an instance using the correct pid on the process manager.
                        selected_task_id = task_metadata.get(
                            "nvct_task_id"
                        ) or task_metadata.get("nvcf_function_id")
                        if not selected_task_id and (self._is_nvct or self._is_nvcf):
                            selected_task_id = task_id
                            process_manager_name = "NVCT" if self._is_nvct else "NVCF"
                            logging.warning(
                                f"No {process_manager_name} Task ID found for {task_id}, using the Farm Task ID to create reconciled instance."
                            )
                        launch_task_response = await self._retrieve_task(
                            selected_task_id, task_type, task_payload
                        )

                        process_id = launch_task_response["data"]["process_id"]
                        process_status = launch_task_response["data"]["process_status"]

                        logging.info(
                            f"Reconciled {task_id} with {process_id} with status {process_status}"
                        )
                        time_now = get_utc_unixtime()
                        self._task_process_map[(task_type, task_function)][task_id] = {
                            "process_id": process_id,
                            "checkin_time": time_now,
                            "created_time": time_now,
                        }
                    except Exception as exc:
                        await self.set_task_errored(task_id, str(exc))
                    else:
                        await self._set_task_status(
                            task_id, process_status, "agent is reconciling task"
                        )
        return True

    async def _run(self) -> None:
        """Execute the next task the agent is able to perform."""
        labels_str = ",".join(self._labels)
        logging.info(
            f"Starting Controller TaskManager agent_id: {self._agent_id}, labels: {labels_str}"
        )
        while not self._should_stop.is_set():
            task_submitted = False
            sleep_duration = self._fetch_task_idle_delay

            try:
                if not self.is_evicted:
                    task_submitted = await self._get_task()
            except Exception as exc:
                logging.error(str(exc))

            if task_submitted:
                sleep_duration = self._fetch_task_delay

            await asyncio.sleep(sleep_duration)

        logging.info("Stopping TaskManager run loop")

    async def run(self) -> None:
        try:
            await self._run()
        except asyncio.exceptions.CancelledError:
            logging.debug("TaskManager.run coroutine has been cancelled.")

    def _get_processid_for_task(self, task_id: str) -> Optional[str]:
        """
        Return the process ID of the given task.

        Args:
            task_id (str): Unique identifier of the task for which to return the process ID.

        Returns:
            str: The process ID of the given task.

        """
        for tasks in self._task_process_map.values():
            if task_id in tasks:
                return tasks[task_id]["process_id"]

    async def do_checkin(self, task_id: str) -> None:
        """
        Record the time of the checkin for the given task.

        Args:
            task_id (str): Unique identifier of the task for which to record the checkin.

        Returns:
            None

        """
        for tasks in self._task_process_map.values():
            if task_id in tasks:
                tasks[task_id]["checkin_time"] = get_utc_unixtime()
                break

    async def _run_checks(self) -> None:
        """Execute task status checks."""
        while not self._should_stop.is_set():
            try:
                await self._check_tasks()
            except Exception as exc:
                logging.error(f"Error running task checks: {str(exc)}")

            await asyncio.sleep(self._task_checkin_interval)

    async def run_checks(self) -> None:
        try:
            await self._run_checks()
        except asyncio.exceptions.CancelledError:
            logging.debug("TaskManager.run_checks coroutine has been cancelled.")

    async def _check_tasks(self) -> None:
        """Perform a status check for the active tasks."""
        task_types = await self.get_task_types()

        active_processes = await self.list_active_processes()
        running_processes = await self.list_running_processes()
        finished_processes = await self.list_finished_processes()
        errored_processes = await self.list_errored_processes()

        for task_type, task_function in task_types:
            await self._check_active_tasks_status(
                task_type=task_type,
                task_function=task_function,
                active_processes=active_processes.get(task_type, []),
                running_processes=running_processes.get(task_type, []),
                active_process_map=self._task_process_map[(task_type, task_function)],
                task_checkin_timeout=self._task_checkin_timeout,
                finished_processes=finished_processes.get(task_type, []),
                errored_processes=errored_processes.get(task_type, []),
            )

    async def _check_active_tasks_status(
        self,
        task_type: str,
        task_function: str,
        active_processes: List,
        running_processes: List,
        active_process_map: Dict,
        task_checkin_timeout: int,
        finished_processes: List,
        errored_processes: List,
    ) -> None:
        """
        Check the status of the tasks matching the given search criterias.

        Reconciles their database status with their process status.

        Args:
            task_type (str): Type of the task to search for.
            task_function (str): Function of the task to search for.
            active_processes (List): List of active processes.
            running_processes (List): List of running processes.
            active_process_map (Dict): Mapping of tasks and their associated process ID.
            task_checkin_timeout (int): Duration before which to report a timeout.
            finished_processes (List): List of finished processes.
            errored_processes (List): List of errored processes.
        """
        futures_checking_with_remote = []

        statuses_to_check = ["starting", "running"]
        tasks = await self._task_store.get_tasks(
            task_type=task_type,
            task_function=task_function,
            statuses=statuses_to_check,
        )
        tasks_to_check = await self._check_task_status(
            tasks,
            active_process_map,
            running_processes,
            errored_processes,
            finished_processes,
            active_processes,
            task_checkin_timeout,
        )
        for task_to_check in tasks_to_check:
            task_id, process_created_time = task_to_check
            futures_checking_with_remote.append(
                asyncio.ensure_future(
                    self._check_status_with_remote(task_id, process_created_time)
                )
            )

        try:
            await asyncio.wait_for(
                asyncio.gather(*futures_checking_with_remote, return_exceptions=True),
                timeout=10,
            )
        except asyncio.TimeoutError:
            logging.warning("Failed to collect status for all tasks. Timed out.")

    async def _check_task_status(
        self,
        tasks: List[Dict],
        active_process_map: Dict,
        running_processes: List,
        errored_processes: List,
        finished_processes: List,
        active_processes: List,
        task_checkin_timeout: int,
    ) -> List:
        """
        Check status of tasks.

        Args:
            tasks (List[dict]): List of tasks to check
            active_process_map (Dict):
            running_processes (List):
            errored_processes (List):
            finished_processes (List):
            active_processes (List):
            task_checkin_timeout (int):
        """
        tasks_to_check_with_remote = []

        task_ids = [task["task_id"] for task in tasks]
        if task_ids:
            logging.info(f"Checking status of tasks {' '.join(task_ids)}")

        for task in tasks:
            task_id = task["task_id"]
            task_type = task["task_type"]
            task_function = task.get("task_function", None)
            status = task["status"]
            status_has_changed = False

            try:
                # TODO: is there a potential of the active_process_map not being up to date, causing tasks to be flagged as crashed.
                process = active_process_map[task_id]
                process_id = process.get("process_id", None)
                process_created_time = process.get("created_time", None)
            except KeyError:
                message = (
                    f"Unable to retrieve task id {task_id}. Process likely crashed"
                )
                await self.set_task_errored(task_id=task_id, reason=message)
                continue

            try:
                if process_id in running_processes and status == "starting":
                    await self._set_task_status(task_id, "running", "running")
                    status_has_changed = True
                elif process_id in errored_processes:
                    await self.set_task_errored(
                        task_id=task_id,
                        reason="Process finished without a successful exit code.",
                    )
                    status_has_changed = True
                elif process_id in finished_processes:
                    await self.set_task_finished(task_id=task_id)
                    status_has_changed = True
                elif process_id not in active_processes:
                    await self.set_task_errored(
                        task_id=task_id, reason="Process likely crashed"
                    )
                    status_has_changed = True

                # Simple processes currently can't do a checkin so don't verify they checked in
                if task_function:
                    await self._process_checkin_time(
                        task_id,
                        task_type,
                        process_id,
                        active_process_map,
                        status,
                        task_checkin_timeout,
                    )
            except Exception:
                logging.exception(f"Unable to update the task status for {task_id}.")
                continue

            if not status_has_changed:
                tasks_to_check_with_remote.append([task_id, process_created_time])

        return tasks_to_check_with_remote

    async def _process_checkin_time(
        self,
        task_id: str,
        task_type: str,
        process_id: int,
        active_process_map: Dict,
        status: str,
        task_checkin_timeout: int,
    ) -> None:
        time_now = get_utc_unixtime()

        if status == "starting":
            # We reset the check in time for processes that are still in the starting stage.
            active_process_map[task_id]["checkin_time"] = time_now

        if status == "running" and task_checkin_timeout > 0:
            last_checkin = active_process_map[task_id]["checkin_time"]
            if last_checkin + task_checkin_timeout < time_now:
                await self.set_task_errored(
                    task_id=task_id, reason="Process has timed out."
                )
                await self.interrupt_running_process(
                    process_id=str(process_id), process_type=task_type
                )

    async def _check_status_with_remote(
        self, task_id: str, process_created_time: float
    ) -> None:
        """
        Check task status with remote task service to trigger actions from the queue.

        Args:
            task_id (str): Task ID of the task
            process_created_time (float): Since epoch time
        """
        try:
            task_data = await fetch_data(f"{self._tasks_service_url}/info/{task_id}")
            task_status = task_data["status"]

            if task_status in ["cancelled", "cancelling"]:
                logging.warning(f"Task {task_id} is in {task_status}, interrupting it.")
                await self._interrupt_task(task_id)
                return

            if task_status in ["submitted"]:
                logging.warning(f"Task {task_id} is in {task_status}, interrupting it.")
                await self._interrupt_task(
                    task_id, "task got retried", skip_task_service_update=True
                )
                return

            # We check the revision history to see if the task hasn't already started running in another agent.
            # The task might be in a running state, but, because it got requeued and picked up by other agent before we saw it.
            # TODO: Create JIRA -- revision history could use a filter on agent-id and time, e.g: query only revisions
            # NOT from me AND after launch time of the task. For now do it in python.
            # Ensure it's all UTC in both agent and server side... otherwise this can get problematic.
            revisions = await fetch_data(
                f"{self._tasks_service_url}/revision-history/{task_id}"
            )

            for revision in revisions:
                agent_id = revision["agent_id"]
                if agent_id == self._agent_id:
                    continue

                revision_time = revision["time"]
                if revision_time < process_created_time:
                    continue

                logging.warning(
                    f"Task {task_id} is being interrupted because another agent"
                    f" has changed its status after we've created it: {str(revision)}"
                )

                await self._interrupt_task(
                    task_id,
                    "task running in another agent",
                    skip_task_service_update=True,
                )

        except Exception as exc:
            logging.error(
                f"Failed to process remote state: {str(type(exc))}, {str(exc)}"
            )

    async def _get_task(self) -> bool:
        """Select and schedule a task for execution.

        Returns:
            bool: True if a task was scheduled for execution, False otherwise.
        """

        job_definitions: List[Dict[str, Any]] = await self.get_job_type_definitions()
        task_types = await self.get_task_types()

        active_tasks = {}
        for task_type, task_function in task_types:
            active_tasks[(task_type, task_function)] = await self._task_store.get_tasks(
                task_type=task_type,
                task_function=task_function,
                statuses=["running", "starting"],
            )

        possible_tasks, capacity = await self._bay_manager.get_capacity(
            active_tasks,
            job_definitions,
            taskid_to_job_definition_map=self._taskid_to_job_definition_map,
        )
        if not possible_tasks:
            return False

        try:
            data_to_post = dict(
                task_types=possible_tasks,
                capacity=capacity,
                agent_id=self._agent_id,
                labels=self._labels,
            )
            data = await post_data(f"{self._tasks_service_url}/fetch", data_to_post)
        except Exception as exc:
            logging.error(
                f"Problem fetching tasks to execute from the remote Tasks service: {str(type(exc))}: {str(exc)}"
            )
            data = None

        if not data:
            # NOTE: catch empty or None.
            return False

        task_id = data["task_id"]
        task_type = data["task_type"]
        task_args = data["task_args"]
        task_function = data["task_function"]
        task_metadata = data["metadata"]
        task_requirements = data["task_requirements"]

        # populate the task_id -> job name (task_type) map
        # this will be cleaned up when we notice the transition to a finished state
        self._taskid_to_job_definition_map[task_id] = task_type

        # We override the status as pending to avoid we thinking that the operator
        # already has a task with the status Starting, which happens down the line.
        data["status"] = "pending"

        try:
            await self._task_store.insert_existing_task(**data)
        except Exception as exc:
            logging.error(f"Problem inserting task into local task store {str(exc)}")
            return False

        if task_function:
            task_args["task_id"] = task_id
            task_args["task_log_file"] = (
                "${logs}/" + f"{task_type}_{task_function}_{task_id}_" + "${start_timestamp}.log"
            )

        try:
            task_payload = {
                "jsonapi": {"version": "1.0"},
                "data": {
                    "allowed_args": task_args,
                    "metadata": task_metadata,
                    "task_requirements": task_requirements,
                },
            }
            launch_task_response = await self._launch_task(
                task_id, task_type, task_payload
            )

            process_id = launch_task_response["data"]["process_id"]
            process_status = launch_task_response["data"]["process_status"]
            if process_status == "errored":
                raise Exception(f"Process id {process_id} failed to start")

            # If we're already executing a process id within that task, interrupt the task.
            if self._task_process_map[(task_type, task_function)].get(task_id):
                await self._interrupt_task(
                    task_id, "task got retried", skip_task_service_update=True
                )

            time_now = get_utc_unixtime()
            self._task_process_map[(task_type, task_function)][task_id] = {
                "process_id": process_id,
                "checkin_time": time_now,
                "created_time": time_now,
            }
        except Exception as exc:
            await self.set_task_errored(task_id, str(exc))
        else:
            await self._set_task_status(task_id, process_status, "agent")

        return True

    async def _launch_task(self, task_id: str, task_type: str, data: Dict) -> Dict:
        """
        Launch a task of the given type.

        Args:
            task_id (str): Task Id for the task to launch.
            task_type (str): Type of the task to launch.
            data (dict): Payload to launch a task.

        Returns:
            dict containing the process_id and process_status

        """
        response = await self._process_manager.spawn(
            job_name=task_type, payload=data, task_id=task_id
        )
        result = response.model_dump()
        if self._is_nvct or self._is_nvcf:
            # NOTE: this is a hack to keep track of the NVCT/NVCF Task ID, useful for reconsiling task upon controller startup.
            process_manager_task_id = result["data"]["process_id"]
            task = await fetch_data(f"{self._tasks_service_url}/info/{task_id}")
            metadata = task["metadata"] or {}
            if self._is_nvct:
                metadata["nvct_task_id"] = process_manager_task_id
            elif self._is_nvcf:
                metadata["nvcf_function_id"] = process_manager_task_id
            task["metadata"] = metadata
            await post_data(f"{self._tasks_service_url}/update", task)

        return result

    async def _retrieve_task(self, task_id: str, task_type: str, data: Dict) -> Dict:
        """
        Retrieve a task of the given type.

        Args:
            task_id (str): Task Id for the task to launch.
            task_type (str): Type of the task to launch.
            data (dict): Payload to launch a task.

        Returns:
            dict containing the process_id and process_status

        """
        result = await self._process_manager.retrieve(
            job_name=task_type, payload=data, task_id=task_id
        )
        return result.model_dump()

    def stop(self) -> None:
        """Record that the agent should stop its operation."""
        self._should_stop.set()
        self._is_connected = False

    async def get_task(self, task_id: str):
        """
        Return metadata information about the given task.

        Args:
            task_id (str): Unique identifier of the task to return.

        Returns:
            Any: Metadata information about the given task.

        """
        return await self._task_store.get_task(task_id=task_id)

    async def set_task_started(self, task_id: str):
        """
        Record that the given task has started its process.

        Args:
            task_id (str): Unique identifier of the task whose process has started.

        Returns:
            Any: Information about the response to the task's update notification.

        """
        return await self._set_task_status(
            task_id, "starting", "starting", pop_from_process_map=False
        )

    async def set_task_finished(self, task_id: str):
        """
        Record that the given task has finished its process.

        Args:
            task_id (str): Unique identifier of the task whose process has completed.

        Returns:
            Any: Information about the response to the task's update notification.

        """
        return await self._set_task_status(
            task_id, "finished", "finished", pop_from_process_map=True
        )

    async def set_task_errored(self, task_id: str, reason: str):
        """
        Record that the given task has encountered an error.

        Args:
            task_id (str): Unique identifier of the task whose process has encountered an error.
            reason (str): Error message.

        Returns:
            Any: Information about the response to the task's update notification.

        """
        return await self._set_task_status(
            task_id, "errored", reason, pop_from_process_map=True
        )

    async def task_checkin(
        self,
        task_id: str,
        status: str,
        reason: str,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
    ) -> None:
        """
        Perform a checkin for the given task.

        Args:
            task_id (str): Unique identifier of the task for which to perform a checkin.
            status (str): Status of the task to report.
            reason (str): Potential reason for task errors.
            metrics (Optional[str]): Task metrics to report.
            progress (Optional[Dict]): Task progress to report.

        Returns:
            None

        """
        await self.do_checkin(task_id)
        result = await self._set_task_status(
            task_id=task_id,
            status=status,
            reason=reason,
            metrics=metrics,
            progress=progress,
        )

        try:
            if result.get("should_cancel"):
                logging.info(f"Received cancel command for {task_id}")
                await self._interrupt_task(task_id)
        except Exception as exc:
            logging.error(f"Failed to cancel process for task {task_id}: {exc}")

    async def _interrupt_task(
        self,
        task_id: str,
        status_message: str = "",
        skip_task_service_update: bool = False,
    ) -> None:
        """
        Interrupt the given task.

        Args:
            task_id (str): Unique identifier of the task to interrupt.
            status_message (str): The status message to update when interrupting the task.
            skip_task_service_update (bool): If true we don't update the status in the task service to canceled.

        Returns:
            None

        """
        status_message = status_message or "Interrupted by user"
        task = await self._task_store.get_task(task_id=task_id)
        task_type = task["task_type"]
        task_function = task["task_function"]

        process_id = self._get_processid_for_task(task_id)

        if process_id:
            self._task_process_map[(task_type, task_function)].pop(task_id)
            await self.interrupt_running_process(
                process_id=process_id, process_type=task_type
            )
        else:
            logging.warning(
                f"No process to interupt for {task_id}. Marking task as cancelled."
            )

        await self._set_task_status(
            task_id,
            "cancelled",
            status_message,
            pop_from_process_map=True,
            skip_task_service_update=skip_task_service_update,
        )
        logging.info(f"Task {task_id} has been successfully cancelled.")

    async def _set_task_status(
        self,
        task_id: str,
        status: str,
        reason: str,
        pop_from_process_map: bool = False,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        skip_task_service_update: bool = False,
    ):
        """
        Set the status of the given task.

        Args:
            task_id (str): Unique identifier of the task for which to set the status.
            status (str): New status to set to the task.
            reason (str): Potential reason for task errors.
            metrics (Optional[str]): Task metrics to report.
            progress (Optional[Dict]): Task progress to report.
            skip_task_service_update (bool): If true we don't update the status in the task service of the status change.

        Returns:
            Any: Information about the response to the task's update notification.

        """
        logging.info(
            f"Transitioning status of task {task_id} to {status} because {reason}"
        )

        task = await self._task_store.get_task(task_id=task_id)
        task_type = task["task_type"]
        task_function = task["task_function"]
        progress = progress or task["progress"]

        if status in ["cancelled", "errored", "finished"]:
            try:
                # clean up the taskid -> job_definition mapping dict so we don't leak memory.
                # but don't throw errors if things aren't initialized or not passed in properly.
                # it's best effort here.
                try:
                    del self._taskid_to_job_definition_map[int(task_id)]
                except (KeyError, TypeError, ValueError):
                    pass
                await self._process_post_completion_tasks(
                    task.get("metadata", {}), task_id, status, task["userid"]
                )
            except Exception as exc:
                logging.error(
                    f"Failed to process post completion tasks. {str(type(exc))}: {str(exc)}"
                )

        update_service_task_status = True
        result = {}
        try:
            await self._task_store.update_status(
                task_id=task_id,
                task_type=task_type,
                task_function=task_function,
                status=status,
                userid=task["userid"],
                details=reason,
                progress=progress,
            )
        except status_utils.StatusTransitionException as e:
            logging.warning(
                f"Not updating service status of the task {task_id}: {str(e)}"
            )
            update_service_task_status = False

        if not skip_task_service_update and update_service_task_status:
            try:
                data = dict(
                    task_id=task_id,
                    task_type=task_type,
                    task_function=task_function,
                    status=status,
                    agent_id=self._agent_id,
                    comment=reason,
                    metrics=metrics or "",
                    progress=progress,
                    userid=task["userid"],
                )
                await post_data(f"{self._tasks_service_url}/update", data)
            except Exception as exc:
                logging.error(
                    f"Issue updating task {task_id} in the remote Tasks service: {str(type(exc))}: {str(exc)}"
                )

        try:
            if pop_from_process_map:
                try:
                    self._task_process_map[(task_type, task_function)].pop(task_id)
                except KeyError:
                    # Cancelled tasks get pop'd before.
                    if status != "cancelled":
                        raise
            else:
                self._task_process_map[(task_type, task_function)][task_id][
                    "checkin_time"
                ] = get_utc_unixtime()
        except KeyError as exc:
            error_message = f"Failed to update task process map: {exc}"
            if reason:
                error_message += f"\n{reason}"
            logging.error(error_message)

        return result

    async def _process_post_completion_tasks(
        self, metadata: Dict, parent_task_id: str, parent_task_status: str, user_id: str
    ) -> None:
        logging.info(f"Processing post completion tasks for {parent_task_id}")
        await self._process_dependants(
            metadata, parent_task_id, parent_task_status, user_id
        )

    async def _process_dependants(
        self, metadata: Dict, parent_task_id: str, parent_task_status: str, user_id: str
    ) -> None:
        dependants: Optional[List[Dict]] = metadata.get("dependants")
        if not dependants:
            logging.info(f"No task dependants found for {parent_task_id}")
            return

        reason = f"{parent_task_id} completed succesfully. Processing child task."
        status = "submitted"
        if parent_task_status in ["cancelled", "errored"]:
            status = "cancelled"
            reason = f"parent task {parent_task_id} exited with the status: {parent_task_status}. Cancelling task."

        for dependant in dependants:
            source_queue_url = self._get_source_queue_url(dependant["source_queue"])
            task_type = dependant["task_type"]
            task_function = dependant["task_function"]
            for task_id in dependant["task_ids"]:
                data = dict(
                    task_id=task_id,
                    task_type=task_type,
                    task_function=task_function,
                    status=status,
                    comment=reason,
                    agent_id=self._agent_id,
                    userid=user_id,
                )
                await post_data(f"{source_queue_url}/tasks/update", data)

    def _get_source_queue_url(self, source_queue) -> str:
        if source_queue in self._public_to_private_source_queue_hostnames:
            # get the private hostname
            source_queue = self._public_to_private_source_queue_hostnames[source_queue]
        url = self._service_host_url_format_str.format(service_host=source_queue)
        logging.info(f"Retrieving url for source_queue {source_queue}. '{url}'")
        return url

    def process_checkin_result(self, checkin_result: Dict) -> None:
        status = checkin_result.get("status", "")
        is_currently_evicted = self._is_evicted

        self._is_evicted = True if status == "evicted" else False

        if is_currently_evicted and status != "evicted":
            logging.info(
                "Agent has been re-enabled after eviction and will start processing tasks"
            )
        elif not is_currently_evicted and status == "evicted":
            logging.info("Agent has been evicted and will not process new tasks")
