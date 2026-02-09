# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Standard in-memory lossy Task backend persistence solution."""

import abc
import asyncio
from collections import deque, OrderedDict
from contextlib import asynccontextmanager
import re
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import uuid

from .task_revision import TaskRevision


class InvalidTaskFieldException(Exception):
    """Exception when a passed in field filter is not a valid task field."""

    pass


class InvalidLabelError(Exception):
    """Raised when invalid labels are detected."""

    pass


class BaseTaskBackend(abc.ABC):
    """Base class for all Task backend persistence solutions, and the CRUD operations associated to them."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        # Only accept letters, numbers, dashes, underscores and periods.
        self._regex = r"[a-zA-Z0-9-_\s\.]+$"

    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    async def get_task(
        self,
        task_id: Optional[str] = None,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> Dict:
        """
        Return the unique task matching the given search criterias.

        Args:
            task_id (Optional[str]): Unique identifier of the task to return.
            task_type (Optional[str]): Type of the task to return.
            task_function (Optional[str]): Function of the task to return.

        Returns:
            Dict: Metadata information about the task to retrieve.

        Raises:
            KeyError: Raised when no result could be found matching the given search criterias.

        """
        pass

    def validate_labels(self, labels: Optional[List[str]]) -> None:
        """Validate all labels in a list."""

        if not labels:
            return

        invalid_labels = []
        for label in labels:
            if not re.match(self._regex, label):
                invalid_labels.append(label)

        if invalid_labels:
            message = f"Invalid labels that do not follow the regex {self._regex} were deteced: {str(invalid_labels)}"
            raise InvalidLabelError(message)

    @abc.abstractmethod
    async def get_task_revision_history(self, task_id: str,) -> List[TaskRevision]:
        """
        Return the list of revisions to the given task, ordered chronologically.

        Args:
            task_id (str): Unique identifier of the task for which to return the revision history.

        Returns:
            List[TaskRevision]: List of revisions applied to the given task.

        """
        pass

    @abc.abstractmethod
    async def get_tasks(
        self,
        task_type: str,
        task_function: str,
        capacity: Optional[Dict] = None,
        statuses: List[str] = ["submitted"],  # noqa
        fields: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Return the list of all rows matching the given search criterias.

        Args:
            task_type (str): Type of the tasks to return.
            task_function (str): Function of the tasks to return.
            capacity (Optional[Dict]): Capacity of the tasks to return.
            statuses (List[str]): List of task statuses to return.
            fields (Optional[List[str]]): Optional list of fields to include in the result. Default is to include all fields.

        Returns:
            List[Dict]: List of metadata information about the tasks to retrieve.

        """
        pass

    async def get_status(
        self,
        task_id: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> str:
        """
        Return the status of the task matching the given search criterias.

        Args:
            task_id (str): Unique identifier of the task whose status should be returned.
            task_type (Optional[str]): Type of task whose status should be returned.
            task_function (Optional[str]): Function of the task whose status should be returned.

        Returns:
            str: The status of the task matching the given search criterias.

        """
        task = await self.get_task(task_id=task_id, task_type=task_type, task_function=task_function)
        return task["status"]

    @abc.abstractmethod
    async def update_task(
        self,
        task_id: str,
        userid: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        status: Optional[str] = None,
        details: Optional[str] = None,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        agent_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> None:
        """
        Update the task matching the given search criterias.

        ..note::

            Contrary to the workflow of adding a new task, updating a task does not automatically call the
            `_save_task_revision_history()` method of the backend.

            For performance reasons, implementors should instead opt in to calling this method themselves, at the
            appropriate time, in order to preserve the event history of updates to the task.

        Args:
            task_id (str): Unique identifier of the task which needs to be updated.
            task_type (str): Type of the task which needs to be updated.
            task_function (str): Function of the task which needs to be updated.
            status (str): New status of the task which needs to be updated.
            userid (str): Unique identifier of the user who requested the update to the task.
            details (Optional[str]): Details about the task which needs to be updated.
            metrics (Optional[str]): Metrics metadata about the task which needs to be updated.
            progress (Optional[Dict]): Progress metadata about the task which needs to be updated.
            agent_id (Optional[str]): Unique identifier of the agent which performed the update to the task.
            task_comment (Optional[str]): Comment about the task.
            task_function_args (Optional[Dict[str, Any]]): Arguments to supply to the task function.
            priority (Optional[int]): Priority of the task (0 being the highest priority)
            metadata (Optional[Dict]): Any additional information required for this task (ie: list of extensions)
            labels (Optional[List]): Task labels that will steer them towards specific agents

        Returns:
            None

        """
        pass

    async def add_task(
        self,
        status: str,
        task_type: str,
        userid: str,
        task_args: Optional[Dict] = None,
        task_function: Optional[str] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_submission_time: Optional[int] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> str:
        """
        Add the given task metadata to the storage option.

        Args:
            status (str): Status of the task to add.
            task_type (str): Type of the task to add.
            userid (str): Unique identifier of the User who added the task.
            task_args (Optional[Dict]): Arguments of the task.
            task_function (Optional[str]): Function of the task to add.
            task_function_args (Optional[Dict]): Arguments to supply to the task function.
            task_requirements (Optional[Dict]): Requirements for the task.
            task_id (Optional[str]): Unique identifier of the task to add.
            task_comment (Optional[str]): Comment about the task.
            task_submission_time (Optional[int]): Timestamp since epoch this task was added.
            priority (Optional[int]): Priority of the task (0 being the highest priority)
            metadata (Optional[Dict]): Any additional information required for this task (ie: list of extensions)
            labels (Optional[List]): Task labels that will steer them towards specific agents

        Returns:
            str: The unique identifier of the task that was added.

        """
        task_id = await self._save_task(
            status=status,
            task_type=task_type,
            userid=userid,
            task_args=task_args,
            task_function=task_function,
            task_function_args=task_function_args,
            task_requirements=task_requirements,
            task_id=task_id,
            task_comment=task_comment,
            task_submission_time=task_submission_time,
            priority=priority,
            metadata=metadata,
            labels=labels
        )
        await self._save_task_revision(
            TaskRevision(
                task_id=task_id,
                status=status,
                userid=userid,
                agent_id=None,
                details=None,
                progress=None,
            )
        )
        return task_id

    @abc.abstractmethod
    async def _save_task(
        self,
        status: str,
        task_type: str,
        userid: str,
        task_args: Optional[Dict] = None,
        task_function: Optional[str] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_submission_time: Optional[int] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> str:
        """
        Save the given task metadata to the storage option.

        ..note::

            Implementors are expected to provide this `_save_task()` method to make state management easier to handle
            using higher levels of abstraction.

            For example, in the case of a newly-created task, adding a new task to a backend implementation will
            automatically call the current method, immediately followed by a call to `_save_task_revision_history()`, so
            that a initial snapshot of the task can be preserved for history, using the unique identifier of the
            newly-created task provided as return value of this method.

        Args:
            status (str): Status of the task to add.
            task_type (str): Type of the task to add.
            userid (str): Unique identifier of the User who added the task.
            task_args (Optional[Dict]): Arguments of the task.
            task_function (Optional[str]): Function of the task to add.
            task_function_args (Optional[Dict]): Arguments to supply to the task function.
            task_requirements (Optional[Dict]): Requirements for the task.
            task_id (Optional[str]): Unique identifier of the task to add.
            task_comment (Optional[str]): Comment about the task.
            task_submission_time (Optional[str]): Timestamp since epoch this task was submitted.
            priority (Optional[int]): Priority of the task (0 being the highest priority)
            metadata (Optional[Dict]): Any additional information required for this task (ie: list of extensions)
            labels (Optional[Dict]): Task labels that will steer them towards specific agents

        Returns:
            str: The unique identifier of the task that was added.

        """
        pass

    @abc.abstractmethod
    async def _save_task_revision(self, task_revision: TaskRevision,) -> None:
        """
        Store the task revision.

        Ensuring that we patch the revision_id with a unique identifier when storing the revision.

        The backends often are missing setters as any changes to a revision don't necessarily persist to the backend.
        sqlalchemy.core instances strictly forbid this and throw exceptions when attempting to directly mutate
        properties.

        Args:
            task_revision (TaskRevision): a task revision to store in the backend. Note that the revision_id class
                member will likely be overwritten by the backend on insert.

        Returns:
            None
        """

        pass

    @asynccontextmanager
    async def lock_transaction(self) -> AsyncGenerator[Any, None]:
        """
        Return an asynchronous context implementing a transaction on the backend storage.

        Args:
            None

        Returns:
            AsyncGenerator[Any, None]: An ``await``-able response to transaction request.

        """
        async with self._lock:
            yield

    @abc.abstractmethod
    async def get_highest_task_revision(self) -> Optional[int]:
        """
        Return the highest task revision ID from the backend revision log.

        Args:
            None

        Returns:
            int: An integer representing the primary key of the latest revision.
        """
        pass

    @abc.abstractmethod
    async def get_changed_tasks_between_revisions(self, after: int, ending_with: int) -> List[str]:
        """
        Return a list of unique task IDs that have changed over a contiguous span of revisions.

        Args:
            after (int): An integer representing the starting bound for the revision query. This should be the highest
                previously known revision ID that was observed. Revisions greater than this ID will be included, as it's
                expected that this revision would have been already processed in a previous batch and should be excluded
                to avoid being processed twice.
            ending_with (int): An integer representing the ending bound for the revision query. All revision up to and
                including this ID will be included in the query.

        Returns:
            List[str]: A list of unique task IDs that encompass the revisions found.
        """
        pass


class DictTaskBackend(BaseTaskBackend):
    """
    Simple in-memory backend.

    The backend uses a mapping of ``(task_type, task_function)`` items.

    """

    def __init__(self) -> None:
        super().__init__()
        self._data: Dict[Tuple[str, str], OrderedDict[str, Any]] = {}
        self._task_history: Dict[str, 'deque[TaskRevision]'] = {}
        self._revision_index: int = 0
        self._task_status_complete: List[str] = ["archived", "cancelled", "errored", "finished"]
        self._revisions_history_max = 1_000
        self._task_deletions_per_pass = 3
        self._task_history_max = 10_000

    async def start(self):
        pass

    async def get_task(
        self,
        task_id: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> Dict:
        if not task_id:
            raise KeyError("No task id provided")

        if task_type is None or task_function is None:
            for task_type, task_function in self._data.keys():
                try:
                    return await self._fetch_task(task_id, task_type, task_function)
                except KeyError:
                    continue
        else:
            return await self._fetch_task(task_id, task_type, task_function)

        raise KeyError(f"{task_id} not found")

    async def get_task_revision_history(self, task_id: str) -> List[TaskRevision]:
        if task_id not in self._task_history:
            raise KeyError(f"No revision history found for Task {task_id}.")

        return list(self._task_history.get(task_id, []))

    def _get_key(
        self,
        task_id: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Get the correct (task_type, task_function) tuple key for accessing self._data.

        Args:
            task_id: Optional task ID to find the bucket
            task_type: Optional task type for direct bucket access
            task_function: Optional task function for direct bucket access

        Returns:
            Tuple of (task_type, task_function)

        Raises:
            KeyError: If no matching bucket can be found
        """
        # If we have both task_type and task_function, use them directly
        if task_type is not None and task_function is not None:
            return (task_type, task_function)

        # Otherwise scan buckets to find which one contains the task_id
        if task_id is not None:
            for key, tasks in self._data.items():
                if task_id in tasks:
                    return key

        raise KeyError(f"Could not find bucket for task_id={task_id}, task_type={task_type}, task_function={task_function}")

    async def _fetch_task(
        self,
        task_id: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> Dict:
        key = self._get_key(task_id, task_type, task_function)
        return self._data[key][task_id]

    async def get_tasks(
        self,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        capacity: Optional[Dict] = None,
        statuses: List[str] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Dict]:
        if statuses is None:
            statuses = ["submitted"]

        # If task_type and task_function are None, return matching tasks from all buckets
        if task_type is None or task_function is None:
            matching_tasks = []
            for tasks in self._data.values():
                matching_tasks.extend(
                    task for task in tasks.values()
                    if task["status"] in statuses
                )
            return matching_tasks

        # Otherwise get tasks from specific bucket
        try:
            all_tasks = self._data[(task_type, task_function)]
            return [
                task for task in all_tasks.values()
                if task["status"] in statuses
            ]
        except KeyError:
            return []

    async def update_task(
        self,
        task_id: str,
        userid: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        status: Optional[str] = None,
        details: Optional[str] = None,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        agent_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> None:

        self.validate_labels(labels)

        # avoid throwing exceptions if the task is missing
        try:
            # avoid throwing exceptions if the task is missing
            selected_task = await self.get_task(task_id, task_type, task_function)
        except KeyError:
            return

        # Prevent race condition from updating a finished task back to running
        if status and status in ("starting", "running") and selected_task["status"] in ("finished", "errored"):
            return

        if status:
            selected_task["status"] = status
        if metrics:
            selected_task["metrics"] = metrics
        if progress:
            selected_task["progress"] = progress
        if task_comment:
            selected_task["task_comment"] = task_comment
        if task_function_args:
            selected_task["task_function_args"] = task_function_args
        if priority:
            selected_task["priority"] = priority
        if metadata:
            selected_task["metadata"] = metadata
        if labels:
            selected_task["labels"] = labels

        # move updated tasks to the end of the ordereddict, so they're least likely to be discarded
        key = (selected_task["task_type"], selected_task["task_function"])
        self._data[key].move_to_end(task_id)

        await self._save_task_revision(
            TaskRevision(
                task_id=task_id,
                status=status,
                userid=userid,
                agent_id=agent_id,
                details=details,
                progress=progress,
            )
        )

    async def _save_task(
        self,
        userid: str,
        status: str,
        task_type: str,
        task_function: str,
        task_args: Optional[Dict] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_submission_time: Optional[int] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> str:
        self.validate_labels(labels)

        task_id = task_id or str(uuid.uuid4())

        key = (task_type, task_function)

        if key not in self._data:
            self._data[key] = OrderedDict()
        else:
            # we're getting too big, so discard our oldest finished task along
            # with the associated task history.
            # always try to deleted more than we're adding (1 task added, up
            # to 3 deleted by default), since if we grow too large we'll
            # never get back under control.
            if len(self._data[key]) >= self._task_history_max:
                tasks_to_delete = []
                # scan from oldest to newest for items that we can delete and
                # fill out list of candidates in a single pass
                for _, task in self._data[key].items():
                    if len(tasks_to_delete) >= self._task_deletions_per_pass:
                        break
                    if task["status"] in self._task_status_complete:
                        tasks_to_delete.append(task["task_id"])
                for taskid_to_delete in tasks_to_delete:
                    del self._data[key][taskid_to_delete]
                    # also take our history with us
                    if taskid_to_delete in self._task_history:
                        del self._task_history[taskid_to_delete]

        self._data[key][task_id] = {
            "status": status,
            "task_id": task_id,
            "userid": userid,
            "task_type": task_type,
            "task_args": task_args or {},
            "task_function": task_function or "",
            "task_function_args": task_function_args or {},
            "task_requirements": task_requirements or {},
            "task_comment": task_comment or "",
            "task_submission_time": task_submission_time or time.time(),
            "metrics": "",
            "priority": priority or 65535,
            "progress": {
                "current_step_index": 0,
                "total_step_count": 0,
                "progress": 0.0,
                "status_message": "",
                "time_remaining": 0.0,
            },
            "metadata": metadata or {},
            "labels": labels or []
        }

        return task_id

    async def _save_task_revision(self, task_revision: TaskRevision) -> None:
        """See base class."""

        if task_revision.task_id not in self._task_history:
            self._task_history[task_revision.task_id] = deque(maxlen=self._revisions_history_max)

        self._revision_index += 1
        # patch the revision_id
        patched_revision: TaskRevision = TaskRevision(
            task_id=task_revision.task_id,
            status=task_revision.status,
            userid=task_revision.user_id,
            revision_id=self._revision_index,
            agent_id=task_revision.agent_id,
            details=task_revision.details,
            progress=task_revision.progress,
            time=task_revision.time,
        )
        self._task_history[task_revision.task_id].append(patched_revision)

    async def get_highest_task_revision(self) -> Optional[int]:
        """See base class."""
        return self._revision_index

    async def get_changed_tasks_between_revisions(self, after: int, ending_with: int) -> List[str]:
        """See base class."""
        # this is going to be expensive since we're walking all the revisions across all tasks
        matching_tasks = [
            revision.task_id
            for revisions in self._task_history.values()
            for revision in revisions
            if revision.revision_id and revision.revision_id > after and revision.revision_id <= ending_with
        ]

        return list(set(matching_tasks))

    async def update_tasks_status_bulk(
        self,
        task_ids: List[str],
        new_status: str,
    ) -> List[str]:
        """Update the status of multiple tasks in bulk.

        Args:
            task_ids: List of task IDs to update
            new_status: The new status to set

        Returns:
            List of task IDs that were successfully updated
        """
        updated_ids = []

        for task_id in task_ids:
            for _, values in self._data.items():
                if task_id not in values:
                    continue

                task = values[task_id]
                task["status"] = new_status
                updated_ids.append(task_id)
                await self._save_task_revision(
                    TaskRevision(
                        task_id=task_id,
                        status=new_status,
                        userid="system",
                        details="Status updated as part of bulk update",
                    )
                )
                break

        return updated_ids


class TaskIdDictBackend(BaseTaskBackend):
    """
    Simple in-memory backend.

    The backend uses a ``task_id`` mapping.

    """

    def __init__(self) -> None:
        super().__init__()
        self._data: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._task_history: Dict[str, 'deque[TaskRevision]'] = {}
        self._revision_index: int = 0
        self._task_status_complete: List[str] = ["archived", "cancelled", "errored", "finished"]
        self._revisions_history_max = 1_000
        self._task_deletions_per_pass = 3
        self._task_history_max = 10_000

    async def start(self):
        pass

    async def get_task(
        self,
        task_id: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> Dict:
        if not task_id:
            raise KeyError("No task id provided")

        task = self._data.get(task_id)

        if not task:
            raise KeyError(f"{task_id} not found.")

        if task_type is not None and task.get("task_type") != task_type:
            raise KeyError(f"{task_id} not found for ({task_type}, {task_function})")

        if task_function is not None and task.get("task_function") != task_function:
            raise KeyError(f"{task_id} not found for ({task_type}, {task_function})")

        return task

    async def get_task_revision_history(self, task_id: str,) -> List[TaskRevision]:
        if task_id in self._task_history:
            return list(self._task_history[task_id])
        raise KeyError(f"No revision history found for Task {task_id}.")

    async def get_tasks(
        self,
        task_type: str,
        task_function: str,
        capacity: Optional[Dict] = None,
        statuses: List[str] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Dict]:
        if statuses is None:
            statuses = ["submitted"]
        tasks = []

        for task in self._data.values():
            if task_type is not None and task.get("task_type", None) != task_type:
                continue

            if task_function is not None and task.get("task_function", None) != task_function:
                continue

            if task["status"] in statuses:
                tasks.append(task)

        return tasks

    async def update_task(
        self,
        task_id: str,
        userid: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        status: Optional[str] = None,
        details: Optional[str] = None,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        agent_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> None:
        self.validate_labels(labels)

        # Prevent race condition from updating a finished task back to running.
        if status and status in ("starting", "running") and self._data[task_id]["status"] in ("finished", "errored"):
            return

        if status:
            self._data[task_id]["status"] = status
        if metrics:
            self._data[task_id]["metrics"] = metrics
        if progress:
            self._data[task_id]["progress"] = progress
        if task_comment:
            self._data[task_id]["task_comment"] = task_comment
        if task_function_args:
            self._data[task_id]["task_function_args"] = task_function_args
        if priority:
            self._data[task_id]["priority"] = priority
        if metadata:
            self._data[task_id]["metadata"] = metadata
        if labels:
            self._data[task_id]["labels"] = labels

        # move updated tasks to the end of the ordereddict, so they're least likely to be discarded
        self._data.move_to_end(task_id)

        await self._save_task_revision(
            TaskRevision(
                task_id=task_id,
                status=status,
                userid=userid,
                agent_id=agent_id,
                details=details,
                progress=progress,
            )
        )

    async def _save_task(
        self,
        userid: str,
        status: str,
        task_type: str,
        task_args: Optional[Dict] = None,
        task_function: Optional[str] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_submission_time: Optional[int] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> str:
        self.validate_labels(labels)

        # see DictTaskBackend for a detailed explanation
        if len(self._data) >= self._task_history_max:
            tasks_to_delete = []
            for _, task in self._data.items():
                if len(tasks_to_delete) >= self._task_deletions_per_pass:
                    break
                if task["status"] in self._task_status_complete:
                    tasks_to_delete.append(task["task_id"])
            for taskid_to_delete in tasks_to_delete:
                del self._data[taskid_to_delete]
                # also take our history with us
                if taskid_to_delete in self._task_history:
                    del self._task_history[taskid_to_delete]

        task_id = task_id or str(uuid.uuid4())
        self._data[task_id] = {
            "status": status,
            "task_id": task_id,
            "userid": userid,
            "task_type": task_type,
            "task_args": task_args or {},
            "task_function": task_function or "",
            "task_function_args": task_function_args or {},
            "task_requirements": task_requirements or {},
            "task_comment": task_comment or "",
            "task_submission_time": task_submission_time or time.time(),
            "metrics": "",
            "priority": priority or 65535,
            "progress": {
                "current_step_index": 0,
                "total_step_count": 0,
                "progress": 0.0,
                "status_message": "",
                "time_remaining": 0.0
            },
            "metadata": metadata or {},
            "labels": labels or []
        }
        return task_id

    async def _save_task_revision(self, task_revision: TaskRevision) -> None:
        """See base class."""

        if task_revision.task_id not in self._task_history:
            self._task_history[task_revision.task_id] = deque(maxlen=self._revisions_history_max)
        self._revision_index += 1
        # patch the revision_id
        patched_revision: TaskRevision = TaskRevision(
            task_id=task_revision.task_id,
            status=task_revision.status,
            userid=task_revision.user_id,
            revision_id=self._revision_index,
            agent_id=task_revision.agent_id,
            details=task_revision.details,
            progress=task_revision.progress,
            time=task_revision.time,
        )
        self._task_history[task_revision.task_id].append(patched_revision)

    async def get_highest_task_revision(self) -> Optional[int]:
        """See base class."""
        return self._revision_index

    async def get_changed_tasks_between_revisions(self, after: int, ending_with: int) -> List[str]:
        """See base class."""
        # this is going to be expensive since we're walking all the revisions across all tasks
        matching_tasks = [
            revision.task_id
            for revisions in self._task_history.values()
            for revision in revisions
            if revision.revision_id and revision.revision_id > after and revision.revision_id <= ending_with
        ]

        return list(set(matching_tasks))

    async def update_tasks_status_bulk(
        self,
        task_ids: List[str],
        new_status: str,
    ) -> List[str]:
        """Update the status of multiple tasks in bulk.

        Args:
            task_ids: List of task IDs to update
            new_status: The new status to set

        Returns:
            List of task IDs that were successfully updated
        """
        updated_ids = []

        for task_id in task_ids:
            if task_id not in self._data:
                continue

            task = self._data[task_id]
            task["status"] = new_status
            updated_ids.append(task_id)
            await self._save_task_revision(
                TaskRevision(
                    task_id=task_id,
                    status=new_status,
                    userid="system",
                    details="Status updated as part of bulk update",
                )
            )

        return updated_ids
