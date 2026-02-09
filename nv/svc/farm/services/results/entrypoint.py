# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


def configure_results_service(core: ServicesCore = None) -> ServicesCore:
    """Configure results service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.results.config import FarmResultsConfig
    from nv.svc.farm.services.results.router import router

    config = FarmResultsConfig()

    logging.info("Configuring Results service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-results",
            description="Farm Results Service.",
            version=config.package_version,
        )

    result_manager = load_cls_from_string(config.results.manager_class)(
        **config.results.manager_args)

    core.register_facility("config", config)
    core.register_facility("result_manager", result_manager)
    core.register_router(router, prefix=config.results.url_prefix)

    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_results_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
