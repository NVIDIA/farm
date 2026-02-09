# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service NVCF Manager Facility."""

import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode
from typing import Any, Callable, Dict, List, Optional

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

    def __init__(self, username, password, authn_endpoint, timeout: int, verify_ssl: bool = False, api_key: str = None):
        self.username = username
        self.password = password
        self.authn_endpoint = authn_endpoint
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.api_key = api_key
        self.token = None
        self.token_type = None
        self.expires_in = 0
        self.scope = None
        self.valid_until = datetime.now()

    async def refresh(self):
        data = {
            "scope": "list_functions delete_function deploy_function invoke_function list_function_details register_function update_function",
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
        if self.api_key:
            return True

        return datetime.now() < self.valid_until

    def get_auth_header(self):
        if self.api_key:
            return f"Bearer {self.api_key}"

        return f"{self.token_type} {self.token}"


class NVCFClient:
    """NVCFClient helper."""

    def __init__(self, username: str, password: str, authn_endpoint: str, api_endpoint: str, timeout: int, verify_ssl: bool = False, api_key: str = None):
        """NVCF client constructor."""

        self.token = AccessToken(
            username=username,
            password=password,
            authn_endpoint=authn_endpoint,
            timeout=timeout,
            verify_ssl=verify_ssl,
            api_key=api_key,
        )
        self._api_endpoint = api_endpoint

        self.functions_url = self._api_endpoint + "/functions"
        self.deploy_function_url = self._api_endpoint + "/deployments/functions/{function_id}/versions/{version_id}"
        self.delete_function_url = self._api_endpoint + "/functions/{function_id}/versions/{version_id}"
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    async def get_headers(self):
        """Get default headers containing auth."""
        if not self.token.is_valid():
            await self.token.refresh()
        headers = {
            "Authorization": self.token.get_auth_header(),
            "Content-Type": "application/json"
        }
        return headers

    async def deactivate_function(self, function_id: str, version_id: str):
        """Deactivate a NVCF Task."""
        url = self.deploy_function_url.format(function_id=function_id, version_id=version_id)
        headers = await self.get_headers()
        await utils.delete_request(url, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl, params={"graceful": "true"})

    async def delete_function(self, function_id: str, version_id: str):
        """Delete a NVCF Task."""
        url = self.delete_function_url.format(function_id=function_id, version_id=version_id)
        headers = await self.get_headers()
        await utils.delete_request(url, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)

    async def list_functions(self):
        headers = await self.get_headers()
        try:
            query_params = {"visibility": "private"}

            response = await utils.fetch_data(
                self.functions_url,
                params=query_params,  # Use params instead of data for GET requests
                headers=headers,
                timeout=self.timeout,
                verify_ssl=self.verify_ssl
            )
            return response.get("functions", [])
        except Exception as e:
            logging.error(f"Error retrieving functions from NVCF: {e}")
            return []

    async def deploy_function(
        self,
        function_id: str,
        version_id: str,
        deployment_specifications: List[Dict]
    ):
        """Deploy NVCF Function."""

        data = {
            "deploymentSpecifications": deployment_specifications
        }

        url = self.deploy_function_url.replace("{function_id}", function_id).replace("{version_id}", version_id)
        headers = await self.get_headers()

        await utils.post_data(url, data=data, headers=headers, timeout=self.timeout, verify_ssl=self.verify_ssl)


class NVCFInstance(BaseInstance):
    """Instance for NVCF."""

    def __init__(
        self,
        nvcf_client: NVCFClient,
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
        task_id: str = None
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
        self._nvcf_client = nvcf_client
        self._active_check_delay = 30

    def spawn(self):
        raise NotImplementedError("The NVCFInstance cannot be spawned in a threaded mode.")

    async def retrieve_async(self, task_id: str):
        self._stop = asyncio.Event()
        self._process = BaseRemoteProcess(task_id)
        # Note that we also reconcile a "starting" task. Here we are marking it as running.
        self._process.set_status("running")
        return self._process

    async def spawn_nvcf_process(self, function_id: str, version_id: str, deployment_specifications: List[Dict]):

        if self.command == "deploy":
            await self._nvcf_client.deploy_function(function_id, version_id, deployment_specifications=deployment_specifications)
        elif self.command == "deactivate":
            await self._nvcf_client.deactivate_function(function_id, version_id)
        elif self.command == "delete-function":
            await self._nvcf_client.delete_function(function_id, version_id)
            self._process.set_status("finished")
            self._process.set_returncode(0)
        else:
            raise Exception(f"Invalid command: {self.command}")

    async def spawn_async(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        self._stop = asyncio.Event()

        metadata = metadata or {}
        requirements = requirements or {}
        function_id = metadata.get("functionId", requirements.get("functionId"))
        version_id = metadata.get("versionId", requirements.get("versionId"))
        deployment_specifications = metadata.get("deploymentSpecifications", requirements.get("deploymentSpecifications", []))
        self._process = BaseRemoteProcess(process_id=f"{function_id}:{version_id}:{self.task_id}")

        try:
            await self.spawn_nvcf_process(
                function_id=function_id,
                version_id=version_id,
                deployment_specifications=deployment_specifications
            )
        except Exception as exc:
            logging.error(f"Unable to spawn NVCF Task '{self._process.pid}' {str(type(exc))} {str(exc)}")
            self._process.set_status("errored")
            self._process.set_returncode(-1)

        return self._process

    async def stop_async(self):
        try:
            function_id, version_id, _ = self._process.pid.split(":")
            await self._nvcf_client.deactivate_function(function_id, version_id)
        except Exception as exc:
            logging.error(f"Unable to terminate NVCF Task '{self._process.pid}' {str(type(exc))} {str(exc)}")
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


class NVCFProcessManager(ProcessManager):
    """Start, monitor and manage NVCF tasks."""

    _instance_type_cls = NVCFInstance

    def __init__(
        self,
        job_store: BaseJobStore,
        log_upload_interval: int = 10,
        log_upload_endpoint: str = "",
        authn_endpoint: str = "",
        api_endpoint: str = "",
        username: str = None,
        password: str = None,
        api_key: str = None,
        client_request_timeout: int = 60,
        client_verify_ssl: bool = False
    ):
        # Validate authentication parameters
        if not api_key and not (username and password):
            raise ValueError("Either api_key or username/password must be provided")

        super().__init__(job_store, log_upload_interval, log_upload_endpoint)
        self._nvcf_client = NVCFClient(
            username=username,
            password=password,
            api_key=api_key,
            authn_endpoint=authn_endpoint,
            api_endpoint=api_endpoint,
            timeout=client_request_timeout,
            verify_ssl=client_verify_ssl,
        )

        logging.info("Controller using NVCFProcessManager.")

    def _create_instance_from_job(self, job: BaseJob, task_id: str = None) -> NVCFInstance:
        logging.info(f"Creating NVCF instance for farm task_id {task_id}")
        return self._instance_type_cls(
            self._nvcf_client,
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
        )

    async def stop_process_async(self, process_type, process_id, kill=False) -> int:
        process_to_stop, active_processes = self._get_process_to_stop(process_type, process_id)
        if not process_to_stop:
            raise Exception(f"{process_id} not found")

        exit_code = await process_to_stop.kill_async() if kill else await process_to_stop.stop_async()
        active_processes.remove(process_to_stop)
        return exit_code

    def _handle_update_deployment_process(self, process, status: Optional[str] = None):
        if status is None:
            logging.error(f"Status is None for {process._process.pid}")
            return

        if status == "INACTIVE":
            logging.info(f"Skipping {process._process.pid} status update because it is INACTIVE")
            process._process.set_status("running")
        elif status == "ACTIVE":
            logging.info(f"Setting {process._process.pid} to finished")
            process._process.set_status("finished")
            process._process.set_returncode(0)
        elif status == "ERROR":
            logging.error(f"Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")
        elif status == "DEPLOYING":
            logging.info(f"Setting {process._process.pid} to running")
            process._process.set_status("running")
        else:
            logging.error(f"Unmapped state from NVCF: {status}. Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")

    def _handle_update_deactivate_process(self, process, status: Optional[str] = None):
        if status is None:
            logging.error(f"Status is None for {process._process.pid}")
            return

        if status == "INACTIVE":
            logging.info(f"Setting {process._process.pid} to finished")
            process._process.set_status("finished")
            process._process.set_returncode(0)
        elif status == "ACTIVE":
            logging.info(f"Setting {process._process.pid} to running")
            process._process.set_status("running")
        else:
            logging.error(f"Unmapped state from NVCF: {status}. Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")

    def _handle_update_delete_function_process(self, process, status: Optional[str] = None):
        if status is None:
            process._process.set_status("finished")
            process._process.set_returncode(0)
        else:
            process._process.set_returncode(-1)
            process._process.set_status("errored")

    def update_process(self, process, status: Optional[str] = None):
        if process.command == "deploy":
            self._handle_update_deployment_process(process, status)
        elif process.command == "deactivate":
            self._handle_update_deactivate_process(process, status)
        elif process.command == "delete-function":
            self._handle_update_delete_function_process(process, status)
        else:
            logging.error(f"Unmapped command: {process.command}. Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")

    async def update_processes(self):
        process_ids = [process._process.pid for processes in self._active_processes.values() for process in processes]

        if len(process_ids) == 0:
            logging.info("No process ids to update, skipping NVCF update")
            return

        list_functions_response = await self._nvcf_client.list_functions()
        list_functions_dict = {f"{function['id']}:{function['versionId']}": function for function in list_functions_response}

        if len(list_functions_dict) == 0:
            logging.info("No processes retrieved from NVCF, skipping process update")
            return

        for processes in self._active_processes.values():
            for process in processes:
                function_id, version_id, _ = process._process.pid.split(":")
                process_id = f"{function_id}:{version_id}"
                status = list_functions_dict.get(process_id, {}).get("status")

                self.update_process(process=process, status=status)

    async def monitor_processes(self):
        await self.update_processes()
        return await super().monitor_processes()
