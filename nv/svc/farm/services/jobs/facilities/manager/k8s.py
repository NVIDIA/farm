# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Kubernetes Manager Facility."""

__all__ = ["ProcessManager"]

import asyncio
from datetime import datetime, timezone
import functools
import json
import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

from kubernetes_asyncio.client import models

from nv.svc.kubernetes.client import KubernetesClient

from nv.svc.farm.services.jobs.job_types.base import BaseJob
from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore
from nv.svc.farm.services.jobs.facilities.manager.base import (
    BaseInstance,
    BaseRemoteProcess,
    ProcessManager,
)


class K8sFarmClientManager(KubernetesClient):
    def __init__(
            self,
            ttl_seconds_after_finished: Optional[int] = 300,
            job_template_spec_overrides_file: Optional[str] = None,
            container_spec_overrides_file: Optional[str] = None,
            request_timeout: Optional[int] = 5,
            namespace: Optional[str] = "default",
            list_jobs_limit_per_page: int = 250):
        """K8s farm client manager constructor.

        Args:
            ttl_seconds_after_finished (int): Time in seconds to remove job after finished.
            job_template_spec_overrides_file (Optional[str]): File containing override data for the Job `spec.template.spec`.
            container_spec_overrides_file (Optional[str]): File containing override data for the Job `spec.template.spec.containers`.
            request_timeout (int): Timeout during which to wait after submitting a request (in seconds).
            namespace (str): Namespace to use for the jobs.
            list_jobs_limit_per_page (int): Maximum number of jobs to return per page when listing jobs.
        """

        super().__init__()
        self._async_req = True
        self._job_template_spec_overrides = _load_json_file(job_template_spec_overrides_file)
        self._container_spec_overrides = _load_json_file(container_spec_overrides_file)
        self._ttl_seconds_after_finished = ttl_seconds_after_finished
        self.__request_timeout = request_timeout
        self._namespace = namespace
        self._list_jobs_limit_per_page = list_jobs_limit_per_page

    def initialize_clients(func):
        """initialize_clients.

        This decorator will automatically initialize clients
        """

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            await self._initialize_clients()
            return await func(self, *args, **kwargs)
        return wrapper

    @initialize_clients
    async def get_job_status(self, name, **kwargs) -> dict:
        """
        Read the specified Job by name and returns its status.

        If all attr within the v1.status object are None. Returns a dict with status set to None

        async_req=True is passed to all requests

        :param name: name of the Job (required)
        :type name: str
        :param namespace: namespace name V1Job exists in, global is used if not set
        :type namespace: str
        :param _request_timeout: total request timeout if set, else uses global client setting
        :return: Result Object
        :rtype: dict
        """
        kwargs, namespace = self.set_common_args(kwargs)
        http_batch_v1 = self.apis.BatchV1Api(self.api_http)
        result = await http_batch_v1.read_namespaced_job_status(name=name,
                                                                namespace=namespace,
                                                                **kwargs).get()
        result = {"status": None} if result.status == models.V1JobStatus() else result.to_dict(serialize=True)
        return result

    def _map_k8s_job_status_to_string(self, job_status: models.V1JobStatus) -> Optional[str]:
        """
        Map Kubernetes V1JobStatus to a simplified status string.

        :param job_status: Kubernetes job status object
        :type job_status: models.V1JobStatus
        :return: Status string ("Starting", "Succeeded", "Failed", "Running") or None
        :rtype: Optional[str]
        """
        if job_status == models.V1JobStatus():
            return "Starting"
        # Note: succeeded, failed, active, and ready are counts of pods in those states.
        # We compare to 1 because our job spec creates exactly 1 pod per job.
        elif job_status.succeeded == 1:
            return "Succeeded"
        elif job_status.failed == 1:
            return "Failed"
        elif job_status.active == 1:
            # Check if the pod is actually ready before marking as Running.
            # The ready field was added in Kubernetes 1.24+ (April 2022).
            # If ready is None (older K8s) or not 1, the pod is not ready yet.
            if job_status.ready == 1:
                return "Running"
            # Pod is active but not ready (waiting for scheduling, resources, etc.)
            return "Starting"
        else:
            return None

    @initialize_clients
    async def get_jobs_status_bulk(self, **kwargs) -> Dict[str, Optional[str]]:
        """
        Read all Jobs in the namespace and returns their statuses in bulk.

        Uses list_namespaced_job to efficiently retrieve all job statuses with automatic pagination.
        The status extraction logic maps Kubernetes job status to a simplified status string.

        Note: This retrieves all jobs in the namespace because the Kubernetes API does not support
        filtering by a set of job names. It can only return all jobs or filter by a single job name.

        :param kwargs: Optional arguments (e.g., limit for max results per page, _request_timeout for timeout)
        :return: Dictionary mapping job names to their status strings ("Succeeded", "Failed", "Running", or None)
        :rtype: Dict[str, Optional[str]]
        """
        kwargs, namespace = self.set_common_args(kwargs)
        http_batch_v1 = self.apis.BatchV1Api(self.api_http)

        jobs_status_dict = {}

        # Set pagination limit
        kwargs["limit"] = self._list_jobs_limit_per_page

        # Handle pagination to retrieve all jobs in namespace
        while True:
            result = await http_batch_v1.list_namespaced_job(namespace=namespace, **kwargs).get()

            # Extract status for all jobs
            for job in result.items:
                job_name = job.metadata.name
                jobs_status_dict[job_name] = self._map_k8s_job_status_to_string(job.status)

            # Check if we need to continue pagination
            if not result.metadata._continue:
                break

            # Set continue token for next page
            kwargs["_continue"] = result.metadata._continue

        return jobs_status_dict

    @initialize_clients
    async def delete_job(self, name: str, **kwargs) -> models.V1Status:
        """
        Delete a V1Job.

        async_req=True is passed to all requests

        :param name: name of the Job (required)
        :type name: str
        :param namespace name V1Job exists in, global is used if not set
        :type namespace: str
        :param _request_timeout: total request timeout if set, else uses global client setting
        :return: Returns V1Status the result object.
        :rtype: V1Status
        """
        kwargs, namespace = self.set_common_args(kwargs)

        # set extra args
        kwargs["propagation_policy"] = "Background"
        http_batch_v1 = self.apis.BatchV1Api(self.api_http)
        return await http_batch_v1.delete_namespaced_job(name=name,
                                                         namespace=namespace,
                                                         **kwargs).get()

    @initialize_clients
    async def retrieve_job(self, task_id: str, **kwargs) -> Optional[str]:
        """
        Retrieve job name of a given task, by using the task_id to filter by label selector.

        async_req=True is passed to all requests
        :param task_id: the id of a Farm task
        :type task_id: str
        :param namespace: namespace name V1Job exists in, global is used if not set
        :type namespace: str
        :param _request_timeout: total request timeout if set, else uses global client setting
        :return: Returns the Job name of a given task_id.
        :rtype: str
        """
        kwargs, namespace = self.set_common_args(kwargs)

        # set extra args
        kwargs["label_selector"] = f"ov-farm={task_id}"

        http_core_v1 = self.apis.CoreV1Api(self.api_http)
        pod_list = await http_core_v1.list_namespaced_pod(namespace=namespace, **kwargs).get()
        if not pod_list.items:
            logging.error(f"Failed to find pods for task {task_id}")
            return None
        return pod_list.items[0].metadata.labels.get("job-name")

    @initialize_clients
    async def get_job_logs(self, name: str, latest_timestamp: str, **kwargs) -> str:
        """
        Read log of the specified Job.

        By selecting the jobs pod by name, namespace,
        and latest_timestamp to retrieve from
        This method passes async_req=True to all requests
        :param name: name of the Pod (required)
        :type name: str
        :param latest_timestamp: the timestamp to get the logs from
        :type latest_timestamp: ISO string, see date.isoformat()
        :param timestamps: If true, add an RFC3339 or RFC3339Nano timestamp at the beginning of every line of log output. Defaults to false.
        :type timestamps: bool
        :param namespace: namespace name V1Job exists in, global is used if not set
        :type namespace: str
        :param _request_timeout: total request timeout if set, else uses global client setting
        :return: Returns the logs as str
        :rtype: str
        """

        http_core_v1 = self.apis.CoreV1Api(self.api_http)
        since_time = datetime.fromisoformat(latest_timestamp)

        # Calculate the time difference between the current time and since_time
        time_difference = datetime.now(timezone.utc) - since_time

        # Extract the total seconds from the time difference, if this is 0 or less we cannot retrieve logs yet
        since_seconds = int(time_difference.total_seconds())
        if since_seconds <= 0:
            logging.debug(f"Retreiving logs from up to {str(since_seconds)} ago from {str(since_time)}")
            return ""
        kwargs, namespace = self.set_common_args(kwargs)

        pod_list_kwargs = dict(kwargs)
        pod_list_kwargs["label_selector"] = f"job-name={name}"
        pod_list = await http_core_v1.list_namespaced_pod(namespace=namespace,
                                                          **pod_list_kwargs).get()
        if not pod_list.items:
            logging.error(f"Failed to find pods for job {name}")
            return ""
        pod_log_kwargs = dict(kwargs)
        pod_log_kwargs["pretty"] = True
        pod_log_kwargs["since_seconds"] = since_seconds
        return await http_core_v1.read_namespaced_pod_log(namespace=namespace,
                                                          name=pod_list.items[0].metadata.name,
                                                          **pod_log_kwargs).get()

    @initialize_clients
    async def create_job(
        self,
        # container spec fields
        container_image: str,
        name: str,
        args: Optional[List[str]] = None,
        command: Optional[List[str]] = None,
        labels: Optional[Dict] = None,
        env: Optional[List[Dict]] = None,
        env_from: Optional[List[Dict]] = None,
        image_pull_policy: Optional[str] = None,
        lifecycle: Optional[Dict] = None,
        liveness_probe: Optional[Dict] = None,
        ports: Optional[List[Dict]] = None,
        readiness_probe: Optional[Dict] = None,
        resource_limits: Optional[Dict] = None,
        security_context: Optional[Dict] = None,
        startup_probe: Optional[Dict] = None,
        stdin: Optional[bool] = None,
        stdin_once: Optional[bool] = None,
        termination_message_path: Optional[str] = None,
        termination_message_policy: Optional[str] = None,
        tty: Optional[bool] = None,
        volume_devices: Optional[List[Dict]] = None,
        volume_mounts: Optional[List[Dict]] = None,
        working_dir: Optional[str] = None,
        container_spec_field_overrides: Optional[Dict] = None,
        # pod spec fields
        active_deadline_seconds: Optional[int] = None,
        affinity: Optional[Dict] = None,
        automount_service_account_token: Optional[bool] = None,
        dns_config: Optional[Dict] = None,
        dns_policy: Optional[str] = None,
        enable_service_links: Optional[bool] = None,
        ephemeral_containers: Optional[List[Dict]] = None,
        host_aliases: Optional[List[Dict]] = None,
        host_IPC: Optional[bool] = None,
        host_network: Optional[bool] = None,
        host_PID: Optional[bool] = None,
        hostname: Optional[str] = None,
        image_pull_secrets: Optional[List[Dict]] = None,
        init_containers: Optional[List[Dict]] = None,
        node_name: Optional[str] = None,
        node_selector: Optional[Dict] = None,
        os: Optional[Dict] = None,
        overhead: Optional[Dict] = None,
        preemption_policy: Optional[str] = None,
        priority: Optional[int] = None,
        priority_class_name: Optional[str] = None,
        readiness_gates: Optional[List[Dict]] = None,
        runtime_class_name: Optional[str] = None,
        scheduler_name: Optional[str] = None,
        pod_security_context: Optional[Dict] = None,
        service_account: Optional[str] = None,
        service_account_name: Optional[str] = None,
        set_hostname_as_FQDN: Optional[bool] = None,
        share_process_namespace: Optional[bool] = None,
        subdomain: Optional[str] = None,
        termination_grace_period_seconds: Optional[int] = None,
        tolerations: Optional[List[Dict]] = None,
        topology_spread_constraints: Optional[List[Dict]] = None,
        volumes: Optional[List[Dict]] = None,
        pod_spec_field_overrides: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Launch a new job.

        :param _request_timeout: total request timeout if set, else uses global client setting
        :return models.V1Job
        """
        kwargs, namespace = self.set_common_args(kwargs)
        http_batch_v1 = self.apis.BatchV1Api(self.api_http)
        resources = {}
        if resource_limits:
            # set limits and requests the same for guaranteed resources.
            resources["limits"] = resource_limits
            resources["requests"] = resource_limits

        labels = labels or {}
        args = args or []
        body = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": name,
                "labels": labels
            },
            "spec": {
                "backoffLimit": 0,
                "template": {
                    "metadata": {
                        "labels": labels
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": container_image,
                                "command": command,
                                "args": args
                            }
                        ],
                        "restartPolicy": "Never",
                        "backoffLimit": 0,
                        "parallelism": 1,
                        "completions": 1
                    }
                }
            }
        }
        if self._ttl_seconds_after_finished is not None:
            body["spec"]["ttlSecondsAfterFinished"] = self._ttl_seconds_after_finished

        if self._job_template_spec_overrides is not None:
            body["spec"]["template"]["spec"].update(self._job_template_spec_overrides)

        for container_spec in body["spec"]["template"]["spec"]["containers"]:
            # NOTE: supplied resource_limits takes precedence over the container_spec_overrides.
            if self._container_spec_overrides is not None:
                container_spec.update(self._container_spec_overrides)

            if env is not None:
                container_spec["env"] = env

            if env_from is not None:
                container_spec["envFrom"] = env_from

            if image_pull_policy is not None:
                container_spec["imagePullPolicy"] = image_pull_policy

            if lifecycle is not None:
                container_spec["lifecycle"] = lifecycle

            if liveness_probe is not None:
                container_spec["livenessProbe"] = liveness_probe

            if ports is not None:
                container_spec["ports"] = ports

            if readiness_probe is not None:
                container_spec["readinessProbe"] = readiness_probe

            if resources:
                container_spec["resources"] = resources

            if security_context is not None:
                container_spec["securityContext"] = security_context

            if startup_probe is not None:
                container_spec["startupProbe"] = startup_probe

            if stdin is not None:
                container_spec["stdin"] = stdin

            if stdin_once is not None:
                container_spec["stdinOnce"] = stdin_once

            if termination_message_path is not None:
                container_spec["terminationMessagePath"] = termination_message_path

            if termination_message_policy is not None:
                container_spec["terminationMessagePolicy"] = termination_message_policy

            if tty is not None:
                container_spec["tty"] = tty

            if volume_devices is not None:
                container_spec["volumeDevices"] = volume_devices

            if volume_mounts is not None:
                container_spec["volumeMounts"] = volume_mounts

            if working_dir is not None:
                container_spec["workingDir"] = working_dir

            if container_spec_field_overrides is not None:
                # allow specifying custom fields as a safeguard for fields added to the spec in the future
                container_spec.update(container_spec_field_overrides)

        if active_deadline_seconds is not None:
            body["spec"]["template"]["spec"]["activeDeadlineSeconds"] = active_deadline_seconds

        if affinity is not None:
            body["spec"]["template"]["spec"]["affinity"] = affinity

        if automount_service_account_token is not None:
            body["spec"]["template"]["spec"]["automountServiceAccountToken"] = automount_service_account_token

        if dns_config is not None:
            body["spec"]["template"]["spec"]["dnsConfig"] = dns_config

        if dns_policy is not None:
            body["spec"]["template"]["spec"]["dnsPolicy"] = dns_policy

        if enable_service_links is not None:
            body["spec"]["template"]["spec"]["enableServiceLinks"] = enable_service_links

        if ephemeral_containers is not None:
            body["spec"]["template"]["spec"]["ephemeralContainers"] = ephemeral_containers

        if host_aliases is not None:
            body["spec"]["template"]["spec"]["hostAliases"] = host_aliases

        if host_IPC is not None:
            body["spec"]["template"]["spec"]["hostIPC"] = host_IPC

        if host_network is not None:
            body["spec"]["template"]["spec"]["hostNetwork"] = host_network

        if host_PID is not None:
            body["spec"]["template"]["spec"]["hostPID"] = host_PID

        if hostname is not None:
            body["spec"]["template"]["spec"]["hostname"] = hostname

        if image_pull_secrets is not None:
            body["spec"]["template"]["spec"]["imagePullSecrets"] = image_pull_secrets

        if init_containers is not None:
            body["spec"]["template"]["spec"]["initContainers"] = init_containers

        if node_name is not None:
            body["spec"]["template"]["spec"]["nodeName"] = node_name

        if node_selector is not None:
            body["spec"]["template"]["spec"]["nodeSelector"] = node_selector

        if os is not None:
            body["spec"]["template"]["spec"]["os"] = os

        if overhead is not None:
            body["spec"]["template"]["spec"]["overhead"] = overhead

        if preemption_policy is not None:
            body["spec"]["template"]["spec"]["preemptionPolicy"] = preemption_policy

        if priority is not None:
            body["spec"]["template"]["spec"]["priority"] = priority

        if priority_class_name is not None:
            body["spec"]["template"]["spec"]["priorityClassName"] = priority_class_name

        if readiness_gates is not None:
            body["spec"]["template"]["spec"]["readinessGates"] = readiness_gates

        if runtime_class_name is not None:
            body["spec"]["template"]["spec"]["runtimeClassName"] = runtime_class_name

        if scheduler_name is not None:
            body["spec"]["template"]["spec"]["schedulerName"] = scheduler_name

        if pod_security_context is not None:
            body["spec"]["template"]["spec"]["securityContext"] = pod_security_context

        if service_account is not None:
            body["spec"]["template"]["spec"]["serviceAccount"] = service_account

        if service_account_name is not None:
            body["spec"]["template"]["spec"]["serviceAccountName"] = service_account_name

        if set_hostname_as_FQDN is not None:
            body["spec"]["template"]["spec"]["setHostnameAsFQDN"] = set_hostname_as_FQDN

        if share_process_namespace is not None:
            body["spec"]["template"]["spec"]["shareProcessNamespace"] = share_process_namespace

        if subdomain is not None:
            body["spec"]["template"]["spec"]["subdomain"] = subdomain

        if termination_grace_period_seconds is not None:
            body["spec"]["template"]["spec"]["terminationGracePeriodSeconds"] = termination_grace_period_seconds

        if tolerations is not None:
            body["spec"]["template"]["spec"]["tolerations"] = tolerations

        if topology_spread_constraints is not None:
            body["spec"]["template"]["spec"]["topologySpreadConstraints"] = topology_spread_constraints

        if volumes is not None:
            body["spec"]["template"]["spec"]["volumes"] = volumes

        if pod_spec_field_overrides is not None:
            # allow specifying custom fields as a safeguard for fields added to the spec in the future
            body["spec"]["template"]["spec"].update(pod_spec_field_overrides)

        return await http_batch_v1.create_namespaced_job(namespace=namespace,
                                                         body=body,
                                                         **kwargs).get()

    def set_common_args(self, kwargs):
        """
        Set common kwargs sent to all requests.

        Removes and returns "namespace" as it is a positional arg
        """
        if "async_req" not in kwargs:
            kwargs["async_req"] = self._async_req
        if "request_timeout" not in kwargs:
            kwargs["_request_timeout"] = self.__request_timeout
        namespace = kwargs.pop("namespace", self._namespace)
        return kwargs, namespace


def _load_json_file(filepath: str) -> Dict:
    data = None
    if filepath:
        try:
            with open(filepath, mode="r", encoding="utf-8") as fp:
                data = json.load(fp)
        except Exception as exc:
            raise RuntimeError(f"Failed to load JSON data from '{filepath}'. {str(exc)}")
    return data


class K8sInstance(BaseInstance):

    def __init__(
        self,
        k8s_manager: K8sFarmClientManager,
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
        self._k8s_client_mgr = k8s_manager

        self._active_check_delay = self._settings.k8s_manager.active_check_delay
        self._log_check_delay = self._settings.k8s_manager.log_check_delay
        self._latest_log_time = datetime.now(timezone.utc).isoformat()

    def spawn(self):
        raise NotImplementedError("The K8sInstances cannot be spawned in a threaded mode")

    async def retrieve_async(self, task_id: str):
        self._stop = asyncio.Event()
        try:
            process_id = await self._k8s_client_mgr.retrieve_job(task_id)
        except Exception as exc:
            logging.error(f'Failed to get job from k8s for "{task_id}": {str(exc)}')

        if process_id is None:
            raise Exception(f'Failed to retrieve job for the task "{task_id}"')

        self._process = BaseRemoteProcess(process_id)
        # Note that we also reconcile a "starting" task. Here we are marking it as running.
        self._process.set_status("running")
        self._log_listener_thread = asyncio.ensure_future(self._install_log_listeners())
        return self._process

    async def spawn_async(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        self._stop = asyncio.Event()

        metadata = metadata or {}
        requirements = requirements or {}

        # retrieve container spec fields, optionally retrieve camelcase if exists
        # NOTE: attempt to retrieve env and working_dir from the top-level job definition fields, otherwise retrieve from capacity_requirements

        env = None
        if self._env is not None and len(self._env):
            # convert env dict to k8s env list of dicts.
            # merge with env values provided via requirements
            requirements_env = requirements.get("env", [])
            # retrieve all requirements.env names, and ensure they take precedence over self._env
            keys = [e["name"].lower() for e in requirements_env if "name" in e]
            env = [{"name": k, "value": v} for k, v in self._env.items() if k.lower() not in keys]
            env.extend(requirements_env)
        else:
            env = requirements.get("env")

        env_from = requirements.get("env_from", requirements.get("envFrom"))
        image_pull_policy = requirements.get("image_pull_policy", requirements.get("imagePullPolicy"))
        lifecycle = requirements.get("lifecycle")
        liveness_probe = requirements.get("liveness_probe", requirements.get("livenessProbe"))
        ports = requirements.get("ports")
        readiness_probe = requirements.get("readiness_probe", requirements.get("readinessProbe"))
        resource_limits = requirements.get("resource_limits", requirements.get("resourceLimits", requirements.get("resources")))
        security_context = requirements.get("security_context", requirements.get("securityContext"))
        startup_probe = requirements.get("startup_probe", requirements.get("startupProbe"))
        stdin = requirements.get("stdin")
        stdin_once = requirements.get("stdin_once", requirements.get("stdinOce"))
        termination_message_path = requirements.get("termination_message_path", requirements.get("terminationMessagePath"))
        termination_message_policy = requirements.get("termination_message_policy", requirements.get("terminationMessagePolicy"))
        tty = requirements.get("tty")
        volume_devices = requirements.get("volume_devices", requirements.get("volumeDevices"))
        volume_mounts = requirements.get("volume_mounts", requirements.get("volumeMounts"))
        working_dir = self._working_directory or requirements.get("working_dir", requirements.get("workingDir"))
        container_spec_field_overrides = requirements.get("container_spec_field_overrides", requirements.get("containerSpecFieldOverrides"))

        # pod spec fields
        active_deadline_seconds = requirements.get("active_deadline_seconds", requirements.get("activeDeadlineSeconds"))
        affinity = requirements.get("affinity")
        automount_service_account_token = requirements.get("automount_service_account_token", requirements.get("automountServiceAccountToken"))
        dns_config = requirements.get("dns_config", requirements.get("dnsConfig"))
        dns_policy = requirements.get("dns_policy", requirements.get("dnsPolicy"))
        enable_service_links = requirements.get("enable_service_links", requirements.get("enableServiceLinks"))
        ephemeral_containers = requirements.get("ephemeral_containers", requirements.get("ephemeralContainers"))
        host_aliases = requirements.get("host_aliases", requirements.get("hostAliases"))
        host_IPC = requirements.get("host_IPC", requirements.get("hostIPC"))
        host_network = requirements.get("host_network", requirements.get("hostNetwork"))
        host_PID = requirements.get("host_PID", requirements.get("hostPID"))
        hostname = requirements.get("hostname")
        image_pull_secrets = requirements.get("image_pull_secrets", requirements.get("imagePullSecrets"))
        init_containers = requirements.get("init_containers", requirements.get("initContainers"))
        node_name = requirements.get("node_name", requirements.get("nodeName"))
        node_selector = requirements.get("node_selector", requirements.get("nodeSelector"))
        os = requirements.get("os")
        overhead = requirements.get("overhead")
        preemption_policy = requirements.get("preemption_policy", requirements.get("preemptionPolicy"))
        priority = requirements.get("priority")
        priority_class_name = requirements.get("priority_class_name", requirements.get("priorityClassName"))
        readiness_gates = requirements.get("readiness_gates", requirements.get("readinessGates"))
        runtime_class_name = requirements.get("runtime_class_name", requirements.get("runtimeClassName"))
        scheduler_name = requirements.get("scheduler_name", requirements.get("schedulerName"))
        pod_security_context = requirements.get("pod_security_context", requirements.get("podSecurityContext"))
        service_account = requirements.get("service_account", requirements.get("serviceAccount"))
        service_account_name = requirements.get("service_account_name", requirements.get("serviceAccountName"))
        set_hostname_as_FQDN = requirements.get("set_hostname_as_FQDN", requirements.get("setHostnameAsFQDN"))
        share_process_namespace = requirements.get("share_process_namespace", requirements.get("shareProcessNamespace"))
        subdomain = requirements.get("subdomain")
        termination_grace_period_seconds = requirements.get("termination_grace_period_seconds", requirements.get("terminationGracePeriodSeconds"))
        tolerations = requirements.get("tolerations")
        topology_spread_constraints = requirements.get("topology_spread_constraints", requirements.get("topologySpreadConstraints"))
        volumes = requirements.get("volumes")
        pod_spec_field_overrides = requirements.get("pod_spec_field_overrides", requirements.get("podSpecFieldOverrides"))

        labels = {
            "ov-farm": self._task_id,  # used in retrieve_job in the manager.
            "farm-task-id": self._task_id,
        }
        req_labels = requirements.get("labels")
        if req_labels:
            labels.update(req_labels)

        if not isinstance(self._command, list):
            self._command = [self._command]

        kwargs = {}
        if self._command:
            kwargs["entry_point"] = self._command

        job_name = f"{self._task_id}--{str(uuid.uuid4())[-4:]}"

        job_kwargs = dict(
            container_image=self._container_image,
            name=job_name,
            command=self._command,
            args=self._args,
            labels=labels,
            env=env,
            env_from=env_from,
            image_pull_policy=image_pull_policy,
            lifecycle=lifecycle,
            liveness_probe=liveness_probe,
            ports=ports,
            readiness_probe=readiness_probe,
            resource_limits=resource_limits,
            security_context=security_context,
            startup_probe=startup_probe,
            stdin=stdin,
            stdin_once=stdin_once,
            termination_message_path=termination_message_path,
            termination_message_policy=termination_message_policy,
            tty=tty,
            volume_devices=volume_devices,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
            container_spec_field_overrides=container_spec_field_overrides,
            # pod spec fields
            active_deadline_seconds=active_deadline_seconds,
            affinity=affinity,
            automount_service_account_token=automount_service_account_token,
            dns_config=dns_config,
            dns_policy=dns_policy,
            enable_service_links=enable_service_links,
            ephemeral_containers=ephemeral_containers,
            host_aliases=host_aliases,
            host_IPC=host_IPC,
            host_network=host_network,
            host_PID=host_PID,
            hostname=hostname,
            image_pull_secrets=image_pull_secrets,
            init_containers=init_containers,
            node_name=node_name,
            node_selector=node_selector,
            os=os,
            overhead=overhead,
            preemption_policy=preemption_policy,
            priority=priority,
            priority_class_name=priority_class_name,
            readiness_gates=readiness_gates,
            runtime_class_name=runtime_class_name,
            scheduler_name=scheduler_name,
            pod_security_context=pod_security_context,
            service_account=service_account,
            service_account_name=service_account_name,
            set_hostname_as_FQDN=set_hostname_as_FQDN,
            share_process_namespace=share_process_namespace,
            subdomain=subdomain,
            termination_grace_period_seconds=termination_grace_period_seconds,
            tolerations=tolerations,
            topology_spread_constraints=topology_spread_constraints,
            volumes=volumes,
            pod_spec_field_overrides=pod_spec_field_overrides,)

        await self._k8s_client_mgr.create_job(**job_kwargs)
        self._process = BaseRemoteProcess(process_id=job_name)
        self._log_listener_thread = asyncio.ensure_future(self._install_log_listeners())
        return self._process

    async def _retrieve_job_logs(self) -> None:
        try:
            logs = await self._get_latest_logs()
            if logs:
                self._on_stdout_message(logs)
        except Exception as exc:
            logging.warning(f"Failed to retrieve logs for {self._process.pid}: {str(type(exc))}, {str(exc)}")

    async def _install_log_listeners(self) -> None:
        while self.returncode is None:
            await self._retrieve_job_logs()
            await asyncio.sleep(self._log_check_delay)

    async def _get_latest_logs(self) -> str:
        logs = await self._k8s_client_mgr.get_job_logs(name=self._process.pid, latest_timestamp=self._latest_log_time)
        self._latest_log_time = datetime.now(timezone.utc).isoformat()
        return logs

    async def stop_async(self):
        try:
            await self._k8s_client_mgr.delete_job(name=self._process.pid)
            await self._k8s_client_mgr._close_clients()
        except Exception as exc:
            logging.error(f"Unable to terminate job {str(type(exc))} {str(exc)}")
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


class KubernetesProcessManager(ProcessManager):
    """Start, monitor and manage Kubernetes jobs."""

    _instance_type_cls = K8sInstance

    def __init__(
        self,
        job_store: BaseJobStore,
        log_upload_interval: int = 10,
        log_upload_endpoint: str = "http://127.0.0.1:8011/queue/management/logs/upload",
        jobs_namespace: str = None,
        request_timeout_in_seconds: int = None,
        ttl_seconds_after_finished: int = None,
        job_template_spec_overrides_file: str = None,
        container_spec_overrides_file: str = None,
        list_jobs_limit_per_page: int = 250,
        log_check_delay: int = 15,
    ):
        super().__init__(job_store, log_upload_interval, log_upload_endpoint)

        k8s_manager_settings = self._settings.get("k8s_manager") or {}
        # TODO: fix setting mess later.

        self._log_upload_interval = k8s_manager_settings.get("log_upload_interval") or log_upload_interval
        self._log_upload_endpoint = k8s_manager_settings.get("log_upload_endpoint") or log_upload_endpoint

        namespace = jobs_namespace or k8s_manager_settings.get("jobs_namespace")
        timeout = request_timeout_in_seconds or k8s_manager_settings.get("request_timeout_in_seconds")
        ttl_seconds_after_finished = ttl_seconds_after_finished or k8s_manager_settings.get("ttl_seconds_after_finished")
        job_template_spec_overrides_file = job_template_spec_overrides_file or k8s_manager_settings.get("job_template_spec_overrides_file")
        container_spec_overrides_file = container_spec_overrides_file or k8s_manager_settings.get("container_spec_overrides_file")
        list_jobs_limit_per_page = list_jobs_limit_per_page or k8s_manager_settings.get("list_jobs_limit_per_page")
        self._log_check_delay = log_check_delay or k8s_manager_settings.get("log_check_delay")

        self._k8s_client_mgr = K8sFarmClientManager(
            job_template_spec_overrides_file=job_template_spec_overrides_file,
            container_spec_overrides_file=container_spec_overrides_file,
            request_timeout=timeout,
            namespace=namespace,
            ttl_seconds_after_finished=ttl_seconds_after_finished,
            list_jobs_limit_per_page=list_jobs_limit_per_page
        )

    def _create_instance_from_job(self, job: BaseJob, task_id: str = None) -> K8sInstance:
        return self._instance_type_cls(
            self._k8s_client_mgr,
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

    def update_process(self, process, status: Optional[str] = None):
        """
        Update a single process based on its status.

        Note: Final log retrieval for terminal states (Succeeded/Failed) is handled asynchronously in _flush_logs for perf reasons.
        """
        if status == "Succeeded":
            logging.info(f"Setting {process._process.pid} to finished")
            process._process.set_returncode(0)
            process._process.set_status("finished")
            return

        if status == "Failed":
            logging.info(f"Setting {process._process.pid} to errored")
            process._process.set_returncode(-1)
            process._process.set_status("errored")
            return

        if status == "Running":
            if process.status != "running":
                process._process.set_status("running")
                logging.info(f"Setting {process._process.pid} to running")
            return

        if status == "Starting":
            if process.status != "starting":
                logging.info(f"Setting {process._process.pid} to starting")
                process._process.set_status("starting")
            return

        # Unmapped state from Kubernetes
        logging.error(f"Unmapped state from Kubernetes: {status}")
        process._process.set_returncode(-1)
        process._process.set_status("errored")

    async def update_processes(self):
        """Update all active processes using bulk job status retrieval."""
        # Check if there are any active processes to update
        active_count = sum(len(processes) for processes in self._active_processes.values())

        if active_count == 0:
            logging.info("Controller has no k8s jobs scheduled, skipping K8s update")
            return

        try:
            bulk_jobs_status = await self._k8s_client_mgr.get_jobs_status_bulk()
        except Exception as e:
            logging.error(f"Error calling Kubernetes API: {e}")
            return

        for processes in self._active_processes.values():
            for process in processes:
                status = bulk_jobs_status.get(process._process.pid)
                self.update_process(process=process, status=status)

    async def _flush_logs(self):
        """
        Batch retrieve final logs for processes that have become inactive.

        This internal function collects all inactive processes from self._active_processes
        and retrieves their logs in parallel before they're removed from active_processes.
        """
        # Collect all inactive processes that are still in active_processes
        inactive_processes = []
        for processes in self._active_processes.values():
            for process in processes:
                if not process.is_active:
                    inactive_processes.append(process)

        if inactive_processes:
            # we need to give enough time to k8s to flush logs to disk.
            await asyncio.sleep(self._log_check_delay)
            await asyncio.gather(*[process._retrieve_job_logs() for process in inactive_processes])

    async def monitor_processes(self):
        """Monitor processes using bulk job status updates."""
        # Update process statuses from Kubernetes
        await self.update_processes()

        # Batch retrieve final logs for processes that became inactive
        await self._flush_logs()

        # Call base class monitor_processes to handle process lifecycle
        result = await super().monitor_processes()

        return result

    async def stop_process_async(self, process_type, process_id, kill=False) -> int:
        process_to_stop, active_processes = self._get_process_to_stop(process_type, process_id)
        if not process_to_stop:
            raise Exception(f"{process_id} not found")

        # On windows kill == terminate but on Unix will ensure a SIGINT is sent
        exit_code = await process_to_stop.kill_async() if kill else await process_to_stop.stop_async()

        active_processes.remove(process_to_stop)
        return exit_code
