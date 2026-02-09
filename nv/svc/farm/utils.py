# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Services Utilities."""

import asyncio
import functools
import inspect
import logging
import os
from pathlib import Path
import time
import typing
from typing import Dict, Any

from fastapi import security, Depends, Request
from platformdirs import PlatformDirs
from starlette import requests, exceptions, status

from nv.svc.core.exceptions import ServicesBaseException

import nv.svc.farm


_GLOBAL_CONFIG_ENVVAR_NAME = "NV__SVC__GLOBAL__CONFIG_FILEPATH"
PLATFORM_DIRS = PlatformDirs("nv-svc-farm", "nvidia")
FARM_USER_DATA_DIR = PLATFORM_DIRS.user_data_dir


class FarmServicesBaseException(ServicesBaseException):
    """Farm Services Base Exception that logs error messages and status codes.

    This exception extends ServicesBaseException and automatically logs
    the error message and status code when raised.
    """

    def __init__(self, status_code: int, detail: str, request: Request, **kwargs):
        """Initialize the exception with logging.

        Args:
            status_code: HTTP status code for the error
            detail: Error message detail
            request: FastAPI Request object (required, used to extract endpoint info)
            **kwargs: Additional keyword arguments for ServicesBaseException
        """
        # Extract endpoint from request
        path = request.url.path
        method = request.method

        # Log the error message and status code with structured logging
        logging.error(
            "Farm Services Exception",
            extra={
                "status_code": status_code,
                "detail": detail,
                "path": path,
                "method": method
            }
        )

        # Call the parent constructor
        super().__init__(status_code=status_code, detail=detail, **kwargs)


async def post_data(url: str, data: Dict, **session_kwargs: Any):
    """Perform a 'post' request."""
    logging.debug(f"HTTP POST request to '{url}', with data {data}")
    from nv.svc.core.client.http import HTTPClientSession

    async with HTTPClientSession(raise_for_status=True) as session:
        response = await session.post(url, json=data, **session_kwargs)
        rjson = await response.json()
        return rjson


async def fetch_data(url: str, **session_kwargs: Any):
    """Perform a 'get' request."""

    logging.debug(f"HTTP GET request to '{url}'")
    from nv.svc.core.client.http import HTTPClientSession

    async with HTTPClientSession(raise_for_status=True) as session:
        response = await session.get(url, **session_kwargs)
        rjson = await response.json()
        return rjson


async def delete_request(url: str, **session_kwargs: Any):
    """Perform a 'delete' request."""

    logging.debug(f"HTTP DELETE request to '{url}'")
    from nv.svc.core.client.http import HTTPClientSession

    async with HTTPClientSession(raise_for_status=True) as session:
        response = await session.delete(url, **session_kwargs)
        if response.status == 204:
            return {}

        rjson = await response.json()
        return rjson


def configure_default_config_filepath():
    """Configure default global config filepath."""
    # NOTE: NV__SVC__GLOBAL__CONFIG_FILEPATH should be configured outside of the application before starting.
    if _GLOBAL_CONFIG_ENVVAR_NAME not in os.environ:
        # set the default config/application.toml.
        fp = str(Path(nv.svc.farm.__file__).parent / "config" / "application.toml")
        os.environ[_GLOBAL_CONFIG_ENVVAR_NAME] = fp
        logging.info(f"Configured '{_GLOBAL_CONFIG_ENVVAR_NAME}' envvar with '{fp}'")


class _ApiKeyHeader(security.APIKeyHeader):

    def __init__(
        self,
        scheme_name: typing.Optional[str] = None,
        auto_error: bool = True,
        check_functions: typing.List[typing.Awaitable[str]] = None
    ):
        super().__init__(name="X-API-KEY", scheme_name=scheme_name, auto_error=auto_error)
        self._functions = check_functions or []

    async def __call__(self, request: requests.Request) -> typing.Optional[str]:
        if not self._functions:
            return None

        # Extract API key
        api_key = await super().__call__(request)

        tasks = [asyncio.ensure_future(func(api_key)) for func in self._functions]
        try:
            await asyncio.gather(*tasks)
            return api_key
        except Exception:
            for task in tasks:
                task.cancel()
            raise exceptions.HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")


def ApiKeyHeader(scheme_name: typing.Optional[str] = None, auto_error: bool = True, check_functions: typing.List[typing.Awaitable[str]] = None):
    """Create a configurable APIKey based Auth implementation that can be used directly with the services framework.

    It can be passed through directly as a dependency to a router or endpoint.
    """

    return Depends(_ApiKeyHeader(scheme_name=scheme_name, auto_error=auto_error, check_functions=check_functions))


# --- Timing utilities ---------------------------------------------------------
def log_timing(label: str = None):
    """Log per-call elapsed time and seconds since last call.

    - label: optional label to use instead of function __name__
    - origin_ts: optional initial perf_counter() timestamp treated as the last completion

    Behavior:
        - First invocation: logs that it is the first invocation (no since_last).
        - Subsequent invocations: at start, logs since_last_s = start - origin.
        - At end of every call: logs elapsed_s and updates origin to the end time.
    """

    # 'origin' represents the last completion timestamp
    origin = time.perf_counter()

    def _decorate(func):
        func_name = label or getattr(func, "__name__", "anonymous")

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def _async_wrapped(*args, **kwargs):
                nonlocal origin
                start = time.perf_counter()
                since_last = (start - origin)
                origin = start
                try:
                    logging.info(f"function_invocation_start: {func_name} last_run={since_last:.3f}s")
                    return await func(*args, **kwargs)
                finally:
                    end = time.perf_counter()
                    elapsed = end - start
                    logging.info(f"function_invocation_complete: {func_name} {elapsed:.3f}s")

            return _async_wrapped

        @functools.wraps(func)
        def _sync_wrapped(*args, **kwargs):
            nonlocal origin
            start = time.perf_counter()
            since_last = (start - origin)
            origin = start
            logging.info(f"function_invocation_start: {func_name} last_run={since_last:.3f}s")
            try:
                return func(*args, **kwargs)
            finally:
                end = time.perf_counter()
                elapsed = end - start
                logging.info(f"function_invocation_complete: {func_name} {elapsed:.3f}s")

        return _sync_wrapped

    return _decorate
