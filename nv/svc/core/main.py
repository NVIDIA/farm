# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework."""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import starlette
from fastapi.responses import JSONResponse
from fastapi.routing import APIWebSocketRoute
from starlette.types import ASGIApp

from . import _app, _encoding, routers
from .config import ServicesCoreConfig
from .facilities import base as facilities

_singleton = None


def register_endpoint(verb: str, url: str, func: Callable[..., Any], **kwargs: Optional[Any]) -> None:
    """
    Register an endpoint with the Services framework.

    Args:
        verb (str): HTTP verb the endpoint should respond to (e.g. "get", "post", "put", etc.).
        url (str): URL of the endpoint.
        func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_endpoint(verb, url, func, **kwargs)


def register_websocket_endpoint(url: str, func: Callable[..., Any], **kwargs) -> None:
    """
    Register an endpoint with the Services framework accessible via websockets.

    Args:
        url (str): URL of the endpoint.
        func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
        kwargs (kwargs): Optional additional parameters to forward to FastAPI.

    """
    _singleton.register_websocket_endpoint(url, func, **kwargs)


def register_mount(path: str, app: ASGIApp, **kwargs: Optional[Any]) -> None:
    """
    Register a mount point with the Services framework.

    Args:
        path (str): URL of the endpoint.
        app (ASGIApp): An ASGI-compatible mount point to forward to FastAPI.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_mount(path, app, **kwargs)


def register_facility(name: str, facility: facilities.Facility) -> None:
    """
    Register a facility with the Services framework. For automatically including in registered routers.

    Must ensure the facility is registered before registering routers.

    Args:
        name: (str): Name of the facility.
        facility (facilities.Facility): Facility to register to the Services framework.

    Returns:
        None
    """
    _singleton.register_facility(name, facility)


def register_router(router: routers.ServiceAPIRouter, **kwargs: Optional[Any]) -> None:
    """
    Register a router with the Services framework.

    Args:
        router (routers.ServiceAPIRouter): Router to register to the Services framework.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.register_router(router, **kwargs)


def register_middleware(cls: type, **kwargs: Optional[Any]) -> None:
    """
    Register a middleware with Services framework.

    Args:
        cls (type): Middleware to register to the Services framework.
        **kwargs: Optional additional parameters to forward to FastAPI.

    Returns:
        None

    """
    _singleton.app.add_middleware(cls, **kwargs)


def deregister_endpoint(verb: str, url: str) -> None:
    """
    Deregister an endpoint from the Services framework.

    Args:
        verb (str): HTTP verb of the endpoint to deregister (e.g. "get", "post", "put", etc.).
        url (str): URL of the endpoint to deregister.

    Returns:
        None

    """
    _singleton.deregister_endpoint(verb, url)


def deregister_mount(path: str) -> None:
    """
    Deregister a mount point from the Services framework.

    Args:
        path (str): Path of the mount point to deregister.

    Returns:
        None

    """
    _singleton.deregister_mount(path)


def deregister_router(router: routers.ServiceAPIRouter, prefix: str = None) -> None:
    """
    Deregister a router from the Services framework.

    Args:
        router (routers.ServiceAPIRouter): Router to deregister.
        prefix (str): Prefix of the Router to deregister.

    Returns:
        None

    """
    _singleton.deregister_router(router, prefix=prefix)


def register_encoder(name: str, encoder: Any) -> None:
    """
    Register a data encoder.

    The encoder is expected to have both a `compress` and `decompress` function.

    Args:
        name (str): Name of the encoder to register.
        encoder (Any): Encoder to register.

    Returns:
        None

    """
    _encoding.register_encoder(name, encoder)


def set_metadata(title: str, description: str, version: str, tags_metadata: List[Dict[str, str]] = None, root_path: Optional[str] = None) -> None:
    """
    Set service metadata.

    Args:
        title (str): Title of the service
        description (str): Description of the service
        version (str): Version of the service

    Kwargs:
        tags_metadata List[Dict[str, str]]: List of definitions for tags in the format:
            [{"name": "<name of tag>"}, "description": "<tag description>"}, {"name": "<name of tag>"}, "description": "<tag description>"}]
        root_path (Optional[str]): Root path to use in case of a service being behind
            a proxy (see the `Fast API documentation <https://fastapi.tiangolo.com/advanced/behind-a-proxy>`_ for reference).

    Returns:
        None

    """
    _singleton.set_description(title, description, version)

    if root_path:
        _singleton.set_root_path(root_path)

    if tags_metadata:
        get_app().openapi_tags.extend(tags_metadata)


def get_app():
    """Return the application instance."""
    return _singleton.app


async def _status():
    """Return the current status of the service."""
    return "OK"


class ServicesCore:
    """
    The Core of microservices framework.

    When paired with one (or multiple) of the transport extensions the services can be served to be accessed over
    various protocols such as HTTP, HTTPS, etc.

    """

    _METRICS_FACILITY_NAME = "metrics"
    _TRACING_FACILITY_NAME = "tracing"

    _title = "Services Core"
    _description = "Services Core Framework."
    _version = "0.1.0"

    def __init__(self, **kwargs):
        """Initialize ServicesCore instance."""
        self._conf = ServicesCoreConfig()
        root_path = self._conf.settings.nv.svc.core.root_path
        self._data_path = self._conf.settings.nv.svc.core.data_path

        title = kwargs.pop("title", self._title)
        description = kwargs.pop("description", self._description)
        version = kwargs.pop("version", self._version)
        _root_path = kwargs.pop("root_path", root_path)
        openapi_tags = kwargs.pop("openapi_tags", [])

        if "lifespan" in kwargs:
            logging.warning("'lifespan' kwarg is not supported. Use 'register_startup_coroutine()' and 'register_shutdown_coroutine()' instead.")
            kwargs.pop("lifespan")

        @asynccontextmanager
        async def _lifespan(app: _app.OmniverseService):
            asyncio.ensure_future(self._lifespan_startup())
            yield
            await self._lifespan_shutdown()

        self._app = _app.OmniverseService(
            title=title,
            description=description,
            version=version,
            root_path=_root_path,
            openapi_tags=openapi_tags,
            lifespan=_lifespan,
            **kwargs
        )
        self._facilities: Dict[str, facilities.Facility] = {}

        self._async_apps = {}

        self._grpc_server = None

        self._startup_coroutine_info: List[Tuple[Callable[..., Any], Dict[str, Any]]] = []
        self._shutdown_coroutine_info: List[Tuple[Callable[..., Any], Dict[str, Any]]] = []
        self._futures: List[asyncio.Future] = []

        # Register FastAPI middlewares to assist with configuration of the Services framework:
        self._register_middlewares()

        # Register default endpoints and initialize the internal singleton.
        self._on_startup()

    async def _lifespan_startup(self) -> None:
        """
        Startup method for the lifespan of the application.

        Starts asyncapps and executes registered startup coroutines.
        """

        def _done_callback(task):
            # surface any exceptions if any.
            task.result()

        for name, app in self._async_apps.items():
            logging.debug(f"Starting Async App: {name}")
            await app.start()

        for coroutine, kwargs in self._startup_coroutine_info:
            task = asyncio.ensure_future(coroutine(**kwargs))
            task.add_done_callback(_done_callback)
            self._futures.append(task)

    async def _lifespan_shutdown(self) -> None:
        """
        Shutdown method for the lifespan of the application.

        Stops asyncapps, cancels futures, and executes registered shutdown coroutines.
        """
        for name, app in self._async_apps.items():
            logging.debug(f"Stopping Async App: {name}")
            await app.stop()

        for future in self._futures:
            future.cancel()

        for coroutine, kwargs in self._shutdown_coroutine_info:
            await coroutine(**kwargs)

    def register_startup_coroutine(self, coroutine: Callable[..., Any], **kwargs: Any) -> None:
        """
        Register a coroutine to be executed during application startup.

        Parameters:
            coroutine (Callable): The coroutine function to be registered.
            **kwargs (Any): Keyword arguments to be passed to the coroutine.

        Returns:
            None
        """
        self._startup_coroutine_info.append((coroutine, kwargs))

    def register_shutdown_coroutine(self, coroutine: Callable[..., Any], **kwargs: Any) -> None:
        """
        Register a coroutine to be executed during application shutdown.

        Parameters:
            coroutine (Callable): The coroutine function to be registered.
            **kwargs (Any): Keyword arguments to be passed to the coroutine.

        Returns:
            None
        """
        self._shutdown_coroutine_info.append((coroutine, kwargs))

    def _register_middlewares(self) -> None:
        """
        Register FastAPI middlewares to assist with configuration of the Services framework.

        Args:
            None

        Return:
            None

        """
        if self._conf.settings.nv.svc.core.correlation_id.use_default_middleware:
            header_name = self._conf.settings.nv.svc.core.correlation_id.header_name
            update_request_header = self._conf.settings.nv.svc.core.correlation_id.update_request_header

            try:
                from asgi_correlation_id import CorrelationIdMiddleware

                self._app.add_middleware(
                    middleware_class=CorrelationIdMiddleware,
                    header_name=header_name,
                    update_request_header=update_request_header,
                )
                logging.debug("CorrelationID middleware enabled.")
            except ImportError as exc:
                logging.error(f"`asgi_correlation_id` middleware could not be imported: {str(exc)}")

    @property
    def app(self) -> _app.OmniverseService:
        """
        Return a reference to the FastAPI app.

        Returns:
            (OmniverseApp): A reference to the OmniverseService app.

        """
        return self._app

    def set_description(self, title: str, description: str, version: str) -> None:
        """
        Set the description of the microservices framework.

        Args:
            title (str): Title of the microservices framework.
            description (str): Description of the microservices framework.
            version (str): String representing the semantic versioning scheme of the microservices framework.

        Returns:
            None

        """
        self._app.title = title
        self._app.description = description
        self._app.version = version
        self._reset_openapi_schema()

    def set_root_path(self, root_path: str) -> None:
        """
        Set the root path of the service (e.g.: `/api/v1`).

        Args:
            root_path (str): Root path to use in case of a service being behind a proxy (https://fastapi.tiangolo.com/advanced/behind-a-proxy/)

        Returns:
            None

        """
        self._app.root_path = root_path
        self._reset_openapi_schema()

    @property
    def facilities(self) -> Dict[str, facilities.Facility]:
        """
        Return the dict of Facilities currently registered with the microservices framework.

        Returns:
            Dict[str, facilities.Facility]: The dict of Facilities currently registered.

        """
        return self._facilities

    def on_startup(self) -> None:
        """Start the ServicesCore application (deprecated)."""
        logging.warning("on_startup() is no longer required to be called. Method will be deprecated on version 1.0.0")

    def _on_startup(self) -> None:
        """Startup the ServicesCore application."""
        global _singleton
        _singleton = self

        self.register_endpoint("get", "/status", _status, include_in_schema=self._conf.show_status_endpoint,
                               summary="Returns the current status of the service")
        self.register_endpoint("get", "/health", _status, include_in_schema=self._conf.show_status_endpoint, summary="Health probe")
        self.register_endpoint("get", "/ready", _status, include_in_schema=self._conf.show_status_endpoint, summary="Readiness probe")
        self.register_endpoint("get", "/startup", _status, include_in_schema=self._conf.show_status_endpoint, summary="Startup probe")

        self._configure_metrics()
        self._configure_tracing()

    def register_grpc_server(self, grpc_server):
        """Register a GRPC server instance (from nv.svc.server.grpc)."""
        try:
            from nv.svc.server.grpc import GRPCServer
        except ImportError:
            raise Exception("Unable to register a gRPC server, ensure nv.svc.core is installed with 'grpc' extra.")

        if self._grpc_server is not None:
            raise Exception("gRPC server was already created, only one instance of gRPC server is allowed.")

        if not isinstance(grpc_server, GRPCServer):
            raise Exception(f"grpc_server must an instance of nv.svc.server.grpc.GRPCServer, but received '{type(grpc_server)}'")

        logging.debug(f"Registering gRPC server using bind address '{grpc_server._bind_addr}'")
        self._grpc_server = grpc_server
        self.register_startup_coroutine(self._grpc_server.startup)
        self.register_shutdown_coroutine(self._grpc_server.shutdown)

    def _configure_metrics(self):
        try:
            from nv.svc.facilities.monitoring.metrics.facilities import MetricsFacility
            from nv.svc.facilities.monitoring.metrics.main import MetricsRuntime
        except ImportError:
            logging.debug("Unable to autoconfigure metrics, ensure nv.svc.core is installed with 'metrics' extra.")
            return

        logging.debug("Configuring metrics.")
        metrics = MetricsRuntime()
        metrics.on_startup()

        self._facilities[self._METRICS_FACILITY_NAME] = MetricsFacility(self._app.title)
        self.register_shutdown_coroutine(metrics.on_shutdown)

    def _configure_tracing(self):
        try:
            from nv.svc.facilities.monitoring.tracing.main import TracingRuntime
        except ImportError:
            logging.debug("Unable to autoconfigure tracing, ensure nv.svc.core is installed with 'tracing' extra.")
            return

        logging.debug("Configuring tracing.")
        tracing = TracingRuntime(trace_process_name=self._app.title)
        tracing.on_startup()

        self._facilities[self._TRACING_FACILITY_NAME] = tracing.facility
        self.register_shutdown_coroutine(tracing.on_shutdown)

    async def _async_app_schema_endpoint(self, app_name: str):
        if app_name not in self._async_apps:
            return JSONResponse(
                status_code=404,
                content={"message": "Not Found"},
            )

        return self._async_apps[app_name].spec()

    def register_endpoint(self, verb: str, url: str, func: Callable[..., Any], **kwargs: Optional[Any]) -> None:
        """
        Register an endpoint with the Services framework.

        Args:
            verb (str): HTTP verb the endpoint should respond to (e.g. "get", "post", "put", etc.).
            url (str): URL of the endpoint.
            func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        verb_func = getattr(self._app, verb)
        verb_func(url, **kwargs)(func)
        self._reset_openapi_schema()

    def register_websocket_endpoint(self, url: str, func: Callable[..., Any], **kwargs: Optional[Any]) -> None:
        """
        Register an endpoint with the Services framework accessible via websockets.

        Args:
            url (str): URL of the endpoint.
            func (Callable[..., Any]): Callback to execute upon reaching the endpoint.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        self._app.add_api_websocket_route(url, func, **kwargs)
        self._reset_openapi_schema()

    def register_mount(self, path: str, app: ASGIApp, **kwargs: Optional[Any]) -> None:
        """
        Register a mount point with the Services framework.

        Args:
            path (str): URL of the endpoint.
            app (ASGIApp): An ASGI-compatible mount point to forward to FastAPI.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        self._app.mount(path, app, **kwargs)
        self._reset_openapi_schema()

    def register_router(self, router: routers.ServiceAPIRouter, **kwargs: Optional[Any]) -> None:
        """
        Register a router with the Services framework.

        Args:
            router (routers.ServiceAPIRouter): Router to register to the Services framework.
            **kwargs: Optional additional parameters to forward to FastAPI.

        Returns:
            None

        """
        if "prefix" in kwargs and kwargs["prefix"]:
            prefix = kwargs["prefix"].replace(".", "/")
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"
            kwargs["prefix"] = prefix

            # NOTE: update '_bypassed_paths' and '_permissions' with the prefix,
            # which is otherwise unknown to the AuthorizedServiceAPIRouter, since the router is being registered at the app level
            if hasattr(router, "_bypassed_paths"):
                prefixed_bypassed_paths: Set[str] = set()
                for path in router._bypassed_paths:
                    prefixed_path = f'{kwargs["prefix"].rstrip("/")}{path}'
                    prefixed_bypassed_paths.add(prefixed_path)
                router._bypassed_paths = prefixed_bypassed_paths

            if hasattr(router, "_permissions"):
                permissions = {}
                for path, perms in router._permissions.items():
                    prefixed_path = f'{kwargs["prefix"].rstrip("/")}{path}'
                    permissions[prefixed_path] = perms
                router._permissions = permissions

        for name, facility in self._facilities.items():
            router.register_facility(name, facility)

        names = ", ".join(list(self._facilities.keys()))
        logging.debug(f"Router {str(router.__class__)} registered with facilities '{names}'.")

        self._app.include_router(router, **kwargs)
        self._reset_openapi_schema()

    def register_facility(self, name: str, facility) -> None:
        """
        Register a facility with the Services framework. For automatically including in registered routers.

        Must ensure the facility is registered before registering routers.

        Args:
            name: (str): Name of the facility.
            facility (facilities.Facility): Facility to register to the Services framework.

        Returns:
            None
        """
        self._facilities[name] = facility

    def deregister_endpoint(self, verb: str, url: str) -> None:
        """
        Deregister an endpoint from the Services framework.

        Args:
            verb (str): HTTP verb of the endpoint to deregister (e.g. "get", "post", "put", etc.).
            url (str): URL of the endpoint to deregister.

        Returns:
            None

        """
        to_remove = []
        for route in self._app.routes:
            if route.path == url:
                if isinstance(route, starlette.routing.Mount) or verb.upper() in route.methods:
                    to_remove.append(route)

        for route in to_remove:
            self._app.routes.remove(route)

        self._reset_openapi_schema()

    def deregister_mount(self, path: str) -> None:
        """
        Deregister the given service mount point.

        Args:
            path (str): Path of the mount point to deregister.

        Returns:
            None

        """
        mounts_to_remove = []
        for route in self._app.routes:
            if isinstance(route, starlette.routing.Mount) and route.path == path:
                mounts_to_remove.append(route)

        for mount_to_remove in mounts_to_remove:
            self._app.routes.remove(mount_to_remove)

        self._reset_openapi_schema()

    def deregister_router(self, router: routers.ServiceAPIRouter, prefix: str = None) -> None:
        """
        Deregister a router from the Services framework.

        Args:
            router (routers.ServiceAPIRouter): Router to deregister.
            prefix (str): Prefix of the Router to deregister.

        Returns:
            None

        """
        if prefix:
            prefix = prefix.replace(".", "/")
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"

        for route in router.routes:
            if hasattr(route, "methods"):
                methods = sorted(route.methods)
                path = f"{prefix}{route.path}" if prefix else route.path
                for method in methods:
                    self.deregister_endpoint(method, path)
            elif issubclass(route.__class__, APIWebSocketRoute) and route in self._app.routes:
                # WebSocket routes do not feature `methods` properties, as opposed to HTTP-based routers:
                self._app.routes.remove(route)

        self._reset_openapi_schema()

    def _reset_openapi_schema(self) -> None:
        """Reset the OpenAPI schema of the microservices framework."""
        self._app.openapi_schema = None

    def on_shutdown(self) -> None:  # pragma: no cover
        """Shutdown the ServicesCore application."""
        global _singleton
        _singleton = None

        for name, facility in self._facilities.items():
            logging.debug(f"Stopping facility '{name}'")
            facility.stop()

        if self._app:
            self.deregister_endpoint("get", "/status")
            self.deregister_endpoint("get", "/health")
            self.deregister_endpoint("get", "/ready")
            self.deregister_endpoint("get", "/startup")
