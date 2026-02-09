# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Tasks Event Handlers."""

import asyncio
from collections import defaultdict
from dataclasses import asdict, dataclass
import logging
from typing import Callable, Dict, Any

from nv.svc.farm.services.tasks.utils import status_utils


@dataclass
class _TaskEventQueueItem:
    """Queue item for task events.

    Attributes:
        type: The type of event
        payload: The event payload containing task data
    """

    type: str
    payload: Dict[str, Any]


class BaseTaskEventHandler():
    """
    Processes Task Events according to their registered handler functions.

    Handler functions must accept the Task Dict for processing.
    """

    def __init__(self):
        self._stop_event = asyncio.Event()
        self._event_queue = asyncio.Queue()
        # mapping from event type to event handlers
        # e.g { "some_event_type": [FuncSendEmail, FuncSendSlackUpdate] }
        self._event_handlers = defaultdict(list)

    @property
    def event_handlers(self):
        """Retrieve all event handlers."""
        return self._event_handlers

    def push_event(self, event_type: str, old_task_state: Dict, new_task_state: Dict) -> None:
        if not self.event_handler_exists(event_type, old_task_state):
            return

        payload = {
            "old_task_state": old_task_state,
            "new_task_state": new_task_state
        }

        event = _TaskEventQueueItem(event_type, payload)

        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            logging.warning(f"QueueFull dropping event {asdict(event)}")

    def _register_event_handler(self, event_type: str, handler: Callable) -> None:
        self._event_handlers[event_type].append(handler)

    def _register_status_event_handler(self, status: status_utils.Status, handler: Callable) -> None:
        self._register_event_handler(f"status_{status.value}", handler)

    def _register_status_errored_event_handler(self, handler: Callable) -> None:
        """Register a handler for task error events.

        Args:
            handler: Async callable that takes a task dict as its only argument
        """
        self._register_status_event_handler(status_utils.Status.errored, handler)

    def _register_task_processed_event_handler(self, handler: Callable) -> None:
        """Register a handler for task processed events.

        Args:
            handler: Async callable that takes a task dict as its only argument
        """
        for status in status_utils.get_processed_status_list():
            self._register_status_event_handler(status, handler)

    def event_handler_exists(self, event_type: str, task_info: Dict = None) -> bool:
        return event_type in self.event_handlers

    async def _process_event(self, event: _TaskEventQueueItem) -> None:
        logging.info(f"Processing task event: {asdict(event)}")

        handlers = self._event_handlers.get(event.type)
        if not handlers:
            logging.warning(f"Skipping event, no handlers exist. {asdict(event)}")
            return

        for handler in handlers:
            try:
                await handler(payload=event.payload)
            except Exception as exc:
                logging.error(f"Failed processing task event {asdict(event)} with handler {type(handler)}. {str(type(exc))}: {str(exc)}")

    async def start(self) -> None:
        """Start the event handler runtime."""

        while not self._stop_event.is_set():
            try:
                # waits until there's an event.
                event = await self._event_queue.get()
                await self._process_event(event)
                self._event_queue.task_done()
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logging.error(f"Failed checking event queue. {str(type(exc))}: {str(exc)}")

    async def stop(self) -> None:
        """Stop the event handler runtime."""

        self._stop_event.set()
