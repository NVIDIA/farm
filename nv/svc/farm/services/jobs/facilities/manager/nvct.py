# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service NVCT Manager Facility."""

import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode
import uuid
from typing import Any, Callable, Dict, List, Optional

import dynaconf
from nv.svc.farm import utils
from nv.svc.farm.services.jobs.job_types.base import BaseJob
from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore
from nv.svc.farm.services.jobs.facilities.manager.base import (
    BaseInstance,
    BaseRemoteProcess,
    ProcessManager,
)


class AccessToken:
    """Helper for AccessToken with refresh functionality."""

    def __init__(self, username, password, authn_endpoint, timeout: int, verify_ssl: bool = False):
        self.username = username
        self.password = password
        self.authn_endpoint = authn_endpoint
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.token = None
        self.token_type = None
        self.expires_in = 0
        self.scope = None
        self.valid_until = datetime.now()

    async def refresh(self):
        data = {
            "scope": "launch_task task_details cancel_task delete_task list_events list_results list_tasks",
            "grant_type": "client_credentials"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            response_obj = await session.post(
                self.authn_endpoint,
                data=urlencode(data),
                headers=headers,
                auth=aiohttp.BasicAuth(self.username, self.password),
                timeout=self.timeout,
                verify_ssl=self.verify_ssl,
            )
            response = await response_obj.json()

        if "access_token" not in response:
            raise Exception("Token received from authn endpoint is empty.")
        self.token = response["access_token"]
        self.token_type = response["token_type"]
        self.expires_in = response["expires_in"]
        self.scope = response["scope"]
        self.valid_until = datetime.now() + timedelta(seconds=self.expires_in)

    def is_valid(self):
        return datetime.now() < self.valid_until

    def get_auth_header(self):
        return f"{self.token_type} {self.token}"


class NVCTClient:
    """NVCTClient helper."""

    def __init__(self, username: str, password: str, disable_authn: bool, authn_endpoint: str, api_endpoint: str, timeout: int, verify_ssl: bool = False):
        """NVCT client constructor."""

        self.disable_authn = disable_authn
        self.token = AccessToken(
            username=username,
            password=password,
            authn_endpoint=authn_endpoint,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self._api_endpoint = api_endpoint

        self.task_create_url = self._api_endpoint
        self.task_info_url_fmt = self._api_endpoint + "/{task_id}"
        self.task_bulk_info_url = self._api_endpoint + "/bulk"
        self.task_delete_url_fmt = self._api_endpoint + "/{task_id}"
        self.task_events_url_fmt = self._api_endpoint + "/{task_id}/events"
        self.task_cancel_url_fmt = self._api_endpoint + "/{task_id}/cancel"

        self.timeout = timeout
        self.verify_ssl = verify_ssl

    async def get_headers(self):
        """Get default headers containing auth."""

        # authn is disabled, in cases of mocking nvct without any authentication services
        if self.disable_authn:
            return {}

        if not self.token.is_valid():
            await self.token.refresh()
        headers = {
            "Authorization": self.token.get_auth_header(),
            "Content-Type": "application/json"
        }
        return headers

    async def get_task_status(self, task_id) -> str:
        """Read the specified task and returns its status."""

        task = await self.retrieve_task(task_id)
        return task["status"]

    async def delete_task(self, task_id: str):
        """Delete a NVCT Task."""

        url = self.task_delete_url_fmt.format(task_id=task_id)
        headers = await self.get_headers()
        await utils.delete_request(url, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)

    async def retrieve_task(self, task_id: str) -> Dict:
        """Retrieve NVCT Task."""

        url = self.task_info_url_fmt.format(task_id=task_id)
        headers = await self.get_headers()
        response = await utils.fetch_data(url, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)
        return response["task"]

    async def retrieve_tasks(self, task_ids: list):
        url = self.task_bulk_info_url
        headers = await self.get_headers()
        try:
            response = await utils.post_data(url, data={"taskIds": task_ids}, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)
            return response["tasks"]
        except Exception as e:
            logging.error(f"Error retrieving tasks from NVCT: {e}")
            return []

    async def cancel_task(
        self,
        task_id: str
    ) -> str:
        """Cancel a NVCT Task."""
        headers = await self.get_headers()
        url = self.task_cancel_url_fmt.format(task_id=task_id)
        await utils.post_data(url, data={}, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)

    async def create_task(
        self,
        name: str,
        container_image: str,
        max_runtime_duration: str,
        max_queued_duration: str,
        result_handling_strategy: str,
        gpu_specification: Dict,
        container_args: str = None,
        container_environment: list = None,
        tags: list = None,
        description: str = None,
        results_location: str = None,
        models: list = None,
        resources: list = None,
        secrets: list = None,
        termination_grace_period_duration: str = None,
    ) -> str:
        """Create a NVCT Task."""

        # following the NVCT openapi spec using camelCase keys
        data = {
            "name": name,
            "gpuSpecification": gpu_specification,
            "containerImage": container_image,
            "maxRuntimeDuration": max_runtime_duration,
            "maxQueuedDuration": max_queued_duration,
            "resultHandlingStrategy": result_handling_strategy,
        }
        if container_args:
            data["containerArgs"] = container_args
        if container_environment:
            data["containerEnvironment"] = container_environment
        if tags:
            data["tags"] = tags
        if description:
            data["description"] = description
        if results_location:
            data["resultsLocation"] = results_location
        if models:
            data["models"] = models
        if resources:
            data["resources"] = resources
        if secrets:
            data["secrets"] = secrets
        if termination_grace_period_duration:
            data["terminationGracePeriodDuration"] = termination_grace_period_duration

        headers = await self.get_headers()
        response = await utils.post_data(self.task_create_url, data=data, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)

        nvct_task_id = response["task"]["id"]
        logging.info(f"NVCT Task ID: '{nvct_task_id}', for Task Name '{name}'")
        return nvct_task_id


class NVCTInstance(BaseInstance):
    """Instance for NVCT."""

    def __init__(
        self,
        nvct_client: NVCTClient,
        command: str,
        container: str,
        args: List[str],
        env: Dict[str, Any] = None,
        stdin=None,
        stdout=None,
        stderr=None,
        on_stdout_message: Callable[[str], None] = None,
        on_stderr_message: Callable[[str], None] = None,
        success_return_codes: List[str] = None,
        working_directory: str = None,
        task_id: str = None,
        default_gpu_specification: Dict = None,
        default_max_runtime_duration: str = None,
        default_max_queued_duration: str = None,
        default_result_handling_strategy: str = None,
        default_secrets: list = None,
    ):
        super().__init__(
            command=command,
            container=container,
            args=args,
            env=env,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            subprocess_kwargs=None,
            on_stdout_message=on_stdout_message,
            on_stderr_message=on_stderr_message,
            success_return_codes=success_return_codes,
            working_directory=working_directory,
            task_id=task_id
        )
        self._nvct_client = nvct_client
        self._active_check_delay = 30
        self._default_gpu_specification = default_gpu_specification
        self._default_max_runtime_duration = default_max_runtime_duration
        self._default_max_queued_duration = default_max_queued_duration
        self._default_result_handling_strategy = default_result_handling_strategy
        self._default_secrets = default_secrets

    def spawn(self):
        raise NotImplementedError("The NVCTInstance cannot be spawned in a threaded mode.")

    async def retrieve_async(self, task_id: str):
        self._stop = asyncio.Event()
        self._process = BaseRemoteProcess(task_id)
        # Note that we also reconcile a "starting" task. Here we are marking it as running.
        self._process.set_status("running")
        return self._process

    async def spawn_async(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        self._stop = asyncio.Event()

        metadata = metadata or {}
        requirements = requirements or {}

        # Keys from capacity_requirements/metadata should be camelCase per NVCT CreateTaskRequest.
        task_name = metadata.get("name", requirements.get("name", f"{self._task_id}--{str(uuid.uuid4())[-4:]}"))

        tags = metadata.get("tags", requirements.get("tags", []))
        tags.extend(["OV-FARM", self._task_id])
        description = metadata.get("description", requirements.get("description", f"OV-Farm Task ID {self._task_id}"))

        container_args = metadata.get("containerArgs", requirements.get("containerArgs", self._args))
        if isinstance(container_args, list):
            container_args = " ".join(container_args)

        secrets = self._default_secrets or []
        secrets.extend(metadata.get("secrets", []))
        secrets.extend(requirements.get("secrets", []))

        nvct_task_id = await self._nvct_client.create_task(
            name=task_name,
            container_image=metadata.get("containerImage", self._container_image),
            max_runtime_duration=metadata.get("maxRuntimeDuration", requirements.get("maxRuntimeDuration", self._default_max_runtime_duration)),
            max_queued_duration=metadata.get("maxQueuedDuration", requirements.get("maxQueuedDuration", self._default_max_queued_duration)),
            result_handling_strategy=metadata.get("resultHandlingStrategy", requirements.get("resultHandlingStrategy", self._default_result_handling_strategy)),
            gpu_specification=metadata.get("gpuSpecification", requirements.get("gpuSpecification", self._default_gpu_specification)),
            container_args=container_args,
            container_environment=metadata.get("containerEnvironment", requirements.get("containerEnvironment")),
            tags=tags,
            description=description,
            models=metadata.get("models", requirements.get("models")),
            resources=metadata.get("resources", requirements.get("resources")),
            secrets=secrets,
            results_location=metadata.get("resultsLocation", requirements.get("resultsLocation")),
            termination_grace_period_duration=metadata.get("terminationGracePeriodDuration", requirements.get("terminationGracePeriodDuration")),
        )
        self._process = BaseRemoteProcess(process_id=nvct_task_id)
        return self._process

    async def stop_async(self):
        try:
            await self._nvct_client.cancel_task(task_id=self._process.pid)
        except Exception as exc:
            logging.error(f"Unable to terminate NVCT Task '{self._process.pid}' {str(type(exc))} {str(exc)}")
            raise

        self._process.set_returncode(-1)
        self.shutdown()
        return self._process.returncode

    async def kill_async(self):
        return await self.stop_async()

    def stop(self):
        asyncio.ensure_future(self.stop_async())
        return -1

    def kill(self):
        return self.stop()

    @property
    def is_active(self) -> bool:
        return self.returncode is None


class NVCTProcessManager(ProcessManager):
    """Start, monitor and manage NVCT tasks."""

    _instance_type_cls = NVCTInstance

    def __init__(
        self,
        job_store: BaseJobStore,
        log_upload_interval: int = 10,
        log_upload_endpoint: str = "",
        disable_authn: bool = False,
        authn_endpoint: str = "",
        api_endpoint: str = "",
        username: str = None,
        password: str = None,
        client_request_timeout: int = 60,
        client_verify_ssl: bool = False,
        default_gpu: str = "A100",
        default_gpu_backend: str = "AZURE",
        default_gpu_instance_type: str = "AZURE.GPU.A100_1x",
        default_max_runtime_duration: str = "PT1H",
        default_max_queued_duration: str = "PT3H",
        default_result_handling_strategy: str = "NONE",
        default_secrets: list = None,
    ):
        assert username and password, "username and password required."
        super().__init__(job_store, log_upload_interval, log_upload_endpoint)
        self._nvct_client = NVCTClient(
            username=username,
            password=password,
            disable_authn=disable_authn,
            authn_endpoint=authn_endpoint,
            api_endpoint=api_endpoint,
            timeout=client_request_timeout,
            verify_ssl=client_verify_ssl,
        )
        self._default_gpu_specification = {
            "gpu": default_gpu,
            "backend": default_gpu_backend,
            "instanceType": default_gpu_instance_type
        }
        self._default_max_runtime_duration = default_max_runtime_duration
        self._default_max_queued_duration = default_max_queued_duration
        self._default_result_handling_strategy = default_result_handling_strategy
        self._default_secrets = default_secrets
        if isinstance(self._default_secrets, dynaconf.vendor.box.box_list.BoxList):
            self._default_secrets = self._default_secrets.to_list()
        logging.info("Controller using NVCTProcessManager.")

    def _create_instance_from_job(self, job: BaseJob, task_id: str = None) -> NVCTInstance:
        logging.info(f"Creating NVCT instance for farm task_id {task_id}")
        return self._instance_type_cls(
            self._nvct_client,
            command=job.command,
            container=job.container,
            args=job.args,
            env=job.env,
            stdin=job.stdin,
            stdout=job.stdout,
            stderr=job.stderr,
            on_stdout_message=job.on_stdout_message,
            on_stderr_message=job.on_stderr_message,
            success_return_codes=job.success_return_codes,
            working_directory=job.working_directory,
            task_id=task_id,
            default_gpu_specification=self._default_gpu_specification,
            default_max_runtime_duration=self._default_max_runtime_duration,
            default_max_queued_duration=self._default_max_queued_duration,
            default_result_handling_strategy=self._default_result_handling_strategy,
            default_secrets=self._default_secrets,
        )

    async def stop_process_async(self, process_type, process_id, kill=False) -> int:
        process_to_stop, active_processes = self._get_process_to_stop(process_type, process_id)
        if not process_to_stop:
            raise Exception(f"{process_id} not found")

        exit_code = await process_to_stop.kill_async() if kill else await process_to_stop.stop_async()
        active_processes.remove(process_to_stop)
        return exit_code

    def update_process(self, process, status: Optional[str] = None):
        if status is None:
            logging.error(f"Status is None for {process._process.pid}")
            return

        if status == "QUEUED":
            logging.info(f"Setting {process._process.pid} to waiting")
            process._process.set_status("waiting")
        elif status == "LAUNCHED":
            logging.info(f"Setting {process._process.pid} to starting")
            process._process.set_status("starting")
        elif status == "COMPLETED":
            logging.info(f"Setting {process._process.pid} to finished")
            process._process.set_returncode(0)
            process._process.set_status("finished")
        elif status in ("ERRORED", "EXCEEDED_MAX_RUNTIME_DURATION", "EXCEEDED_MAX_QUEUED_DURATION"):
            logging.info(f"Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")
        elif status == "CANCELED":
            logging.info(f"Setting {process._process.pid} to cancelled")
            process._process.set_returncode(-1)
            process._process.set_status("cancelled")
        elif status == "RUNNING":
            logging.info(f"Setting {process._process.pid} to running")
            process._process.set_status("running")
        else:
            logging.error(f"Unmapped state from NVCT: {status}. Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")

    async def update_processes(self):
        task_ids = [process._process.pid for processes in self._active_processes.values() for process in processes]

        if len(task_ids) == 0:
            logging.info("No task ids to update, skipping NVCT update")
            return

        bulk_tasks = await self._nvct_client.retrieve_tasks(task_ids=task_ids)
        bulk_tasks_dict = {task["id"]: task for task in bulk_tasks}

        if len(bulk_tasks_dict) == 0:
            logging.info("No processes retrieved from NVCT, skipping process update")
            return

        for processes in self._active_processes.values():
            for process in processes:
                status = bulk_tasks_dict.get(process._process.pid, {}).get("status")
                self.update_process(process=process, status=status)

    async def monitor_processes(self):
        await self.update_processes()
        return await super().monitor_processes()
