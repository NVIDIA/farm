# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Logs Service Base Log Store Facility."""

import abc
import typing

from nv.svc.core.facilities import base


class BaseLogStore(abc.ABC, base.Facility):
    """Base implementation for log store."""

    def __init__(self) -> None:
        """Log Store constructor."""
        super().__init__()

    @abc.abstractmethod
    async def get_logs(self, task_id: str, agent_id: str = None, latest_only: bool = True, log_entries: int = 50) -> typing.Dict:
        """
        Return the logs for the given task running on the given agent.

        TODO:
            * This might be more appropriately persisted at the task level instead of at the Agent level, in order to
              avoid keeping logs in memory and to allow for long-term log storage should a session be closed.
            * In addition, this does not currently preserve the log history should a same task be retried on the same
              agent. This can happen, for example, in the case of a failed task that was retried. Logs of previous
              sessions would then be overwritten.

        Args:
            agent_id (str): Unique identifier of the agent running the task for which to return the logs.
            task_id (str): Unique identifier of the task for which to return the logs.

        Kwargs:
            latest_only (bool): In the case where the task ran on multiple agents, only return the log issued by the most
                recent run. Default: True
            log_entries (int): Amount of log entries to return. Default: 50

        Returns:
            Dict: Metadata information about the logs.

        """
        pass

    @abc.abstractmethod
    async def set_logs(self, agent_id: str, task_id: str, logs: str) -> None:
        """
        Record the logs for the given task running on the given agent.

        Args:
            agent_id (str): Unique identifier of the agent running the task for which to record the logs.
            task_id (str): Unique identifier of the task for which to record the logs.
            logs (str): Content of the log for the given task running on the given agent.

        Returns:
            None

        """
        pass

    def stop(self):
        """Perform any clean up that might be required."""
        pass
