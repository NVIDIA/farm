# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Agents Service Base Manager Facility."""

import abc
import asyncio
import logging
import time
import typing

from nv.svc.core.facilities import base

from nv.svc.farm.utils import fetch_data, post_data


class BaseAgentManager(abc.ABC, base.Facility):
    """Base implementation for agent management."""

    def __init__(self, check_interval: int, lost_timeout: int, farm_tasks_address: str) -> None:
        super().__init__()
        if check_interval > lost_timeout:
            raise Exception(
                f"The check_interval {check_interval} cannot be greater "
                f"than the lost_timeout {lost_timeout}."
            )
        self._lost_timeout = lost_timeout
        self._check_interval = check_interval
        self._stop_event = asyncio.Event()
        self._farm_tasks_address = farm_tasks_address.rstrip("/")
        self._sem = asyncio.Semaphore(5)

    @abc.abstractmethod
    async def list(self, status: str = None) -> dict:
        pass

    @abc.abstractmethod
    async def update(
        self,
        agent_id: str,
        active_tasks: typing.List = None,
        task_types: typing.List = None,
        resources: typing.Dict = None,
        errored_task_count: int = None,
        labels: typing.List = None
    ) -> typing.Dict:
        """
        Update the status of a given agent.

        Args:
            agent_id (str): Unique identifier for the given agent.

        Kwargs:
            active_tasks (List[str]): List of active tasks this agent is processing.
            task_types (List[str]): List of task types this agent can process.
            resources (Dict): Resources available to this agent.
            errored_task_count (int): Count of failed tasks.
            labels (List[str]): List of labels associated with agent.

        Returns:
            Dict: Dictionary containing the agent_id and agent_status.

        """
        pass

    @abc.abstractmethod
    async def _update_agent_data(self, agent_id, agent_data) -> typing.Dict:
        pass

    async def remove(self, agent_id: str, active_tasks: typing.List = None):
        """
        Remove an agent that was lost and fail its tasks.

        Args:
            agent_id: (str): Unique identifier for the given agent

        Kwargs:
            active_tasks (List[str]): List of tasks this agent had been working on
        """
        active_tasks = active_tasks or []
        tasks_to_error = []
        for task_id in active_tasks:
            task = asyncio.create_task(self._fail_active_task(task_id, agent_id, f"agent {agent_id} was shutdown. Failing task."))
            tasks_to_error.append(task)
        await asyncio.gather(*tasks_to_error)

    @abc.abstractmethod
    async def evict(self, agent_id: str):
        """
        Evict an agent and prevent it from taking on new tasks.

        Args:
            agent_id: (str): Unique identifier for the given agent
        """
        pass

    @abc.abstractmethod
    async def enable(self, agent_id: str):
        """
        Enable an agent and allow it to take on new tasks.

        Args:
            agent_id: (str): Unique identifier for the given agent
        """
        pass

    async def _check(self, lost_timeout: int):
        agents = {}
        timeout = time.time()

        agents = await self.list()

        for agent_id, agent_data in agents.items():
            if agent_data["checkin_time"] + lost_timeout < timeout and not agent_data["status"] == "lost":
                agent_data["status"] = "lost"
                active_tasks = agent_data["active_tasks"]

                tasks_to_error = []
                for task_id in active_tasks:
                    task = asyncio.create_task(self._fail_active_task(task_id, agent_id, f"agent {agent_id} was lost. Failing task."))
                    tasks_to_error.append(task)
                await asyncio.gather(*tasks_to_error)

                agent_data["active_tasks"] = []
                await self._update_agent_data(agent_id, agent_data)

    async def _fail_active_task(self, task_id: str, agent_id: str, reason: str):
        async with self._sem:
            task_details = None
            try:
                task_details = await fetch_data(f"{self._farm_tasks_address}/info/{task_id}")
            except Exception as exc:
                logging.warning(f"Failed to retrieve task details for task {task_id}. {str(type(exc))}: {str(exc)}")
                return

            if not task_details:
                logging.warning(f"No task found for {task_id}")
                return

            try:
                await self._update_task_to_errored(task_id, task_details, agent_id, reason)
            except Exception as exc:
                logging.warning(f"Failed to update task {task_id}. {str(type(exc))}: {str(exc)}")

    async def _update_task_to_errored(self, task_id: str, task_details: typing.Dict, agent_id: str, reason: str):
        data = dict(
            task_id=task_id,
            task_type=task_details["task_type"],
            task_function=task_details["task_function"],
            status="errored",
            task_comment=task_details["task_comment"],
            progress={
                "current_step_index": 0,
                "total_step_count": 0,
                "progress": 0.0,
                "status_message": reason
            },
            agent_id=agent_id,
            userid=task_details["userid"]
        )
        await post_data(f"{self._farm_tasks_address}/update", data=data)

    async def run(self):
        while not self._stop_event.is_set():
            try:
                await self._check(self._lost_timeout)
            except Exception as exc:
                logging.warning(f"Failed to run agent checks. {str(type(exc))}: {str(exc)}")
            await asyncio.sleep(self._check_interval)

    def stop(self):
        self._stop_event.set()
