# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Retries Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


def configure_retries_service(core: ServicesCore = None) -> ServicesCore:
    """Configure retries service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.retries.config import FarmRetriesConfig
    from nv.svc.farm.services.retries.facilities import RetryManager
    from nv.svc.farm.services.retries.router import router

    config = FarmRetriesConfig()

    logging.info("Configuring Retries service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-retries",
            description="Farm Retries Service.",
            version=config.package_version,
        )

    retry_manager = RetryManager(
        farm_tasks_address=config.retries.farm_tasks_address,
        retry_limit=config.retries.retry_limit,
        task_max_age=config.retries.task_max_age,
        task_type_blocklist=config.retries.task_type_blocklist,
        task_function_blocklist=config.retries.task_function_blocklist,
    )

    core.register_facility("retry_manager", retry_manager)
    core.register_router(router, prefix=config.retries.url_prefix, tags=config.retries.tags)
    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_retries_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
