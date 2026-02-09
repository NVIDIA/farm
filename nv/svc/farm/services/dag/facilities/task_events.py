# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm DAG Task Event Handler."""

from typing import Any, Dict

from nv.svc.farm.utils import post_data
from nv.svc.farm.services.tasks.facilities.task_events.base import BaseTaskEventHandler


class DAGTaskEventHandler(BaseTaskEventHandler):
    """Task event handler for managing DAG-related task events."""

    def __init__(self, dag_service_url: str):
        """Initialize the DAG task event handler.

        Args:
            dag_service_url: URL of the DAG service
        """
        super().__init__()
        self._dag_service_url = dag_service_url.rstrip("/")
        self._task_completed_endpoint = f"{dag_service_url}/task-completed"
        self._register_task_processed_event_handler(self._handle_task_processed_event)

    async def _handle_task_processed_event(self, payload: Dict[str, Any]) -> None:
        """Handle a task completed event.

        Args:
            payload: Task data including old_task_state and new_task_state
        """
        task = payload.get("new_task_state")
        if not task.get("metadata", {}).get("dag", {}).get("id"):
            return

        await post_data(self._task_completed_endpoint, data=payload)
