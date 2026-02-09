# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Agents Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


def configure_agents_service(core: ServicesCore = None) -> ServicesCore:
    """Configure agents service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.agents.config import FarmAgentsConfig
    from nv.svc.farm.services.agents.router import router

    config = FarmAgentsConfig()

    logging.info("Configuring Agents service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-agents",
            description="Farm Agents Service.",
            version=config.package_version,
        )

    agent_manager = load_cls_from_string(config.agents.manager_class)(
        check_interval=config.agents.check_interval,
        lost_timeout=config.agents.lost_timeout,
        farm_tasks_address=config.agents.farm_tasks_address,
        **config.agents.manager_args)

    core.register_facility("agent_manager", agent_manager)
    core.register_router(router, prefix=config.agents.url_prefix, tags=config.agents.tags)

    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_agents_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
