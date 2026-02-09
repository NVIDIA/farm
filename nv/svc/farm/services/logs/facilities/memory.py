# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Logs Service Memory Log Store Facility."""

import time
import typing
from collections import OrderedDict, deque


from nv.svc.farm.services.logs.config import FarmLogsConfig
from nv.svc.farm.services.logs.facilities.base import BaseLogStore


class TaskLogDeque:
    """Task Log Deque."""

    def __init__(self, maxlen: int):
        """Task Log Deque constructor."""
        now: float = time.time()
        self.last_agent: str = ""
        self.created: float = now
        self.updated: float = now
        self.logs: deque[str] = deque(maxlen=maxlen)


class MemoryLogStore(BaseLogStore):
    """In memory log store."""

    def __init__(self) -> None:
        """Memory log store constructor."""
        super().__init__()
        self._logs: OrderedDict[str, TaskLogDeque] = OrderedDict()

        config = FarmLogsConfig(auto_configure_logging=False)
        self._max_tasks = config.logs.max_tasks
        self._max_log_entries = config.logs.max_log_entries

    async def get_logs(
        self, task_id: str, agent_id: typing.Optional[str] = None, latest_only: bool = True, log_entries: int = 50
    ) -> typing.Dict[str, typing.Any]:
        """
        Return the logs for the given task running on the given agent.

        Args:
            task_id (str): Unique identifier of the task for which to return the logs.
            agent_id (str): Ignored.

        Kwargs
            latest_only (str): Ignored.
            log_entries (int): Ignored.

        Returns:
            Dict: Metadata information about the logs for the given task.

        """

        if task_id not in self._logs:
            raise KeyError(f"No logs found for Task {task_id}.")

        task_logs = self._logs[task_id]
        logs = {"created_at": task_logs.created, "updated_at": task_logs.updated, "logs": "".join(task_logs.logs)}
        return logs

    async def set_logs(self, agent_id: str, task_id: str, logs: str) -> None:
        """
        Record logs for the given task running on the given agent.

        Args:
            agent_id (str): Ignored.
            task_id (str): Unique identifier of the task for which logs should be persisted.
            logs (str): Logs to persist about the given task.

        Returns:
            None

        """

        if task_id not in self._logs:
            # we've exceeding the number of logs that we'll track, so remove some
            while len(self._logs) > self._max_tasks:
                self._logs.popitem(last=False)

            self._logs[task_id] = TaskLogDeque(maxlen=self._max_log_entries)
        else:
            self._logs[task_id].updated = time.time()

        if agent_id and self._logs[task_id].last_agent != agent_id:
            self._logs[task_id].logs.append(f"\n#### Agent ID: {agent_id}\n" + logs)
            self._logs[task_id].last_agent = agent_id
        else:
            self._logs[task_id].logs.append(logs)

        self._logs.move_to_end(task_id)
