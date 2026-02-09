# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Agents Service Memory Manager Facility."""

import time
import typing

from .base import BaseAgentManager


class DictAgentManager(BaseAgentManager):
    """In memory agent manager."""

    def __init__(self, check_interval: int, lost_timeout: int, farm_tasks_address: str) -> None:
        super().__init__(check_interval, lost_timeout, farm_tasks_address)
        self._agents = {}
        self._logs: typing.Dict[str, typing.Dict[str, typing.Dict[str, str]]] = {}

    async def list(self, status: str = None) -> dict:
        if not status:
            return self._agents

        return {agent_id: agent_data for agent_id, agent_data in self._agents.items() if agent_data["status"] == status}

    async def update(
        self,
        agent_id: str,
        active_tasks: typing.List = None,
        task_types: typing.List = None,
        resources: typing.Dict = None,
        errored_task_count: int = None,
        labels: typing.List = None,
    ) -> typing.Dict:
        agent_data = {
            "active_tasks": active_tasks or [],
            "task_types": task_types or [],
            "checkin_time": time.time(),
            "status": "active" if active_tasks else "idle",
            "resources": resources or {},
            "errored_task_count": errored_task_count or 0,
            "labels": labels or []
        }
        return await self._update_agent_data(agent_id, agent_data)

    async def remove(self, agent_id: str, active_tasks: typing.List = None):
        await super().remove(agent_id, active_tasks=active_tasks)
        if agent_id in self._agents:
            self._agents.pop(agent_id)

    async def _update_agent_data(self, agent_id, agent_data) -> typing.Dict:
        if agent_id in self._agents:
            status = self._agents[agent_id].get("status", None)
            if status == "evicted":
                agent_data["status"] = "evicted"

        self._agents[agent_id] = agent_data
        return {"agent_id": agent_id, "status": agent_data["status"]}

    async def evict(self, agent_id: str):
        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "evicted"

    async def enable(self, agent_id: str):
        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "idle"
