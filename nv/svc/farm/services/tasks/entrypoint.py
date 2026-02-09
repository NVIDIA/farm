# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Tasks Service Entrypoint."""

import asyncio
from collections import defaultdict
import logging
from random import uniform
from typing import Any, Dict, List

from nv.svc.core.main import ServicesCore
from nv.svc.core.utils import load_cls_from_string
from nv.svc.server.http import HTTPServer

from nv.svc.farm.utils import configure_default_config_filepath


async def _collect_metrics(task_store, metrics_facility, metrics_collect_interval):
    # Add jitter to avoid all services, querying the same metrics at the same time.
    await asyncio.sleep(uniform(0.0, 10.0))
    statuses = ["submitted", "running"]
    status_gauges = {
        status: metrics_facility.gauge(
            status,
            f"Number of {status} tasks",
            labelnames=("task_type", "task_function"),
            unit="tasks") for status in statuses}
    while True:
        try:
            await _collect_task_gauges(task_store, statuses, status_gauges)
        except asyncio.exceptions.CancelledError:
            return
        except Exception as exc:
            logging.warning(f"Failed to collect metrics: {type(exc)}, {exc}")
        finally:
            await asyncio.sleep(metrics_collect_interval)


async def _collect_task_gauges(task_store, statuses: List[str], status_gauges: Dict[str, Any]):
    tasks = {status: asyncio.ensure_future(task_store.get_tasks(statuses=[status])) for status in statuses}
    await asyncio.gather(*tasks.values())

    for status, future in tasks.items():
        collected = defaultdict(int)
        data = future.result()
        gauge = status_gauges[status]
        for task in data:
            collected[(task["task_type"], task["task_function"])] += 1

        for task_id, value in collected.items():
            task_type, task_function = task_id
            gauge.labels(task_type=task_type, task_function=task_function).set(value)


def configure_tasks_service(core: ServicesCore = None) -> ServicesCore:
    """Configure tasks service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.tasks.config import FarmTasksConfig
    from nv.svc.farm.services.tasks.facilities.tasks.task_backend import TaskDatabaseBackend
    from nv.svc.farm.services.tasks.facilities.tasks.store import TaskStore
    from nv.svc.farm.services.tasks.router import router

    config = FarmTasksConfig()

    logging.info("Configuring Tasks service.")

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-tasks",
            description="Farm Tasks Service.",
            version=config.package_version,
        )

    # Initialize event handlers
    event_handlers = []

    # Add any additional configured handlers
    for import_path in config.tasks.event_handlers:
        handler_cls = load_cls_from_string(import_path)
        class_name = import_path.split(".")[-1]
        handler_args = config.tasks.event_handler_args.get(class_name, {})
        event_handlers.append(handler_cls(**handler_args))

    backend = TaskDatabaseBackend(database_handle="task-persistence")
    task_store = TaskStore(backend=backend, event_handlers=event_handlers)

    core.register_facility("task_store", task_store)
    core.register_facility("config", config)
    core.register_router(router, prefix=config.tasks.url_prefix, tags=config.tasks.tags)
    core.register_startup_coroutine(task_store.start)

    # metrics_facility = core._facilities[core._METRICS_FACILITY_NAME]
    # core.register_startup_coroutine(
    #     collect_metrics,
    #     task_store=task_store,
    #     metrics_facility=metrics_facility,
    #     metrics_collect_interval=config.tasks.metrics_collect_interval,
    # )
    return core


def main():
    """Configure and run the application with an HTTP server."""

    configure_tasks_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
