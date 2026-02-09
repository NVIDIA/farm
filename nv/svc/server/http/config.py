# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Services Server HTTP Config Settings."""

from pathlib import Path

from nv.svc.core.utils.config import Config, setting

DEFAULT_DATA_PATH = str(Path(__file__).resolve().parent / "data")


@setting(
    "http.enabled",
    cast=bool,
    default=True,
    description="Enables HTTP Server",
)
@setting(
    "host",
    cast=str,
    default="0.0.0.0",
    description="Host to bind HTTP Server to",
)
@setting(
    "port",
    cast=int,
    default="8011",
    description="Port number for HTTP Server to listen on",
)
@setting(
    "loop",
    cast=str,
    default="auto",
    description=(
        "Set the event loop implementation. The 'uvloop' implementation provides greater performance, but is not compatible with Windows or PyPy. "
        "Options: 'auto', 'asyncio', 'uvloop'."),
)
@setting(
    "workers",
    cast=int,
    gte=1,
    default=1,
    description="Use multiple worker processes.",
)
@setting(
    "setup_event_loop",
    cast=bool,
    default=True,
    description="Automatically set up and configure the event loop via uvicorn.",
)
@setting(
    "log_level",
    cast=str,
    default="error",
    description="Log level for HTTP Server",
)
@setting(
    "enable_access_logs",
    cast=bool,
    default=False,
    description="Enable access logs on HTTP Server",
)
@setting(
    "allow_port_range",
    cast=bool,
    default=True,
    description="Allow port range on HTTP Server",
)
@setting(
    "https.enabled",
    cast=bool,
    default=False,
    description="Enables HTTPS Server",
)
@setting(
    "https.host",
    cast=str,
    default="0.0.0.0",
    description="Host to bind HTTPS Server to",
)
@setting(
    "https.port",
    cast=int,
    default="8433",
    description="Port number for HTTPS Server to listen on",
)
@setting(
    "https.loop",
    cast=str,
    default="auto",
    description=(
        "Set the event loop implementation. The 'uvloop' implementation provides greater performance, but is not compatible with Windows or PyPy. "
        "Options: 'auto', 'asyncio', 'uvloop'."),
)
@setting(
    "https.workers",
    cast=int,
    gte=1,
    default=1,
    description="Use multiple worker processes for HTTPS Server.",
)
@setting(
    "https.log_level",
    cast=str,
    default="error",
    description="Log level for HTTPS Server",
)
@setting(
    "https.enable_access_logs",
    cast=bool,
    default=False,
    description="Enable access logs on HTTPS Server",
)
@setting(
    "ssl.ssl_keyfile", cast=str, default="", description="SSL keyfile"
)
@setting(
    "ssl.ssl_certfile",
    cast=str,
    default="",
    description="SSL Certificate",
)
@setting(
    "ssl.ssl_version", cast=str, default="", description="SSL Version"
)
@setting(
    "ssl.ssl_cert_reqs",
    cast=str,
    default="",
    description="SSL Certificate Requests",
)
@setting(
    "ssl.ssl_ca_certs",
    cast=str,
    default="",
    description="SSL CA Certificates",
)
@setting(
    "ssl.ssl_ciphers",
    cast=str,
    default="TLSv1",
    description="SSL Ciphers",
)
@setting(
    "cors.enabled",
    cast=bool,
    default=False,
    description="Enable CORS"
)
@setting(
    "cors.allow_origins",
    cast=list,
    default=[],
    description="List of allow origins",
)
@setting(
    "cors.allow_credentials",
    cast=bool,
    default="",
    description="Allow credentials",
)
@setting(
    "cors.allow_methods",
    cast=list,
    default=[],
    description="List of allowed methods",
)
@setting(
    "cors.allow_headers",
    cast=list,
    default=[],
    description="List of allowed headers",
)
def ServerHTTPConfig(*validators) -> Config:
    """Services Server HTTP Configuration Settings."""
    return Config(package_name=__package__, validators=list(validators), raise_on_package_not_found_error=False)
