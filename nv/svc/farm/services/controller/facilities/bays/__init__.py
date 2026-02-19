# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Bays Facilities."""

import abc
import json
import logging

from typing import Dict, List, Tuple, Optional, Any

# flake8: noqa: B027

class BaseBays(abc.ABC):
    """Base class for bays."""

    def __init__(self) -> None:
        self._used = []

    @abc.abstractmethod
    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict], taskid_to_job_definition_map: Dict[int, str] = {}) -> Tuple[List, Dict]:
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

    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict], taskid_to_job_definition_map: Dict[int, str] = {}) -> Tuple[List, Dict]:
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


    def _get_gpu_count(self, gpu_instance_type: Optional[str]) -> int:
        """Get the number of GPUs for a given GPU instance type.

        Args:
            gpu_instance_type (str): The GPU instance type name to parse for the number of GPUs which are required by this task.

        Returns:
            int: The extracted number of GPUs for the given GPU instance type, or default to 1 when the number of GPUs cannot be determined.
        """

        if not gpu_instance_type:
            return 1

        try:
            gpu_count = int(gpu_instance_type.rsplit("_", 1)[1].rstrip("x"))
            return gpu_count
        except (ValueError, IndexError):
            pass

        return 1


    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict[str, Any]], taskid_to_job_definition_map: Dict[int, str] = {}) -> Tuple[List, Dict]:
        """
        Return the capacity for the given tasks.

        Args:
            tasks (Dict): Tasks for which to return the capacity.

        Returns:
            (List, Dict): Capacity for the given tasks.

        """
        task_tuples = []
        capacity = {}

        # build the gpu usage map
        # BUG: we should really be using underlying capacities since those can differentiate cpu, gpu, memory
        # .. so this is a massive simplification of the model.
        gpu_usage_map: Dict[str, int] = {}
        for job_def in job_definitions:
            gpu_usage_map[job_def.get("name", "")] = self._get_gpu_count(
                job_def.get("capacity_requirements", {}).get("gpuSpecification", {}).get("instanceType"))

        total_usage = 0
        for task_tuple, task_ids in tasks.items():
            for task_id in task_ids:
                task_gpu_count = 1
                task_job_definition = taskid_to_job_definition_map.get(task_id)
                if task_job_definition:
                    task_gpu_count = gpu_usage_map.get(task_job_definition, 1)

                total_usage += task_gpu_count

                if total_usage >= self._max_capacity:
                    return [], {}

            task_tuples.append(task_tuple)

        return task_tuples, capacity


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

    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict], taskid_to_job_definition_map: Dict[int, str] = {}) -> Tuple[List, Dict]:
        self._max_capacity = self._get_capacity_limit(self._capacity_file)
        return await super().get_capacity(tasks, job_definitions, taskid_to_job_definition_map)
