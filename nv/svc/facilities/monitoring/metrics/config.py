# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""facilities monitoring metrics config."""

from nv.svc.core.utils.config import Config, setting

PACKAGE_NAME = "nv.svc.facilities.monitoring.metrics"


@setting(
    "mount_metrics_endpoint_separate_http_server",
    default=False,
    cast=bool,
    description="Additonally mount the metrics registry endpoint on a separate prometheus http server.",
)
@setting(
    "separate_http_server_port",
    default=8081,
    cast=int,
    description="Port to use for the separate http server if enabled.",
)
@setting(
    "metrics_endpoint_path",
    default="/metrics",
    description="Path to mount the prometheus endpoint.",
)
@setting(
    "enable_metrics_middleware",
    default=True,
    cast=bool,
    description="Enable the metrics middleware.",
)
@setting(
    "show_metrics_endpoint",
    default=True,
    cast=bool,
    description="Configures /metrics endpoint and returns prometheus formatted metrics related to the use of the service.",
)
@setting(
    "export_metrics_to_collector",
    default=False,
    cast=bool,
    description="Enable/Disable exporting metrics to the OTLP Collector.",
)
@setting(
    "export_metrics_to_console",
    default=False,
    cast=bool,
    description="Enable/Disable exporting metrics to STDOUT.",
)
@setting(
    "secure",
    default=False,
    cast=bool,
    description="Enable/Disable secure connection with OTLP Collector.",
)
@setting(
    "collector_url",
    default="opentelemetry.ov.local:8443",
    description="The OTLP Collector URL.",
)
@setting(
    "export_interval_s",
    default=10,
    cast=int,
    description="Specify the export interval in seconds.",
)
def MonitoringMetricsConfig(*validators) -> Config:
    """Service monitoring metrics facility configuration settings."""
    return Config(package_name=PACKAGE_NAME, validators=list(validators), raise_on_package_not_found_error=False)
