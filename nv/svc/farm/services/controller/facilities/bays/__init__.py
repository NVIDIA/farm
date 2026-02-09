# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Bays Facilities."""

import abc
import json
import logging

from typing import Dict, List, Tuple

# flake8: noqa: B027

class BaseBays(abc.ABC):
    """Base class for bays."""

    def __init__(self) -> None:
        self._used = []

    @abc.abstractmethod
    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict]) -> Tuple[List, Dict]:
        """
        Get list of tasks and the capacity available to currently run on the agent.

        Args:
            tasks (Dict[Tuple[str, str], List[int]]): List of currently active tasks and their types.
            job_definitions (List[Dict]): A list of the available jobs an agent can run.
        """
        pass

    async def acquire(self, process, capacities):
        """
        Acquire a slot for the given process.

        Args:
            process (Any): Process for which to assign a slot.
            capacities (List[str]): List of capacities to assign to the process.
        """
        pass

    async def release(self, process, capacities):
        """
        Release the slot and capacities used by the given process.

        Args:
            process (Any): Process for which to assign a slot.
            capacities (List[str]): List of capacities to assign to the process.
        """
        pass


class OneSlotBay(BaseBays):
    """One-slot bay."""

    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict]) -> Tuple[List, Dict]:
        """
        Return the capacity for the given tasks.

        Args:
            tasks (Dict): Tasks for which to return the capacity.

        Returns:
            (List, Dict): Capacity for the given tasks.

        """
        task_types = []
        capacity = {}
        for task_type, values in tasks.items():
            if len(values) > 0:
                return [], {}

            task_types.append(task_type)

        return task_types, capacity


class MultiSlotBay(BaseBays):
    """Multi slot bay."""

    def __init__(self, max_capacity: int) -> None:
        super().__init__()
        self._max_capacity = max_capacity

    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict]) -> Tuple[List, Dict]:
        """
        Return the capacity for the given tasks.

        Args:
            tasks (Dict): Tasks for which to return the capacity.

        Returns:
            (List, Dict): Capacity for the given tasks.

        """
        task_types = []
        capacity = {}

        total_usage = 0
        for values in tasks.values():
            total_usage += len(values)

        for task_type, _values in tasks.items():
            if total_usage >= self._max_capacity:
                return [], {}

            task_types.append(task_type)

        return task_types, capacity


class FileBasedMultiSlotBay(MultiSlotBay):
    """File based multi slot bay."""

    def __init__(self, capacity_file: str) -> None:
        max_capacity = self._get_capacity_limit(capacity_file)
        logging.debug(f"Loaded capacity file '{capacity_file}', with max_capacity '{max_capacity}'.")
        super().__init__(max_capacity)

        self._capacity_file = capacity_file

    def _get_capacity_limit(self, capacity_file) -> int:
        try:
            with open(capacity_file, mode="r") as file:
                data = json.load(file)
                return data["max_capacity"]
        except Exception as exc:
            logging.error(f"Failed to load capacity from {capacity_file}. {str(type(exc))}, {str(exc)}")

        return 0

    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict]) -> Tuple[List, Dict]:
        self._max_capacity = self._get_capacity_limit(self._capacity_file)
        return await super().get_capacity(tasks, job_definitions)
