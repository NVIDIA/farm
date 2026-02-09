# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""facilities monitoring metrics utils."""

import logging
import os
import socket

from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import \
    OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (ConsoleMetricExporter,
                                              PeriodicExportingMetricReader)
import prometheus_client as prometheus
from prometheus_client import multiprocess

from .config import MonitoringMetricsConfig


DEFAULT_INSTANCE_NAME = f"{socket.getfqdn()}-{os.getpid()}"


def configure_metrics_provider(conf: MonitoringMetricsConfig):
    """Configure the metrics provider by adding the otlp and console readers if enabled."""
    export_interval_millis = conf.export_interval_s * 1000
    logging.debug(f"OTLP Collector Endpoint: {conf.collector_url} is secure: {conf.secure}")

    # By default include the PrometheusMetricReader (which uses a custom collector)
    #  so that the `/metrics` endpoint is still able to return metrics from the prometheus registry in prometheus format.
    metric_readers = [PrometheusMetricReader()]

    if conf.export_metrics_to_collector:
        # configure the OTLP exporter with the Collector endpoint.
        insecure = True
        if conf.secure:
            insecure = False
        otlp_exporter = OTLPMetricExporter(endpoint=conf.collector_url, insecure=insecure)
        otlp_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=export_interval_millis)
        metric_readers.append(otlp_reader)

    if conf.export_metrics_to_console:
        console_exporter = ConsoleMetricExporter()
        console_reader = PeriodicExportingMetricReader(console_exporter, export_interval_millis=export_interval_millis)
        metric_readers.append(console_reader)

    provider = MeterProvider(metric_readers=metric_readers)
    set_meter_provider(provider)
    return provider


def get_prometheus_registry():
    """Retrieve the prometheus registry for metrics."""
    if "prometheus_multiproc_dir" in os.environ:
        registry = prometheus.CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = prometheus.REGISTRY
    return registry
