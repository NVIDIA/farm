# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Manager Facilities."""

__all__ = ["ProcessManager"]

import asyncio
import collections
import copy
import logging
import os
import platform
import socket
import subprocess
import sys
import threading
import secrets

from asyncio.streams import StreamReader
from functools import cache
from typing import Any, Callable, Dict, List, DefaultDict, Optional, Union, Tuple

import psutil

from nv.svc.core.facilities.base import Facility

from nv.svc.farm.services.jobs.config import FarmJobsConfig
from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore
from nv.svc.farm.services.jobs.job_types.base import BaseJob
from nv.svc.farm.services.jobs.job_types import get_job_type
from nv.svc.farm.services.jobs.definitions import (
    InstancePayload,
    ProcessCreationPayload,
    SpawnResponseModel,
    JobDefinition
)
from nv.svc.farm.utils import post_data


class BaseRemoteProcess:
    """This defines a remote process running in another system instead of the default subprocess approach."""

    def __init__(self, process_id: str, data: Optional[Dict] = None, status: str = "starting"):
        self._data = data or {}
        self._process_id = process_id
        self._returncode = None
        self._status = status
        self._latest_log_hash = None

    async def communicate(self) -> Tuple:
        # TODO: something more intelligent.
        while self._returncode is None:
            await asyncio.sleep(10)

        return None, None

    @property
    def pid(self):
        return self._process_id

    @property
    def stderr(self):
        return ""

    @property
    def stdout(self):
        return ""

    @property
    def returncode(self) -> Union[str, int]:
        return self._returncode

    def set_returncode(self, returncode: Union[str, int]):
        self._returncode = returncode

    @property
    def latest_log_hash(self) -> int:
        return self._latest_log_hash

    def set_latest_log_hash(self, hash: int):
        self._latest_log_hash = hash

    @property
    def status(self):
        return self._status

    def set_status(self, status: str):
        self._status = status


# We need to cache the config because it takes ~0.7s to load and the BaseInstance init is called
# every time we spawn a process.
@cache
def load_config():
    return FarmJobsConfig(auto_configure_logging=False).jobs


class BaseInstance:

    def __init__(
        self,
        command: str,
        container: str,
        args: List[str],
        env: Dict[str, Any] = None,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        subprocess_kwargs=None,
        on_stdout_message: Callable[[str], None] = None,
        on_stderr_message: Callable[[str], None] = None,
        success_return_codes: List[str] = None,
        working_directory: str = None,
        task_id: str = None,
    ):
        self._command = command
        self._working_directory = working_directory
        self._args = args
        self._env = env or {}
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._subprocess_kwargs = subprocess_kwargs or {}
        self._success_return_codes = success_return_codes or [0]
        self._task_id = task_id
        self._container_image = container

        self._process = None
        self._active_thread = None
        self._stop = None

        self._std_output: List[str] = []
        self._log_read_lock = threading.Lock()
        self._on_stdout_message = self._received_std_out_message
        self._on_stderr_message = self._received_std_err_message
        self._settings = load_config()

    def _received_std_out_message(self, line: str):
        self._std_output.append(line)

    def _received_std_err_message(self, line: str):
        self._std_output.append(line)

    def spawn(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        self._stop = threading.Event()
        self._process = subprocess.Popen(
            [self._command, *self._args],
            env=self._env,
            stdin=self._stdin,
            stdout=self._stdout,
            stderr=self._stderr,
            cwd=self._working_directory,
            **self._subprocess_kwargs,
        )
        self._active_thread = threading.Thread(target=self._communicate)
        self._active_thread.start()

    async def spawn_async(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        # since we allow configuration of the environment variables via capacity_requirements.env
        # we need to merge it with the job definition environment variables
        requirements = requirements or {}
        capacity_env_list = requirements.get("env", [])
        env = {item["name"]: item["value"] for item in capacity_env_list}
        env.update(self._env)

        self._stop = asyncio.Event()
        self._process = await asyncio.create_subprocess_exec(
            self._command,
            *self._args,
            env=env,
            stdin=self._stdin,
            stdout=self._stdout,
            stderr=self._stderr,
            **self._subprocess_kwargs
        )
        self._active_thread = asyncio.ensure_future(self._communicate_async())
        return self._process

    def _communicate(self):
        while not self._stop.is_set():
            try:
                self._process.communicate()
            except Exception as exc:
                logging.error(f"Failed to communicate with process: {str(type(exc))}, {str(exc)}")

    async def _read_stream(self, stream: StreamReader, callback: Callable[[str], None]) -> None:
        """
        Read content from the given stream an capture the output.

        Args:
            stream (StreamReader): Reader from which to collect the output.
            callback (Callable[[str], None]): Callback function to execute upon reading a line from the stream.

        Returns:
            None

        """
        while stream:
            line = await stream.readline()
            if line:
                callback(
                    line.decode("utf-8") if isinstance(line, bytes) else line
                )
            else:
                break

    async def _install_log_listeners(self) -> None:
        """Install the log listeners on the output streams of the process."""
        listeners: List[Callable[[str], None]] = []
        if self._on_stdout_message:
            listeners.append(
                asyncio.create_task(self._read_stream(self._process.stdout, self._on_stdout_message))
            )
        if self._on_stderr_message:
            listeners.append(
                asyncio.create_task(self._read_stream(self._process.stderr, self._on_stderr_message))
            )

        if listeners:
            await asyncio.wait(listeners)

    async def _communicate_async(self) -> None:
        try:
            await self._install_log_listeners()
            stdout, stderr = await self._process.communicate()
            log_string = f"Process exited with return code: {self.returncode}"

            if self.returncode not in self.success_return_codes:
                logging.error(log_string)
            else:
                logging.info(log_string)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logging.error(f"Failed to communicate with process: {str(type(exc))}, {str(exc)}")

    def stop(self):
        self.shutdown()
        logging.info(f"Received terminate command for {self._process.pid}")
        self._process.terminate()
        return self._process.returncode

    def kill(self):
        self.shutdown()
        logging.info(f"Received kill command for process group {self._process.pid}")
        self._kill(self._process.pid)
        return self._process.returncode

    def _kill(self, process_id: int, parent_pid=None):
        process = psutil.Process(process_id)
        for child in process.children():
            self._kill(child.pid, parent_pid=process_id)
        logging.info(f"Received kill command for {process_id}. Parent process: {parent_pid}")

        try:
            process.kill()
        except psutil.NoSuchProcess:
            logging.info(f"Process with {process_id} no longer exists.")
            return

        if platform.system().lower() == "windows" and process.is_running():
            try:
                os.system(f"C:\\Windows\\System32\\taskkill.exe /F /PID {process.pid}")
            except Exception as exc:
                logging.warning(f"Failed to call taskkill: {str(type(exc))}, {str(exc)}")

    @property
    def process_id(self) -> Optional[str]:
        """
        Unique identifier of the process being executed, if it has been spawned.

        Args:
            None

        Returns:
            Optional[str]: The unique identifier of the process that was spawned, or ``None`` otherwise.

        """
        if not self._process:
            return None
        return str(self._process.pid)

    @property
    def status(self) -> Optional[str]:
        if not self._process:
            return None

        if hasattr(self._process, "status"):
            return self._process.status

        if self.is_active:
            return "running"

        if self.completed:
            return "finished"

        return "errored"

    @property
    def returncode(self):
        return self._process.returncode

    @property
    def success_return_codes(self):
        return self._success_return_codes

    @property
    def completed(self) -> bool:
        """Has process completed succesfully."""
        return self.returncode in self.success_return_codes

    @property
    def is_running(self):
        """Either the process knows about it, or we assume it's a python process."""
        return (self.status == "running") or (self.is_active and self.status == "python")

    @property
    def is_active(self):
        return self._resolve_is_active()

    @property
    def task_id(self):
        return self._task_id

    def _resolve_is_active(self) -> bool:
        """Resolve if an instance is active."""
        return psutil.pid_exists(self._process.pid)

    def shutdown(self):
        """Clean up any active threads."""
        if hasattr(self._active_thread, "cancel"):
            self._active_thread.cancel()

    def get_logs(self) -> List[str]:
        """
        Return the list of log entries captured from the ``stdout`` stream of the process.

        Args:
            None

        Returns:
            List[str]: The list of log entries captured from the ``stdout`` stream of the process.

        """
        with self._log_read_lock:
            logs = self._std_output
            self._std_output = []
            return logs

    @property
    def command(self):
        """Command property."""
        return self._command


class ProcessManager(Facility):
    """Start, monitor and manage processes."""

    _instance_type_cls = BaseInstance

    def __init__(
        self,
        job_store: BaseJobStore,
        log_upload_interval: int = 10,
        log_upload_endpoint: str = "http://127.0.0.1:8011/queue/management/logs/upload",
    ):
        """Process manager constructor."""
        super().__init__()

        self._agent_id = f"{socket.getfqdn()}-{os.getpid()}"
        self._log_upload_interval = log_upload_interval
        self._taskid_process_map = {}

        self._settings = FarmJobsConfig(auto_configure_logging=False).jobs
        self._supported_instance_payload_versions = [str(v) for v in self._settings.supported_instance_payload_versions.to_list()]
        self._job_store = job_store

        self._available_jobs = []
        self._active_processes: DefaultDict[str, List[BaseInstance]] = collections.defaultdict(list)
        self._finished_processes: DefaultDict[str, List[BaseInstance]] = collections.defaultdict(list)
        self._errored_processes: DefaultDict[str, List[BaseInstance]] = collections.defaultdict(list)
        self._process_std_output: DefaultDict[str, List[str]] = collections.defaultdict(list)

        self._log_upload_endpoint = log_upload_endpoint

    @property
    def job_store(self) -> BaseJobStore:
        """Retrieve the job store."""
        return self._job_store

    @property
    def active_processes(self) -> Dict:
        """
        Run a dictionary of active processes monitored by the manager.

        Note that an active process can map to several statuses, e.g: starting & running.

        Returns:
            Dict[str, List]: The list of jobs grouped by job type.
        """
        return self._active_processes

    @property
    def finished_processes(self) -> Dict:
        """
        Return a dictionary of finished processes collected by the manager.

        Returns:
            Dict[str, List]: The list of jobs grouped by job type.
        """
        return self._finished_processes

    @property
    def errored_processes(self) -> Dict:
        """
        Return a dictionary of errored processes collected by the manager.

        Returns:
            Dict[str, List]: The list of jobs grouped by job type.
        """
        return self._errored_processes

    @property
    def available_process_keys(self):
        """Available process keys property."""
        return [(job_name, job.task_function) for job_name, job in self._job_store.job_specs.items() if job.active]

    @property
    def available_job_specs(self) -> List:
        """Available job spec property."""
        return list(self._job_store.job_specs.values())

    def _create_spawn_response(self, process_id: str, status: str) -> SpawnResponseModel:
        """Create the response to the request to /spawn enveloping a process id and status."""
        return SpawnResponseModel(
            jsonapi={"version": "1.0"},
            data=ProcessCreationPayload(process_id=process_id, process_status=status)
        )

    def _get_instance_payload(self, payload: Dict) -> InstancePayload:
        """Instance payload is a combination of runtime arguments and metadata required for the instance to run.

        Args:
            payload (dict): This comes from a spawn call, which can come from a REST API or a CLI or an API.
                it traditonally contains the arguments to give to a process, but can also contain the metadata and apiversion.

        Returns:
            InstancePayload: A dataclass that wraps the process arguments and metadata.
        """
        args = payload
        metadata = {}
        task_requirements = {}

        if "jsonapi" in payload:
            api_version = payload["jsonapi"].get("version")
            if api_version not in self._supported_instance_payload_versions:
                raise RuntimeError(f"Unsupported API version: {api_version}")

            args = payload["data"]["allowed_args"]
            metadata = payload["data"]["metadata"]
            task_requirements = payload["data"].get("task_requirements", {})

        return InstancePayload(
            args=args,
            metadata=metadata,
            task_requirements=task_requirements
        )

    def _create_instance_from_job(self, job: BaseJob, task_id: str = None) -> BaseInstance:
        return self._instance_type_cls(
            command=job.command,
            container=job.container,
            args=job.args,
            env=job.env,
            stdin=job.stdin,
            stdout=job.stdout,
            stderr=job.stderr,
            subprocess_kwargs=job.subprocess_kwargs,
            on_stdout_message=job.on_stdout_message,
            on_stderr_message=job.on_stderr_message,
            success_return_codes=job.success_return_codes,
            working_directory=job.working_directory,
            task_id=task_id
        )

    async def _spawn_instance_async(
        self,
        job,
        task_id: str = None,
        job_definition: JobDefinition = None,
        metadata: Dict = None,
        task_requirements: Dict = None
    ) -> BaseInstance:
        task_requirements = task_requirements or {}
        metadata = metadata or {}
        capacity_requirements = copy.deepcopy(job_definition.capacity_requirements or {})

        # merge task requirements with job definition requirements
        job_env_list = capacity_requirements.get("env", [])
        task_env_list = task_requirements.get("env", [])
        task_env_keys = {e["name"] for e in task_env_list}
        filtered_job_env_list = [e for e in job_env_list if e["name"] not in task_env_keys]
        filtered_job_env_list.extend(task_env_list)

        # add task id to env
        filtered_job_env_list.append({"name": "OV_FARM_TASK_ID", "value": task_id})

        # update job definition with the new env list
        capacity_requirements["env"] = filtered_job_env_list

        instance = self._create_instance_from_job(job, task_id=task_id)

        await instance.spawn_async(requirements=capacity_requirements, metadata=metadata)
        return instance

    async def _retrieve_instance_async(self, job: BaseJob, task_id: str) -> BaseInstance:
        instance = self._create_instance_from_job(job, task_id=task_id)
        await instance.retrieve_async(task_id)
        return instance

    async def _run(self) -> None:
        """Run the process."""
        while True:
            try:
                await self.monitor_processes()
            except Exception as exc:
                logging.error(f"Failed to check on running processes: {str(exc)}")
            finally:
                await asyncio.sleep(30)

    async def run(self) -> None:
        """Run the process."""
        try:
            await self._run()
        except asyncio.exceptions.CancelledError:
            logging.debug("ProcessManager.run coroutine has been cancelled.")

    def _process_error(self, task_id: str, command: str, exc: Exception) -> SpawnResponseModel:
        """Create an error process id, logs to stderr and add to the task stdout."""
        error_process_id = str(self._generate_error_process_id())

        error_message = f"ERROR: Farm Agent could not start an instance of the \"{command}\" command.",
        if isinstance(exc, FileNotFoundError):
            # Exception raised if the job's command could not be resolved on the host where the Agent is running.
            error_message = f"ERROR: Farm Agent could not find a \"{command}\" command to execute."

        process_error_message = [
            f"{error_message} ",
            "Additional information from the host are listed below:\n\n",
            f"{str(type(exc))}: {str(exc)}\n",
        ]

        logging.error("\n".join(process_error_message))
        self._process_std_output[error_process_id] = process_error_message
        self._taskid_process_map[error_process_id] = task_id
        return self._create_spawn_response(error_process_id, "errored")

    def _get_full_job_args(self, args: List[str], job_type: BaseJob, job_definition: JobDefinition) -> List[str]:
        """Retrieve the full list of arguments prior to submiting a job."""
        allowed_args = job_type.allowed_args.copy()
        allowed_args.update(job_definition.allowed_args)

        full_args = []
        for arg in job_definition.args:
            # Split '--enable' args
            if arg.startswith("--enable"):
                parts = arg.split(" ")
                full_args.extend(parts)
            else:
                full_args.append(arg)

        for path in job_definition.extension_paths:
            full_args.extend(["--ext-folder", path])

        full_args.extend(self._process_allowed_args(args, allowed_args))
        return full_args

    def _create_job_from_payload(self, job_name: str, payload: dict) -> BaseJob:
        # Unpack the payload.
        instance_payload = self._get_instance_payload(payload)
        args = instance_payload.args

        job_definition = self._job_store.job_specs[job_name]
        job_type = get_job_type(job_definition.job_type)

        full_args = self._get_full_job_args(args, job_type, job_definition)

        return job_type.from_job_definition(job_definition, args=full_args)

    async def spawn(self, job_name: str, payload: Dict, monitor: bool = True, task_id: str = None) -> SpawnResponseModel:
        """Spawn a process and add to list of active processes."""
        instance_payload = self._get_instance_payload(payload)
        args = instance_payload.args
        metadata = instance_payload.metadata
        task_requirements = instance_payload.task_requirements

        job_definition = self._job_store.job_specs[job_name]
        job_type = get_job_type(job_definition.job_type)

        full_args = self._get_full_job_args(args, job_type, job_definition)

        job = job_type.from_job_definition(job_definition, args=full_args)
        try:
            proc = await self._spawn_instance_async(job, task_id, job_definition=job_definition, metadata=metadata, task_requirements=task_requirements)
            self._taskid_process_map[proc.process_id] = task_id
        except Exception as exc:
            return self._process_error(task_id, job.command, exc)

        self._active_processes[job_name].append(proc)
        return self._create_spawn_response(proc.process_id, proc.status)

    async def retrieve(self, job_name: str, payload: Dict, monitor: bool = True, task_id: str = None) -> SpawnResponseModel:
        """Retrieve SpawnResponseModel for job."""
        instance_payload = self._get_instance_payload(payload)
        args = instance_payload.args

        job_definition = self._job_store.job_specs[job_name]
        job_type = get_job_type(job_definition.job_type)

        full_args = self._get_full_job_args(args, job_type, job_definition)

        job = job_type.from_job_definition(job_definition, args=full_args)
        # if we fail to retrieve an instance, this below line throws an exception
        # NOTE: for NVCT need to get the NVCT Task ID not the Farm Task Id
        proc = await self._retrieve_instance_async(job, task_id)

        self._taskid_process_map[proc.process_id] = task_id
        self._active_processes[job_name].append(proc)
        return self._create_spawn_response(proc.process_id, proc.status)

    def _process_allowed_args(self, args: Dict[str, str], allowed_args: Dict[str, Dict]) -> List[str]:
        """
        Process and update provided arguments with their actual commandline argument.

        Arguments
            args: (Dict[str, str]): The list of arguments as submitted by the job
            allowed_args: (Dict[str, Dict]): A dictionary containing the commandline values for the argument and the separator to use.

        Returns:
            List[str]
        """
        processed_args = []
        positional_args = []
        for arg, value in args.items():
            arg_cmdline_name = allowed_args[arg]["arg"]
            if isinstance(arg_cmdline_name, int) or arg_cmdline_name.isdigit():
                positional_args.append((int(arg_cmdline_name), value))
                continue
            separator = allowed_args[arg].get("separator", "=")
            if separator == " ":
                processed_args.extend([arg_cmdline_name, value])
            else:
                processed_args.append(f"{arg_cmdline_name}{separator}{value}")

        for positional_number, value in sorted(positional_args):
            processed_args.insert(positional_number, value)

        return processed_args

    def _generate_error_process_id(self) -> int:
        """
        Generate a random number in the [INT_MIN_VALUE; -1] range.

        To represent a fictitious process ID for a job that
        errored, so that clients can query the status, logs and general properties of the process. Using negative
        numbers here ensure there would be no conflict with legitimate unique process identifiers. This also makes it
        possible for the Farm APIs to identify the process as being in an error state when attempting to query its
        status.

        Furthermore, this also makes it possible to programmatically query for the number of processes that failed to
        launch correctly, based on their PID being negative.

        Returns:
            int: A fictitious unique identifier for the process which failed to launch.

        """
        error_process_id = -secrets.randbelow(sys.maxsize)
        while error_process_id in self._active_processes:
            error_process_id = -secrets.randbelow(sys.maxsize)
        return error_process_id

    async def monitor_processes(self):
        """Monitor the processes for running tasks."""
        processes_to_remove = collections.defaultdict(list)

        for process_type, procs in self._active_processes.items():
            for proc in procs:
                if proc.is_active:
                    self._process_std_output[proc.process_id] = proc.get_logs()
                else:
                    logging.info(f"Transitioning {proc.process_id} to process_to_remove")
                    processes_to_remove[process_type].append(proc)

        for process_type, procs in processes_to_remove.items():
            for proc in procs:
                # Record the last content of the log before removing the process from the list of processes to monitor:
                self._process_std_output[proc.process_id] = proc.get_logs()
                self._process_std_output[proc.process_id].append(f"Process exited with return code: {proc.returncode}")
                if proc.completed:
                    logging.info(f"Transitioning {proc.process_id} to Completed")
                    self._finished_processes[process_type].append(proc)
                else:
                    logging.info(f"Transitioning {proc.process_id} to Failed")
                    self._errored_processes[process_type].append(proc)

                # Clean up any active threads from the process.
                proc.shutdown()

                self._active_processes[process_type].remove(proc)

    def stop(self):
        """Stop the ProcessManager by killing all active processes."""
        logging.debug("Killing all active process in the process manager.")
        for _process_type, procs in self._active_processes.items():
            for process in procs:
                process.kill()
        logging.debug("All active processes have been killed.")

    async def stop_async(self):
        """Stop the ProcessManager by killing all active processes."""
        self.stop()

    def stop_process(self, process_type, process_id, kill=False):
        """Stop a process by process_type and process_id."""
        process_to_stop, active_processes = self._get_process_to_stop(process_type, process_id)
        if not process_to_stop:
            raise Exception(f"{process_id} not found")

        # On windows kill == terminate but on Unix will ensure a SIGINT is sent
        exit_code = process_to_stop.kill() if kill else process_to_stop.stop()

        active_processes.remove(process_to_stop)
        return exit_code

    def _get_process_to_stop(self, process_type, process_id) -> Tuple:
        active_processes = self._active_processes[process_type]

        for process in active_processes:
            if process.process_id == process_id:
                return process, active_processes

        return None, active_processes

    async def stop_process_async(self, process_type, process_id, kill=False) -> int:
        """Stop a process asynchroniously."""
        return self.stop_process(process_type, process_id, kill=kill)

    async def _process_logs(self):
        """While active, process logs and upload them."""
        while True:
            process_ids = list(self._process_std_output.keys())
            for process_id in process_ids:
                try:
                    await self._retrieve_and_upload_logs(process_id)
                except Exception as exc:
                    logging.warning(f"Failed to upload logs: {str(exc)}")

            await asyncio.sleep(self._log_upload_interval)

    async def process_logs(self):
        """While active, process logs and upload them."""
        try:
            await self._process_logs()
        except asyncio.exceptions.CancelledError:
            logging.debug("ProcessManager.process_logs coroutine has been cancelled.")

    async def _retrieve_and_upload_logs(self, process_id: str):
        log_lines = self.get_logs(process_id)
        if not log_lines:
            return

        log_lines = "".join(log_lines)

        task_id = self._taskid_process_map.get(process_id, None)
        if not task_id:
            logging.warning(f"No task_id for {process_id}. Cannot process logs")
            return

        payload = dict(agent_id=self._agent_id, task_id=task_id, logs=log_lines)
        await post_data(self._log_upload_endpoint, data=payload)

    def get_logs(self, process_id: str) -> List[str]:
        """
        Return the list of log entries for the given process.

        Args:
            process_id (str): Unique identifier of the process for which to return the list of log entries.

        Returns:
            List[str]: The list of log entries for the given process.
        """
        # The value is popped to make sure no old logs are kept in memory
        return self._process_std_output.pop(process_id, [])
