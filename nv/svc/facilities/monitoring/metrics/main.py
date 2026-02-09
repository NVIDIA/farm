# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""facilities monitoring metrics facilities."""

import logging

from prometheus_client import start_http_server

from nv.svc.core import main

from .config import MonitoringMetricsConfig
from . import middleware
from . import utils


def start_metrics_server(port=None):
    """Provide metrics registry via a separate http server in daemon thread."""
    registry = utils.get_prometheus_registry()
    logging.info(f"Starting prometheus http server on port {port}")
    start_http_server(port, registry=registry)


class MetricsRuntime:
    """
    Manage the runtime aspects of metrics for the service, including configuration, startup, and shutdown.

    Attributes:
    - _conf: MonitoringMetricsConfig, an instance of MonitoringMetricsConfig for configuration settings.
    - _provider: OTLP meter provider.
    """

    def __init__(self) -> None:
        """Initialize the MetricsRuntime instance with default or configured values for metrics settings."""
        self._conf = MonitoringMetricsConfig()
        self._provider = None

    def on_startup(self):
        """
        Perform actions related to metrics setup during the service startup phase.

        Registers the metrics endpoint and middleware based on configuration settings.
        """
        self._provider = utils.configure_metrics_provider(self._conf)

        main.register_endpoint(
            "get",
            self._conf.metrics_endpoint_path,
            middleware.metrics,
            tags=["metrics"],
            include_in_schema=self._conf.show_metrics_endpoint,
            summary="Returns metrics related to the use of the service.",
        )

        if self._conf.enable_metrics_middleware:
            logging.debug("Enabling metrics middleware.")
            main.get_app().add_middleware(middleware.MetricsMiddleware)

        if self._conf.mount_metrics_endpoint_separate_http_server:
            start_metrics_server(self._conf.separate_http_server_port)

    async def on_shutdown(self):
        """
        Perform cleanup actions during the service shutdown phase.

        Cancels the ongoing metrics provider deregisters the metrics endpoint.
        """
        if self._provider:
            try:
                self._provider.force_flush()
            except Exception:
                pass
            self._provider.shutdown(timeout_millis=1000)

        if self._conf.enable_metrics_middleware:
            main.deregister_endpoint("get", "/metrics")
