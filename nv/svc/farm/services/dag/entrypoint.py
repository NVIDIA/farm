# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm DAG Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath

from .config import FarmDAGConfig
from .facilities.dag_backend import DagDatabaseBackend
from .facilities.dag_store import DAGStore
from .router import router


def configure_dag_service(core: ServicesCore = None) -> ServicesCore:
    """Configure DAG service with service core."""
    configure_default_config_filepath()

    config = FarmDAGConfig()

    logging.info("Configuring DAG service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-dag",
            description="Farm DAG Service.",
            version=config.package_version,
        )

    # Initialize backend and store
    backend = DagDatabaseBackend(connection_string=config.dag.database.get("connection_string"))
    dag_store = DAGStore(
        backend=backend,
        task_service_url=config.dag.task_service_url,
    )

    # Register facilities and router
    core.register_facility("dag_store", dag_store)
    core.register_router(router, prefix=config.dag.url_prefix, tags=config.dag.tags)

    # Register startup coroutines
    core.register_startup_coroutine(dag_store.start)

    return core


def main():
    """Configure and run the application with an HTTP server."""
    configure_dag_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
