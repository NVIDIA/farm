# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework config settings."""

from pathlib import Path

from .utils.config import Config, setting

PACKAGE_NAME = "nv.svc.core"
DEFAULT_DATA_PATH = str(Path(__file__).resolve().parent / "data")


@setting(
    "logging.log_level",
    cast=str,
    default="INFO",
    description="The logging level. NOTE: defaults to INFO, not WARN",
)
def ServicesCoreLoggingConfig(*validators) -> Config:
    """Omni Services Core Logging configuration settings."""
    return Config(package_name=PACKAGE_NAME, auto_configure_logging=False, raise_on_package_not_found_error=False, validators=list(validators))


@setting(
    "root_path",
    default="/",
    description="Set root path for the application.",
)
@setting(
    "show_status_endpoint",
    cast=bool,
    default=True,
    description="Shows the status endpoint for the application.",
)
@setting("data_path", default=DEFAULT_DATA_PATH, description="Data path for the application.")
@setting(
    "correlation_id.use_default_middleware",
    cast=bool,
    default=True,
    description="Flag indicating whether to use the default Correlation ID middleware provided by the Services framework.",
)
@setting("correlation_id.header_name", default="X-Correlation-ID", description="Name of the HTTP Header to read correlation IDs from")
@setting(
    "correlation_id.update_request_header",
    cast=bool,
    default=True,
    description="Flag indicating whether to update the incoming request's header value with the generated correlation ID.",
)
def ServicesCoreConfig(*validators) -> Config:
    """Omni Services Core configuration settings."""
    return Config(package_name=PACKAGE_NAME, validators=list(validators), raise_on_package_not_found_error=False)
