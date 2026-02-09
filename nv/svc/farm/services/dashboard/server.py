# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Module for serving a single-page web application through the SinglePageAppWebServer class.

This module defines the SinglePageAppWebServer class, which is responsible for
serving a single-page web application, handling static files, and providing
configuration and version endpoints.
"""

import os
from typing import Dict

import starlette
from fastapi.requests import Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from nv.svc.core.main import ServicesCore


class SinglePageAppWebServer:
    """
    SinglePageAppWebServer.

    Facility responsible for serving a single page web application.
    """

    def __init__(
        self,
        core: ServicesCore,
        service_name: str,
        version: str,
        frontend_host: str,
        frontend_root_path: str,
        frontend_url_prefix: str,
        static_directory: str,
        build_sub_directory: str = "assets",
    ) -> None:
        self._core: ServicesCore = core
        self._service_name: str = service_name
        self._version: str = version
        # Strip ending / to make route checks simpler
        self._frontend_host: str = frontend_host.rstrip("/")
        # Strip ending / to make route checks simpler... config.py ensures that the leading / is present
        self._frontend_root_path: str = frontend_root_path.rstrip("/")
        self._frontend_url_prefix: str = frontend_url_prefix.rstrip("/")
        # Path entrypoint to the service (root_path + url_prefix)
        self._entrypoint: str = f"{self._frontend_root_path}{self._frontend_url_prefix}"
        self._static_directory: str = self._resolve_static_directory(static_directory)
        self._build_sub_directory: str = build_sub_directory
        self._served_config: Dict[str, str] = dict()
        self._index_file_response = None

    def add_config_value(self, key: str, value) -> None:
        """
        Add a configuration value.

        Given a key (usually from an extension.toml), store the value in a config
        that can be retrieved via GET /config.
        """
        self._served_config[key] = value

    def startup(self) -> None:
        """
        Start the web server.

        Keep track of the index file, as all routes that 404 will be served the
        index in-line with how a single page app works. Pass a no-cache indicator
        so that the HTML is never cached (this means no one has to be asked to
        clear cache to get a new version of the site).
        """

        @self._core.app.get(f"{self._frontend_url_prefix}/config")
        async def get_config(request: Request):
            """
            Serve the explicitly exposed configuration data.

            Return the configuration as a dictionary.
            """
            return self._served_config

        @self._core.app.get(f"{self._frontend_url_prefix}/version")
        async def get_version(request: Request):
            """
            Serve the extension version.

            Return the version as a string.
            """
            return self._version

        # With a single page app, routes are not files, as such, they will 404.
        # When they 404, middleware will make sure this is a subroute of the
        # web app and, if it is, will return index.html so the app can
        # handle routing appropriately.
        @self._core.app.middleware("http")
        async def add_404(request: Request, call_next: Response):
            path = request.url.path
            forwarded_path = request.headers.get("X-Forwarded-Path", self._entrypoint)

            # Ignore URLs that are not part of the web app.
            if not path.startswith(self._entrypoint) or not self._static_directory:
                return await call_next(request)

            file = path[path.rindex("/") + 1 :]

            if path == self._entrypoint or path == f"{self._entrypoint}/" or file == "index.html":
                return self._serve_index_html(forwarded_path)

            response = await call_next(request)

            # Ignore any found resources.
            if response.status_code != 404:
                return response

            # Serve static files from web/build/build_sub_directory even if the request
            # is coming from some subpath with react routing.
            if self._build_sub_directory is not None and self._build_sub_directory in path:
                file = path[path.index(self._build_sub_directory) :]
                return self._serve_from_build_directory(file, forwarded_path)

            # Final edge case, an extensioned file that is not part of the content in
            # the static folder. This is for root icon and logo files.
            if "." in path:
                return self._serve_from_build_directory(file, forwarded_path)

            # Otherwise, return the index.html so the single page app can handle routing.
            return self._serve_index_html(forwarded_path)

        if self._static_directory:
            # Mount static files (e.g., html, js, css, etc.) for serving normally.
            self._core.app.mount(
                f"{self._entrypoint}",
                StaticFiles(directory=self._static_directory, html=False),
                name=f"{self._service_name}-static",
            )

    def shutdown(self) -> None:
        """
        Shutdown the web server.

        Unmount the "mount once the proper Kit-level API is available.
        """
        for route in self._core.app.routes:
            if isinstance(route, starlette.routing.Mount) and route.path == self._frontend_url_prefix:
                self._core.app.routes.remove(route)

    def _serve_from_build_directory(self, file: str, base: str):
        file_path = self._static_directory + "/" + file

        if os.path.isfile(file_path):
            return FileResponse(file_path)

        return self._serve_index_html(base)

    def _resolve_static_directory(self, static_directory: str):
        """
        Resolve the static directory path.

        Accept static directory config if exists and fallback to build directory in dashboard service directory.
        """
        if static_directory:
            return static_directory

        build_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "build")

        if os.path.exists(build_dir):
            return build_dir

        return ""

    def _serve_index_html(self, base: str):
        if self._index_file_response:
            return self._index_file_response

        # Define the path to the index.html file
        index_file_path = os.path.join(self._static_directory, "index.html")

        with open(index_file_path, 'r') as file:
            content = file.read()

        # Locate the <head> tag and insert the <base> tag right after it
        base_tag = f'<base href="{base.rstrip("/")}/">'
        head_position = content.find('<head>')
        if head_position != -1:
            # Insert the base tag after the <head> tag
            head_tag_length = len('<head>')
            content = content[:head_position + head_tag_length] + base_tag + content[head_position + head_tag_length:]

        # Return the modified HTML content with custom headers
        self._index_file_response = HTMLResponse(content=content, headers={"Cache-Control": "no-cache"})

        return self._index_file_response
