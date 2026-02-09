# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""HttpClientSession."""

from typing import Optional, Tuple

import aiohttp
from asgi_correlation_id import context

from ..config import ServicesCoreConfig


_services_core_conf = None


def _load_services_core_conf():
    # helper, load conf once and cache.
    global _services_core_conf
    if _services_core_conf is None:
        _services_core_conf = ServicesCoreConfig()
    return _services_core_conf


def _get_current_traceparent_tracestate() -> Tuple[Optional[str], Optional[str]]:
    # delay import in case its not a dependency
    try:
        import omni.trace as trace
    except ImportError:
        return None, None

    active_stack_span = trace.get_active_stack_span()
    if active_stack_span is not None:
        # NOTE: traceparent can be empty string if the `active_stack_span` is a null span
        traceparent = active_stack_span.get_otlp_traceparent_value()
        tracestate = active_stack_span.get_otlp_tracestate_value()
        return (traceparent if traceparent else None, tracestate if tracestate else None)
    return (None, None)


class HTTPClientSession(aiohttp.ClientSession):
    """HTTP Client Session with tracing headers."""

    def __init__(self, *args, **kwargs):
        """Initialize the class to use for the HTTP header."""
        super().__init__(*args, **kwargs)

        self.__conf = _load_services_core_conf()
        self.__default_headers = kwargs.get("headers", {})

    async def _request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        # update the default_headers
        self._add_tracing_headers()
        self._add_correlation_id_header()
        # update with main headers for the request.
        headers.update(self.__default_headers)
        kwargs["headers"] = headers
        return await super()._request(method, url, *args, **kwargs)

    def _add_tracing_headers(self):
        traceparent, tracestate = _get_current_traceparent_tracestate()
        if traceparent:
            self.__default_headers["traceparent"] = traceparent
        if tracestate:
            self.__default_headers["tracestate"] = tracestate

    def _add_correlation_id_header(self):
        header_name = self.__conf.correlation_id.header_name
        correlation_id = context.correlation_id.get()
        if correlation_id:
            self.__default_headers[header_name] = correlation_id
