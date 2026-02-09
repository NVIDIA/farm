# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""facilities monitoring metrics grpc server interceptor."""

import asyncio
import sys
import time
from inspect import iscoroutine
from typing import Any, Callable

import grpc
from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor.server import AsyncServerInterceptor
from opentelemetry.metrics import Observation

from nv.svc.facilities.monitoring.metrics.config import MonitoringMetricsConfig
from nv.svc.facilities.monitoring.metrics.facilities import MetricsFacility
from nv.svc.facilities.monitoring.metrics.utils import configure_metrics_provider, DEFAULT_INSTANCE_NAME


_COUNT_LOCK = asyncio.Lock()
_ACTIVE_COUNTS = {}


_metrics_facility = MetricsFacility("grpc_server_interceptor")


def _get_active_count_observables(options):
    observations = []
    # Generate observations based on each count.
    for item in _ACTIVE_COUNTS.items():
        (method, instance), count = item
        labels = {"method": method, "instance": instance}
        observations.append(Observation(count, labels))
    return observations


_REQUESTS = _metrics_facility.counter(
    name="grpc_requests_total",
    description="Total amount of requests by method",
    unit="requests"
)

_metrics_facility.observable_gauge(
    name="grpc_requests_active",
    description="Current active requests by method",
    callbacks=_get_active_count_observables,
    unit="requests"
)

_RESPONSES = _metrics_facility.counter(
    name="grpc_requests_responses",
    description="Total amount of responses by method, return code and exception_type",
    unit="responses"
)

_REQUEST_PROCESSING_TIME = _metrics_facility.histogram(
    name="grpc_request_processing_time",
    description="Histogram of request processing time per route in seconds",
    unit="seconds"
)


async def _increment_active_count(method: str, instance: str, amount: int):
    async with _COUNT_LOCK:
        key = (method, instance)
        _ACTIVE_COUNTS[key] = _ACTIVE_COUNTS.get(key, 0) + amount


class MetricsServerInterceptor(AsyncServerInterceptor):
    """An interceptor for gRPC server requests using OpenTelemetry."""

    def __init__(self):
        """Initialize the metrics server interceptor."""
        super().__init__()

        self.conf = MonitoringMetricsConfig()
        configure_metrics_provider(self.conf)
        # NOTE: record 0 to avoid missing metrics per: https://prometheus.io/docs/practices/instrumentation/#avoid-missing-metrics
        _REQUESTS.add(0)
        _RESPONSES.add(0)
        _REQUEST_PROCESSING_TIME.record(0)

    async def _record_metrics(self, start, method_name, labels):
        end = time.perf_counter()

        exc_type, _, _ = sys.exc_info()
        if exc_type is None:
            # no exception, successful request.
            response_labels = labels.copy()
            response_labels["status_code"] = "OK"
            response_labels["exception_type"] = "N/A"
            _RESPONSES.add(1, response_labels)

        await _increment_active_count(method_name, DEFAULT_INSTANCE_NAME, -1)
        _REQUEST_PROCESSING_TIME.record(end - start, labels)

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.aio.ServicerContext,
        method_name: str,
    ) -> Any:
        """
        Intercept the gRPC server request for metrics purposes.

        Args:
            method: Either the RPC method implementation, or the next interceptor in
                the chain.
            request_or_iterator: The RPC request, as a protobuf message if it is a
                unary request, or an iterator of protobuf messages if it is a streaming
                request.
            context: The ServicerContext pass by gRPC to the service.
            method_name: The grpc method name being called.

        Returns:
            Any: The response object or iterator of response objects.
        """
        labels = {"method": method_name, "instance": DEFAULT_INSTANCE_NAME}
        await _increment_active_count(method_name, DEFAULT_INSTANCE_NAME, 1)
        start = time.perf_counter()

        try:
            _REQUESTS.add(1, labels)

            response_or_iterator = method(request_or_iterator, context)

            if hasattr(response_or_iterator, "__aiter__"):
                # Server streaming responses, delegate to an async generator helper.
                # Note that we do NOT await this.
                return self._intercept_streaming(response_or_iterator, context, start, method_name, labels)
            elif iscoroutine(response_or_iterator):
                # Unary, just await and return the response
                return await response_or_iterator
            else:
                return response_or_iterator
        except GrpcException as e:
            context.set_code(e.status_code)
            context.set_details(e.details)
            response_labels = labels.copy()
            response_labels["status_code"] = e.status_string
            response_labels["exception_type"] = str(e.details)
            _RESPONSES.add(1, response_labels)
            raise
        finally:
            await self._record_metrics(start, method_name, labels)

    async def _intercept_streaming(self, iterator, context, start, method_name, labels):
        """
        Intercept the streaming response for tracing purposes.

        Args:
            iterator: An async iterator for the streaming response.
            context: The context object for the RPC.

        Yields:
            Any: The response objects in the streaming response.
        """
        try:
            async for r in iterator:
                yield r
        except GrpcException as e:
            context.set_code(e.status_code)
            context.set_details(e.details)
            raise
        finally:
            await self._record_metrics(start, method_name, labels)
