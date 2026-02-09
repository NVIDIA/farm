# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Services Entrypoint."""

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils.config import Config

from nv.svc.server.http import HTTPServer

from nv.svc.farm.services.agents.entrypoint import configure_agents_service
from nv.svc.farm.services.controller.entrypoint import configure_controller_service
from nv.svc.farm.services.dag.entrypoint import configure_dag_service
from nv.svc.farm.services.dashboard.entrypoint import configure_dashboard_service
from nv.svc.farm.services.jobs.entrypoint import configure_jobs_service
from nv.svc.farm.services.logs.entrypoint import configure_logs_service
from nv.svc.farm.services.results.entrypoint import configure_results_service
from nv.svc.farm.services.retries.entrypoint import configure_retries_service
from nv.svc.farm.services.settings.entrypoint import configure_settings_service
from nv.svc.farm.services.tasks.entrypoint import configure_tasks_service

from nv.svc.farm.utils import configure_default_config_filepath


def configure_farm_services(with_controller=True) -> ServicesCore:
    """Configure Farm services with service core."""

    configure_default_config_filepath()

    config = Config(package_name="nv.svc.farm", auto_configure_logging=True)

    core = ServicesCore(
        title=config.package_name,
        description="Farm Services.",
        version=config.package_version,
    )

    configure_agents_service(core)
    configure_dag_service(core)
    configure_dashboard_service(core)
    configure_jobs_service(core)
    configure_logs_service(core)
    configure_results_service(core)
    configure_retries_service(core)
    configure_settings_service(core)
    configure_tasks_service(core)

    if with_controller:
        # NOTE: Controller also configures Capacity and Operator services.
        configure_controller_service(core)

    return core


def _start_http_server():
    # configure uvicorn http server.
    server = HTTPServer()
    server.on_startup()


def run_all_farm_services():
    """Configure and run the application with an HTTP server."""

    configure_farm_services()
    _start_http_server()


def run_api_farm_services():
    """Configure and run the application with an HTTP server."""

    configure_farm_services(with_controller=False)
    _start_http_server()


def main():
    """Configure and run the application with an HTTP server."""

    run_all_farm_services()


if __name__ == "__main__":
    main()
