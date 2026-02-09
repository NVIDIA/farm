# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.services.capacity.entrypoint import configure_capacity_service

from nv.svc.farm.utils import configure_default_config_filepath


def configure_controller_service(core: ServicesCore = None) -> ServicesCore:
    """Configure controller service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.controller.config import FarmControllerConfig
    from nv.svc.farm.services.controller.task_manager import TaskManager
    from nv.svc.farm.services.controller.router import router
    from nv.svc.farm.services.tasks.facilities.tasks.store import TaskStore

    config = FarmControllerConfig()

    logging.info("Configuring Controller service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-controller",
            description="Farm Controller Service.",
            version=config.package_version,
        )

    job_store = load_cls_from_string(config.controller.job_store_class)(**config.controller.job_store_args)
    process_manager = load_cls_from_string(config.controller.job_manager_class)(
        job_store=job_store,
        **config.controller.job_manager_args
    )

    bay_controller = load_cls_from_string(config.controller.bay_controller_class)(**config.controller.bay_controller_args)
    task_backend = load_cls_from_string(config.controller.task_backend_class)(**config.controller.task_backend_args)
    task_store = TaskStore(task_backend)
    task_manager = TaskManager(
        task_store=task_store,
        bay_controller=bay_controller,
        config=config,
        process_manager=process_manager,
    )

    core.register_facility("task_manager", task_manager)
    core.register_endpoint("get", "/connected", task_manager.get_agent_status)
    core.register_router(router, prefix=config.controller.url_prefix, tags=config.controller.tags)

    core.register_startup_coroutine(job_store.start)
    core.register_startup_coroutine(process_manager.run)
    core.register_startup_coroutine(process_manager.process_logs)

    core.register_startup_coroutine(task_manager.run)
    core.register_startup_coroutine(task_manager.run_checks)
    core.register_startup_coroutine(task_manager.agent_checkin)
    core.register_startup_coroutine(task_manager.reconcile)

    core.register_shutdown_coroutine(process_manager.stop_async)
    core.register_shutdown_coroutine(job_store.stop)
    core.register_shutdown_coroutine(task_manager.unregister_agent)

    configure_capacity_service(core)

    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_controller_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
