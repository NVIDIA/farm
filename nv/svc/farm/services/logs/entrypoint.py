# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Logs Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


def configure_logs_service(core: ServicesCore = None) -> ServicesCore:
    """Configure logs service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.logs.config import FarmLogsConfig
    from nv.svc.farm.services.logs.router import router

    config = FarmLogsConfig()

    logging.info("Configuring Logs service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-logs",
            description="Farm Logs Service.",
            version=config.package_version,
        )

    log_store = load_cls_from_string(config.logs.store_class)(**config.logs.store_args)
    core.register_facility("log_store", log_store)
    core.register_router(router, prefix=config.logs.url_prefix, tags=config.logs.tags)
    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_logs_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
