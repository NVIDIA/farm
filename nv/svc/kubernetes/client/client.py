# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Async Kubernetes Client package."""
from kubernetes_asyncio import client, config, watch
from kubernetes_asyncio.stream import WsApiClient
from kubernetes_asyncio.client.api_client import ApiClient
import kubernetes_asyncio.client.api as client_apis
from nv.svc.core.utils.config import Config
from .config import ServicesCoreConfig
import logging


class KubernetesClient():
    """A Kubernetes client manager thats supports HTTP and WS. The manager takes care of setting up configuration in a standard way.

    The following enable users of this class to not import the underlying package directly
    Attributes:
        apis - Refrence to kubernetees_asyncio.client.api
        watch - Refernce to kubernetes_asyncio.watch
    """

    apis = client_apis
    watch = watch

    def __init__(self, config: Config = None):
        """Initialize settings for clients."""
        if not config:
            config = ServicesCoreConfig()
        else:
            config = config
        self._autoload_in_cluster_k8s_config = config.load_in_cluster_config
        self._verify_ssl = config.verify_ssl
        self._kube_config_path = config.kube_config_path
        self._kube_config_context = config.kube_config_context
        self._kube_config_settings = {}

        # _closed keeps track of whether or not close has been called on the session _close_clients()
        self._closed = False

        if self._kube_config_context:
            self._kube_config_settings['context'] = self._kube_config_context
        if self._kube_config_path:
            self._kube_config_settings['config_file'] = self._kube_config_path

        # These clients are initialized when __aenter__ is called and cannot be done directly (async/await)
        self.api_http = None
        self.api_ws = None

    async def _initialize_clients(self):
        """
        Initialize both an HTTP and WebSocket client using the correct configuration.

        Returns:
            None.
        """
        if self.api_http and self.api_ws and not self._closed:
            logging.debug("Clients are already set, continuing...")
            return

        if self._autoload_in_cluster_k8s_config:
            logging.info("Using the in cluster config for the k8s client.")
            config.load_incluster_config()
        else:
            logging.info("Using kubeconfig for the Kubernetes Clients")
            await config.load_kube_config(**self._kube_config_settings)

        client_config = client.Configuration.get_default_copy()
        client_config.verify_ssl = self._verify_ssl

        self._set_clients(client_config)

    def _set_clients(self, client_config):
        self.api_http = ApiClient(configuration=client_config)
        self.api_ws = WsApiClient(configuration=client_config)
        self._closed = False

    async def _close_clients(self):
        await self.api_http.close()
        await self.api_ws.close()
        self._closed = True

    async def __aenter__(self):
        """Open sessions for clients upon entering with block."""
        await self._initialize_clients()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Close sessions for clients upon exiting with block."""
        await self._close_clients()
