# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


def configure_jobs_service(core: ServicesCore = None) -> ServicesCore:
    """Configure jobs service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.jobs.config import FarmJobsConfig
    from nv.svc.farm.services.jobs.router import router

    config = FarmJobsConfig()

    logging.info("Configuring Jobs service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-jobs",
            description="Farm Jobs Service.",
            version=config.package_version,
        )

    jobs_store = load_cls_from_string(config.jobs.store_class)(**config.jobs.store_args)

    core.register_facility("job_store", jobs_store)
    core.register_router(router, prefix=config.jobs.url_prefix, tags=config.jobs.tags)

    core.register_startup_coroutine(jobs_store.start)
    core.register_shutdown_coroutine(jobs_store.stop)

    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_jobs_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
