# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Controller Bay Capacity Facilites."""

from typing import Dict, List, Tuple

from . import BaseBays

from nv.svc.farm.utils import post_data


class CapacityBasedBay(BaseBays):
    """Capacity based bay."""

    def __init__(self, capacity_service_location: str, mandatory_capacity: List[str] = None) -> None:
        """
        Capacity based bay manager.

        Uses the agent's capacity service to determine available requirements for jobs to execute.

        Args:
            capacity_service_location (str): URI where the capacity service is available.
            mandatory_capacity (str): On top of the jobs capacity requirements also verify that there
                is capacity available for the items that are mandatory.
                This can be used for example to have a hard limit for the amount of jobs running on a host.
        """
        super().__init__()
        self._capacity_service_location = capacity_service_location
        self._mandatory_capacity = mandatory_capacity or []

    async def get_capacity(self, tasks: Dict[Tuple[str, str], List[int]], job_definitions: List[Dict]) -> Tuple[List, Dict]:
        """
        Get list of tasks and the capacity available to currently run on the agent.

        Args:
            tasks (Dict[Tuple[str, str], List[int]]): List of currently active tasks and their types.
            job_definitions (List[Dict]): A list of the available jobs an agent can run.
        """
        capacities = await post_data(f"{self._capacity_service_location}/list", data={"available": True})
        if not capacities:
            return [], {}

        available_capacities = {capacity["identifier"]: capacity for capacity in capacities}
        available_tasks = []

        for job_definition in job_definitions:
            capacity_requirements = job_definition["capacity_requirements"]
            if all(key in available_capacities for key in capacity_requirements.keys()) and \
                    all(key in available_capacities for key in self._mandatory_capacity):
                available_tasks.append((job_definition["name"], job_definition["task_function"]))

        return available_tasks, available_capacities
