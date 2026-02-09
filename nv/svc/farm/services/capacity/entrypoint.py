# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Capacity Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


def configure_capacity_service(core: ServicesCore = None) -> ServicesCore:
    """Configure capacity service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.capacity.config import FarmCapacityConfig
    from nv.svc.farm.services.capacity.router import router

    config = FarmCapacityConfig()

    logging.info("Configuring Capacity service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-capacity",
            description="Farm Capacity Service.",
            version=config.package_version,
        )

    capacity_manager = load_cls_from_string(config.capacity.manager_class)(**config.capacity.manager_args)
    capacity_manager.updateSettings(config.settings)
    core.register_facility("capacity_manager", capacity_manager)
    core.register_router(router, prefix=config.capacity.url_prefix, tags=config.capacity.tags)
    core.register_startup_coroutine(capacity_manager.load_capacities)

    return core


def main():
    """Configure and run the application with an HTTP server."""
    configure_capacity_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
