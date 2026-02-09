# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Agents Service Redis Manager Facility."""

import json
import time
import typing

import redis.asyncio as redis

from .base import BaseAgentManager


class RedisAgentManager(BaseAgentManager):
    """Redis memory agent manager."""

    # TODO: Break up this data structure to take advantage of Redis data structures.

    def __init__(self, check_interval: int, lost_timeout: int, farm_tasks_address: str, connection_string: str = None) -> None:
        super().__init__(check_interval, lost_timeout, farm_tasks_address)
        self._agent_key_prefix = "agent_"
        self._redis = redis.from_url(connection_string)

    async def list(self, status: str = None) -> dict:
        agents = {}
        async for key in self._redis.scan_iter(match=f"{self._agent_key_prefix}*"):
            data = await self._redis.get(key)
            if data:
                agent_id = key.decode("utf-8") if hasattr(key, "decode") else key
                agent_id = agent_id.replace(self._agent_key_prefix, "")
                agents[agent_id] = json.loads(data)

        if not status:
            return agents

        return {agent_id: agent_data for agent_id, agent_data in agents.items() if agent_data["status"] == status}

    async def update(
        self,
        agent_id: str,
        active_tasks: typing.List = None,
        task_types: typing.List = None,
        resources: typing.Dict = None,
        errored_task_count: int = None,
        labels: typing.List = None,
    ) -> typing.Dict:
        data = {
            "active_tasks": active_tasks or [],
            "task_types": task_types or [],
            "checkin_time": time.time(),
            "status": "active" if active_tasks else "idle",
            "resources": resources or {},
            "errored_task_count": errored_task_count or 0,
            "labels": labels or [],
        }

        # Don't allow an agent to reset its own status.
        if not data["status"] == "evicted":
            existing_data = await self._get_agent_data(agent_id)
            if existing_data and existing_data.get("status", "") == "evicted":
                data["status"] = "evicted"

        await self._store_agent_data(agent_id, data)
        return {"agent_id": agent_id, "status": data["status"]}

    async def _store_agent_data(
        self,
        agent_id: str,
        data: typing.Dict,
        expiry: int = None,
        store_when_not_exists: bool = False,
        store_when_exists: bool = False
    ):
        """
        Store the agent data.

        Args:
            agent_id (str): Id of the agent.
            data (dict): Data to store, will be stored as a JSON blob.
            expiry (int): Set key expiry time in seconds
            store_when_not_exists (bool): Only store data if the key does not yet exist.
            store_when_exists (bool): Only store data if the key already exists.
        """
        await self._redis.set(
            self._get_agent_key(agent_id),
            json.dumps(data),
            ex=expiry,
            nx=store_when_not_exists,
            xx=store_when_exists
        )

    def _get_agent_key(self, agent_id: str) -> str:
        """
        For creating the agent key.

        Args:
            agent_id (str): Unique identifier of the agent.
        """
        return f"{self._agent_key_prefix}{agent_id}"

    async def remove(self, agent_id: str, active_tasks: typing.List = None):
        await super().remove(agent_id, active_tasks=active_tasks)
        await self._redis.delete(self._get_agent_key(agent_id))

    async def evict(self, agent_id: str):
        data = await self._get_agent_data(agent_id)
        if not data:
            return

        data["status"] = "evicted"
        await self._update_agent_data(agent_id, data)

    async def enable(self, agent_id: str):
        data = await self._get_agent_data(agent_id)
        if not data or data["status"] != "evicted":
            return

        data["status"] = "idle"
        await self._update_agent_data(agent_id, data)

    async def _get_agent_data(self, agent_id: str) -> typing.Dict:
        """
        Retrieve the agent data for a given agent_id.

        Args:
            agent_id (str): Unique identifier of the agent.
        """
        key = self._get_agent_key(agent_id)
        data = await self._redis.get(key)
        if data:
            data = json.loads(data)

        return data

    async def _update_agent_data(self, agent_id, agent_data) -> typing.Dict:
        # Only set the value if the key still exists.
        # Will avoid race conditions if agent has gone offline since.
        await self._store_agent_data(agent_id, agent_data, store_when_exists=True)
        return {"agent_id": agent_id, "status": agent_data["status"]}
