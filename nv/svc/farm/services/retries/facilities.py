# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Retries Service Facilities."""

import logging
from datetime import datetime
from typing import Dict, List

from nv.svc.core.facilities import base
from nv.svc.farm.utils import post_data


class RetryManager(base.Facility):
    """Retry Manager Facility."""

    def __init__(
        self,
        farm_tasks_address: str,
        retry_limit: int,
        task_max_age: int,
        task_type_blocklist: List[str],
        task_function_blocklist: List[str],
    ):
        """Init.

        Kwargs:
            retry_limit (int): Maximum number of allowed retries.
            task_max_age (int): Tasks that are older than this setting are skipped (use 0 to consider all regardless of age).
            task_type_blocklist (list): Tasks containing a blocklisted task types are skipped.
            task_function_blocklist (list): Tasks containing a blocklisted task functions are skipped.
        """
        self._retry_limit = retry_limit
        self._task_max_age = task_max_age
        self._task_type_blocklist = task_type_blocklist
        self._task_function_blocklist = task_function_blocklist
        self._farm_tasks_address = farm_tasks_address
        self._farm_tasks_retry_endpoint = f"{self._farm_tasks_address.rstrip('/')}/retry"
        self._farm_tasks_update_endpoint = f"{self._farm_tasks_address.rstrip('/')}/update"

    def _is_task_retryable(self, task: Dict) -> bool:
        is_retryable = False
        current_time_utc = datetime.timestamp(datetime.utcnow())
        task_id = task["task_id"]
        retry_metadata = task.get("metadata", {}).get("_retry", {})
        retry_count = retry_metadata.get("count", 0)
        retry_limit = retry_metadata.get("limit", self._retry_limit)
        task_age_seconds = int(current_time_utc - task["task_submission_time"])

        if not retry_metadata.get("is_retryable", True):
            logging.debug(f"Skipping {task_id}, because it is not retryable.")
        elif retry_count >= retry_limit:
            logging.debug(f"Skipping {task_id}, no more retries left.")
        elif task["task_type"] and task["task_type"] in self._task_type_blocklist:
            logging.debug(f"Skipping {task_id}, due to blocklisted task type.")
        elif task["task_function"] and task["task_function"] in self._task_function_blocklist:
            logging.debug(f"Skipping {task_id}, due to blocklisted task function.")
        elif self._task_max_age != 0 and task_age_seconds > self._task_max_age:
            logging.debug(f"Skipping {task_id}, because it is older than {self._task_max_age} seconds.")
        elif retry_count < retry_limit:
            is_retryable = True

        return is_retryable

    async def update_task(self, task: Dict) -> None:
        """Update the task in the Tasks Service."""
        try:
            await post_data(self._farm_tasks_update_endpoint, data=task)
        except Exception as exc:
            logging.error(f"Task update failed for task {task['task_id']}. {str(type(exc))}: {str(exc)}")
            raise Exception(f"Task update failed for task {task['task_id']}.")

    async def retry_task(self, task: Dict) -> None:
        """Retry a Task via the Tasks Service Retry endpoint."""
        task_id = task["task_id"]
        task_metadata = task.get("metadata", {})

        # initialize retry metadata if missing
        retry_metadata = task_metadata.get("_retry", {})

        if retry_metadata.get("is_done", False):
            logging.info(f"Task {task_id} is already done, skipping")
            return

        is_done = self._is_task_retryable(task) is False
        retry_metadata["is_done"] = is_done
        retry_metadata["count"] = retry_metadata.get("count", 0) + 1
        retry_metadata["limit"] = retry_metadata.get("limit", self._retry_limit)
        # is_retryable is a user set field to enable task retries
        retry_metadata["is_retryable"] = retry_metadata.get("is_retryable", True)
        task_metadata["_retry"] = retry_metadata

        updated_fields = {
            "metadata": task_metadata,
            "userid": task["userid"],
            "details": f"Task errored. Retry attempt {retry_metadata['count']} of {retry_metadata['limit']}",
        }
        task.update(updated_fields)

        if is_done:
            logging.info(f"Task {task_id} is done, updating task metadata")
            await self.update_task(task)
            return

        logging.info(f"Sending retry request ({retry_metadata['count']} of {retry_metadata['limit']}) for task id: {task_id}")

        try:
            await post_data(self._farm_tasks_retry_endpoint, data=task)
        except Exception as exc:
            logging.error(f"Retry request failed for task {task_id}. {str(type(exc))}: {str(exc)}")
            raise Exception(f"Retry request failed for task {task_id}.")
