# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Tasks Status Event Handler."""

from typing import Dict

from .base import BaseTaskEventHandler

from nv.svc.farm.utils import post_data


class TaskStatusEventHandler(BaseTaskEventHandler):
    """Task status event handler, handles events per task status."""

    def __init__(self, retries_service_url: str):
        super().__init__()

        self._retries_submit_endpoint = f"{retries_service_url.rstrip('/')}/submit"
        self._register_status_errored_event_handler(self._handle_status_errored_event)

    async def stop(self) -> None:
        await super().stop()

    async def _handle_status_errored_event(self, payload: Dict) -> None:
        """Handle a task error event.

        Args:
            payload: Task data including old_task_state and new_task_state
        """
        new_task_state = payload.get("new_task_state", {})
        is_done = new_task_state.get("metadata", {}).get("_retry", {}).get("is_done", False)

        if is_done:
            return

        await post_data(self._retries_submit_endpoint, data=payload)
