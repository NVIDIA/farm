# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""omni services server http server."""
import asyncio
import logging
import ssl
from typing import Dict, List

from fastapi.middleware.cors import CORSMiddleware

from nv.svc.core import main

from nv.svc.server.http.base import utils as base_utils
from .config import ServerHTTPConfig


class SSLConfigurationError(Exception):
    """Raised when an https server has been enabled but no ssl configuration has been specified."""


class HTTPServer:
    """HTTP(s) server.

    Uses the services registered with the kit controlport and exposes them over HTTP(S)

    When the extension is enabled the API documentation is available on the following url:
    http://<hostname>:<port>/docs or https://<hostname>:<port>/docs
    """

    def __init__(self):
        """Initialize HTTPServer to its defaults."""
        super().__init__()
        self._http_server = None
        self._https_server = None
        self._settings = None
        self._setup_event_loop = True

    def on_startup(self):
        """Start up server event loop."""
        self._settings = ServerHTTPConfig().settings
        self._setup_event_loop = self._settings.nv.svc.server.http.setup_event_loop

        if self._settings.nv.svc.server.http.http.enabled:
            self._http_server = self._setup_http_server()
            if self._setup_event_loop:
                self._http_server.run()
            else:
                asyncio.ensure_future(self._http_server.serve())

        if self._settings.nv.svc.server.http.https.enabled:
            self._https_server = self._setup_https_server()
            if self._setup_event_loop:
                self._https_server.run()
            else:
                asyncio.ensure_future(self._https_server.serve())

    def _setup_http_server(self):
        host = self._settings.nv.svc.server.http.host
        port = self._settings.nv.svc.server.http.port
        loop = self._settings.nv.svc.server.http.loop
        log_level = self._settings.nv.svc.server.http.log_level
        workers = self._settings.nv.svc.server.http.workers
        enable_access_logs = self._settings.nv.svc.server.http.enable_access_logs

        allow_range = self._settings.nv.svc.server.http.allow_port_range
        validated_port = base_utils.validate_port(port, allow_range=allow_range)
        if validated_port != port:
            logging.warning(
                f"http server was meant to start on {port} but port is taken, starting on port {validated_port} instead"
            )
            self._settings.nv.svc.server.http.port = validated_port
            port = validated_port

        return self._configure_server(
            scheme="http",
            host=host,
            port=port,
            workers=workers,
            loop=loop,
            log_level=log_level,
            enable_access_logs=enable_access_logs,
        )

    def _setup_https_server(self):
        https_config: Dict = self._settings.get("nv.svc.server.http.https").to_dict()
        https_config.pop("enabled")

        ssl_config: Dict = self._settings.get("nv.svc.server.http.ssl").to_dict()
        ssl_config = self._validate_ssl_config(ssl_config)

        https_config["ssl_config"] = ssl_config
        return self._configure_server("https", **https_config)

    def _enable_cors_middleware(
        self,
        allow_origins: List[str],
        allow_methods: List[str],
        allow_headers: List[str],
        allow_credentials: bool,
    ) -> None:
        main.register_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )

    def _validate_ssl_config(self, ssl_config: Dict):

        if "ssl_keyfile" not in ssl_config or not ssl_config["ssl_keyfile"]:
            raise SSLConfigurationError(
                "No ssl_keyfile was specified in the settings. An https server cannot be started."
            )

        if "ssl_certfile" not in ssl_config or not ssl_config["ssl_certfile"]:
            raise SSLConfigurationError(
                "No ssl_certfile was specified in the settings. An https server cannot be started."
            )

        ssl_config["ssl_ca_certs"] = ssl_config["ssl_ca_certs"] or None

        ssl_version = ssl_config["ssl_version"]

        # Local import for speed
        from uvicorn import config as _uv_config

        ssl_config["ssl_version"] = (
            ssl_version if ssl_version != -1 else _uv_config.SSL_PROTOCOL_VERSION
        )

        ssl_cert_reqs = ssl_config["ssl_cert_reqs"]
        ssl_config["ssl_cert_reqs"] = (
            ssl_cert_reqs if ssl_cert_reqs != -1 else ssl.CERT_NONE
        )

        return ssl_config

    def _configure_server(
        self,
        scheme,
        host,
        port,
        workers=1,
        log_level="error",
        loop="asyncio",
        enable_access_logs=False,
        ssl_config: Dict = None,
    ):
        # local imports for performance
        import uvicorn

        ssl_config = ssl_config or {}
        config = uvicorn.Config(
            main.get_app(),
            host=host,
            port=port,
            log_level=log_level,
            loop=loop,
            workers=workers,
            access_log=enable_access_logs,
            **ssl_config,
        )

        if self._settings.nv.svc.server.http.cors.enabled:
            allow_origins = (
                self._settings.nv.svc.server.http.cors.allow_origins.to_list()
            )
            allow_credentials = (
                self._settings.nv.svc.server.http.cors.allow_credentials
            )
            allow_methods = (
                self._settings.nv.svc.server.http.cors.allow_methods.to_list()
            )
            allow_headers = (
                self._settings.nv.svc.server.http.cors.allow_headers.to_list()
            )
            self._enable_cors_middleware(
                allow_origins=allow_origins,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
                allow_credentials=allow_credentials,
            )

        try:
            root_path = self._settings.nv.svc.core.root_path
        except Exception:
            root_path = ""
        logging.info(f"Server will attempt to start on {scheme}://{host}:{port} (API Spec available at {root_path}/docs)")

        return uvicorn.Server(config=config)

    def on_shutdown(self):
        """Shuts down the server."""
        if not self._setup_event_loop:
            if self._http_server:
                self._http_server.should_exit = True
                asyncio.get_event_loop().run_until_complete(self._http_server.shutdown())
                self._http_server = None

            if self._https_server:
                self._https_server.should_exit = True
                asyncio.get_event_loop().run_until_complete(self._https_server.shutdown())
                self._https_server = None
