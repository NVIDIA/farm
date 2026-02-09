# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Dashboard Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.server.http import HTTPServer
from nv.svc.farm.utils import configure_default_config_filepath


def configure_dashboard_service(core: ServicesCore | None = None) -> ServicesCore:
    """Configure dashboard service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.dashboard.config import FarmDashboardConfig
    from nv.svc.farm.services.dashboard.server import SinglePageAppWebServer

    config = FarmDashboardConfig()

    logging.info("Configuring Dashboard service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-dashboard",
            description="Farm Dashboard Service.",
            version=config.package_version,
        )

    web_server = SinglePageAppWebServer(
        core=core,
        service_name=f"{config.package_name}-dashboard",
        version=config.package_version,
        frontend_host=config.dashboard.host,
        frontend_root_path=config.settings.nv.svc.core.get("root_path", ""),
        frontend_url_prefix=config.dashboard.url_prefix,
        static_directory=config.dashboard.build_dir,
    )
    web_server.add_config_value("starfleet_enabled", config.dashboard.starfleet_enabled)
    web_server.add_config_value("starfleet_client_id", config.dashboard.starfleet_client_id)
    web_server.add_config_value("starfleet_login_url", config.dashboard.starfleet_login_url)
    web_server.startup()

    return core


def main():
    """Configure and run the application with an HTTP server if enabled."""
    configure_dashboard_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
