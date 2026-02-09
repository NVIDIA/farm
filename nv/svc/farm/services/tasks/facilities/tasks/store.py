# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Persistence interface for Tasks."""

import asyncio
import enum
from typing import Any, Dict, List, Optional, Tuple, Union, TypedDict, Literal

from nv.svc.core.facilities import base

from ..task_events.base import BaseTaskEventHandler
from nv.svc.farm.services.tasks.utils import status_utils
from .backends import BaseTaskBackend
from .task_revision import TaskRevision


class BulkUpdateSuccess(TypedDict):
    """Success response for bulk actions."""

    task_id: str
    status: Literal["success"]


class BulkUpdateError(TypedDict):
    """Error response for bulk actions."""

    task_id: str
    status: Literal["error"]
    error: str


class TaskStore(base.Facility):
    """Persistence interface for Tasks."""

    def __init__(self, backend: BaseTaskBackend, event_handlers: Optional[List[BaseTaskEventHandler]] = None):
        """Initialize the task store.

        Args:
            backend: Backend for storing task data
            event_handlers: Optional list of event handlers for task events
        """
        self._backend = backend
        self._event_handlers = event_handlers or []

    async def start(self) -> None:
        """Start the task store and all event handlers."""
        await self._backend.start()
        await asyncio.gather(*[handler.start() for handler in self._event_handlers])

    async def stop(self) -> None:
        """Stop the task store and all event handlers."""
        await self._backend.stop()
        await asyncio.gather(*[handler.stop() for handler in self._event_handlers])

    def register_event_handler(self, handler: BaseTaskEventHandler) -> None:
        """Register an event handler for task status updates.

        Args:
            handler: Event handler instance to register
        """
        self._event_handlers.append(handler)

    def _defer_status_update(
        self,
        task_id: str,
        status: status_utils.Status,
        task_type: str = None,
        task_function: str = None,
        userid: str = None,
        details: str = None,
        timeout: int = 30
    ) -> None:
        """
        Defer the status update for a task that is being cancelled.

        Args:
            task_id (str): ID of the updated task
            status (Status): New status of the task
            task_type (str, optional): Type of the updated task
            task_function (str, optional): Function of the updated task
            userid (str, optional): Unique identifier of the User who submitted the task.
            details (str, optional): Details about the task to update.
            timeout (int, optional): Timeout after which to force the state to cancelled. Defaults to 30.
        """
        loop = asyncio.get_running_loop()
        loop.call_later(
            timeout,
            asyncio.create_task,
            self.update_status(
                task_id=task_id,
                task_type=task_type,
                task_function=task_function,
                status=status,
                userid=userid,
                details=details
            )
        )

    async def _push_update_status_event(
        self,
        status: status_utils.Status,
        old_task_state: Dict,
    ) -> None:
        """Push a task status update event to registered handlers.

        Args:
            old_task_state: Previous task state
            status: New status of the task
        """
        task_id = old_task_state.get("task_id")
        task_type = old_task_state.get("task_type")
        task_function = old_task_state.get("task_function")

        if status == status_utils.Status.cancelling:
            self._defer_status_update(
                task_id,
                status=status_utils.Status.cancelled,
                task_type=task_type,
                task_function=task_function,
                userid="Queue",
                details="Forced cancellation by queue"
            )

        if not self._event_handlers:
            return

        event_type = f"status_{status.value}"

        # Only get the task and push the event if at least one event is triggered.
        event_handler_exists = any(handler.event_handler_exists(event_type, old_task_state) for handler in self._event_handlers)

        if not event_handler_exists:
            return

        new_task_state = await self.get_task(
            task_id=task_id,
            task_type=task_type,
            task_function=task_function,
        )

        for handler in self._event_handlers:
            handler.push_event(event_type, old_task_state=old_task_state, new_task_state=new_task_state)

    async def get_next_task(
        self,
        task_keys: List[Tuple],
        capacity: Union[Dict, None],
        agent_id: str,
        labels: Optional[List] = None
    ) -> Tuple:
        """
        Return the next task to process, sorted by their priority.

        Args:
            task_keys (List): Mapping of ``(task_type, task_function)`` to use as search criteria.
            capacity (Union[Dict, None]): Capacity to use as search criteria.
            agent_id (str): Unique identifier of the agent who submitted the task.
            labels (Optional[List]): Label criteria by which to select a task.

        Returns:
            Tuple: A tuple with metadata information about the next task to process.

        """
        labels = labels or []
        priority = 0
        selected_task = None
        selected_task_type = None
        selected_task_function = None
        selected_task_userid = None

        self._backend.validate_labels(labels)

        # Lock the operations in this scope to ensure that multiple calls to this function do not risk causing
        # concurrent read/write operations. This could result in multiple Agents executing the same task, which would be
        # undesirable.
        #
        # TODO: In order to limit the time spent iterating through tasks in order to select the next one available, an
        # optimization could be made by exposing an API returning the tasks already sorted by priority. This would allow
        # picking the first task, instead of iterating over a potentially long list of candidate tasks in a critical
        # section.
        #
        # In the case of a SQL-like database, this could take the form of a statement similar to:
        #   `SELECT * FROM tasks WHERE ... ORDER BY priority DESC LIMIT 1`.
        async with self._backend.lock_transaction():
            if hasattr(self._backend, "get_next_task_prioritised"):
                task = await self._backend.get_next_task_prioritised(task_keys, agent_id, capacity=capacity, labels=labels)
                if not task:
                    return None, None, None
                return task, task["task_type"], task["task_function"]

            for task_type, task_function in task_keys:
                tasks = await self._backend.get_tasks(task_type, task_function, capacity)
                # TODO: This won't scale particularly well. Ideally we do this as part of the selection of the tasks from the source.
                tasks = await self._filter_for_capacity(tasks, capacity)

                if not tasks:
                    continue

                task = tasks[0]
                if not selected_task or task.get("priority", 0) > priority:
                    if task.get("labels", []) != labels:
                        continue

                    selected_task_type = task_type
                    selected_task = task
                    selected_task_function = task_function
                    selected_task_userid = task.get("userid", None)
                    priority = task.get("priority", 0)

            if selected_task:
                await self.update_status(
                    task_id=selected_task["task_id"],
                    task_type=selected_task_type,
                    task_function=selected_task_function,
                    status=status_utils.Status.starting,
                    userid=selected_task_userid,
                    agent_id=agent_id,
                )

        return selected_task, selected_task_type, selected_task_function

    async def _filter_for_capacity(self, tasks: List, capacity: Dict) -> List:
        selected_tasks = []
        for task in tasks:
            task_requirements = task["task_requirements"]
            # Filter out 'env' key since environment variables are job configuration,
            # not capacity requirements that need to be matched against available resources
            task_requirements_keys = {key for key in task_requirements.keys() if key != "env"}
            if all(key in capacity for key in task_requirements_keys):
                selected_tasks.append(task)

        return selected_tasks

    async def get_task_status(
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
        return await self._backend.get_status(task_id, task_type, task_function)

    async def get_task(
        self,
        task_id: str = None,
        task_type: str = None,
        task_function: str = None,
    ) -> Dict:
        """
        Return the unique task matching the given search criterias.

        Args:
            task_id (str): Unique identifier of the task to return.
            task_type (str): Type of the task to return.
            task_function (str): Function of the task to return.

        Returns:
            Dict: Metadata information about the task to retrieve.

        Raises:
            KeyError: Raised when no result could be found matching the given search criterias.

        """
        return await self._backend.get_task(task_id=task_id, task_type=task_type, task_function=task_function)

    async def get_task_revision_history(self, task_id: str,) -> List[TaskRevision]:
        """
        Return the revision history for the given task.

        Args:
            task_id (str): Unique identifier of the task for which to return the revision history.

        Returns:
            List[TaskRevision]: The list of task revisions for the given task.

        """
        return await self._backend.get_task_revision_history(task_id=task_id,)

    async def get_tasks(
        self,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        statuses: List[str] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Return the list of all rows matching the given search criterias.

        Args:
            task_type (Optional[str]): Type of the tasks to return.
            task_function (Optional[str]): Function of the tasks to return.
            statuses (List[str]): List of task statuses to return.
            fields (Optional[List[str]]): Optional list of fields to include in the result. Default is to include all fields.

        Returns:
            List[Dict]: List of metadata information about the tasks to retrieve.

        """
        if statuses is None:
            statuses = [status_utils.Status.submitted.value]
        else:
            # ensure list of statuses
            str_statuses = []
            for status in statuses:
                if isinstance(status, enum.Enum):
                    str_statuses.append(status.value)
                else:
                    str_statuses.append(status)
            statuses = str_statuses

        return await self._backend.get_tasks(
            task_type,
            task_function,
            statuses=statuses,
            fields=fields
        )

    async def update_status(
        self,
        task_id: str,
        status: status_utils.Status,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        userid: Optional[str] = None,
        details: Optional[str] = None,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        agent_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        metadata: Optional[dict] = None,
        labels: Optional[List] = None
    ) -> None:
        """
        Update the status of the task matching the given search criteria.

        Args:
            task_id (str): Unique identifier of the task to update.
            task_type (str): Type of the task to update.
            task_function (str): Function of the task to update.
            status (Status): Status of the task to update.
            userid (Optional[str]): Unique identifier of the User who submitted the task.
            details (Optional[str]): Details about the task to update.
            metrics (Optional[str]): Metrics of the task to update.
            progress (Optional[Dict]): Progress of the task to update.
            agent_id (Optional[str]): Unique identifier of the agent that updated the task.
            task_comment (Optional[str]): Comment about the task.
            task_function_args (Optional[Dict[str, Any]]): Arguments to supply to the task function.
            priority (Optional[int]): Priority of the task (0 being the highest priority)
            metadata (Optional[Dict]): Any additional information required for this task (ie: list of extensions)
            labels (Optional[List]): Task labels that will steer them towards specific agents

        Returns:
            None
        """
        current_task_state, task_updates = await self._validate_status_update(
            task_id=task_id,
            task_type=task_type,
            task_function=task_function,
            status=status,
            userid=userid,
            details=details,
            metrics=metrics,
            progress=progress,
            agent_id=agent_id,
            task_comment=task_comment,
            task_function_args=task_function_args,
            priority=priority,
            metadata=metadata,
            labels=labels
        )

        next_status = task_updates.get("status")
        task_updates["status"] = next_status.value

        await self._backend.update_task(**task_updates)
        await self._push_update_status_event(status=next_status, old_task_state=current_task_state)

    async def archive_task(
        self,
        task_id: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
    ) -> None:
        """
        Archive the given task.

        Args:
            task_id (str): Unique identifier of the task to archive.
            task_type (Optional[str]): Type of the task to archive.
            task_function (Optional[str]): Function of the task to archive.

        Returns:
            None

        """
        task = await self.get_task(
            task_id=task_id,
            task_type=task_type,
            task_function=task_function,
        )

        return await self.update_status(
            task_id=task.get("task_id"),
            task_type=task.get("task_type"),
            task_function=task.get("task_function"),
            status=status_utils.Status.archived,
            userid=task.get("userid"),
            details=task.get("task_details"),
            metrics=task.get("metrics"),
            progress=task.get("progress"),
            agent_id=task.get("agent_id"),
        )

    async def add_task(
        self,
        userid: str,
        task_type,
        task_args: Optional[Dict] = None,
        task_function: Optional[str] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_comment: Optional[str] = None,
        task_id: Optional[str] = None,
        priority: Optional[int] = 65535,
        metadata: Optional[Dict] = None,
        status: Optional[status_utils.Status] = None,
        labels: Optional[List] = None
    ) -> str:
        """
        Add the given task to the persistence.

        Args:
            userid (str): Unique identifier of the User who submitted the task.
            task_type (str): Type of the task to add.
            task_args (Optional[Dict]): Arguments of the task to add.
            task_function (Optional[str]): Function of the task to add.
            task_function_args (Optional[Dict]): Arguments to the function of the task to add.
            task_requirements (Optional[Dict]): Requirements of the task.
            task_comment (Optional[str]): Comment about the task.
            task_id (Optional[str]): Unique identifier of the task to add.
            priority (Optional[int]): Priority of the task (0 being the highest priority)
            metadata (Optional[Dict]): Any additional information required for this task (ie: list of extensions)
            labels (Optional[List]): Task labels that will steer them towards specific agents

        Returns:
            str: The unique identifier of the task that was added.

        """
        return await self._backend.add_task(
            status=status or status_utils.Status.submitted.value,
            task_type=task_type,
            userid=userid,
            task_args=task_args,
            task_function=task_function,
            task_function_args=task_function_args,
            task_requirements=task_requirements,
            task_id=task_id,
            task_comment=task_comment,
            priority=priority,
            metadata=metadata,
            labels=labels
        )

    async def insert_existing_task(
        self,
        task_id: str,
        status: Union[status_utils.Status, str],
        task_type: str,
        userid: str,
        task_args: Optional[Dict] = None,
        task_function: Optional[str] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_comment: Optional[str] = None,
        task_submission_time: Optional[str] = None,
        priority: Optional[int] = 65535,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> None:
        """
        Add the given existing task to the persistence.

        Args:
            task_id (str): Unique identifier of the task to add.
            status (Union[Status, str]): Status of the task to add.
            task_type (str): Type of the task to add.
            userid (str): Unique identifier of the User who submitted the task.
            task_args (Optional[Dict]): Arguments of the task to add.
            task_function (Optional[str]): Function of the task to add.
            task_function_args (Optional[Dict]): Arguments to the function of the task to add.
            task_requirements (Optional[Dict]): Requirements of the task.
            task_comment (Optional[str]): Comment about the task.
            task_submission_time (Optional[int]): Timestamp since epoch this task was added.
            priority (Optional[int]): Priority of the task (0 being the highest priority)
            metadata (Optional[Dict]): Any additional information required for this task (ie: list of extensions)
            labels (Optional[List]): Task labels that will steer them towards specific agents

        Returns:
            None

        """
        await self._backend.add_task(
            status=status.value if isinstance(status, status_utils.Status) else status,
            task_type=task_type,
            userid=userid,
            task_args=task_args or {},
            task_function=task_function or "",
            task_function_args=task_function_args or {},
            task_requirements=task_requirements or {},
            task_id=task_id,
            task_comment=task_comment or "",
            task_submission_time=task_submission_time or None,
            priority=priority,
            metadata=metadata,
            labels=labels
        )

    async def cancel_task(
        self,
        task_id: str,
        task_type: str,
        task_function: str,
        userid: str,
    ) -> None:
        """
        Cancel the task matching the given criterias.

        Args:
            task_id (str): Unique identifier of the task to cancel.
            task_type (str): Type of the task to cancel.
            task_function (str): Function of the task to cancel.
            userid (str): Unique identifier of the User who cancelled the task.

        Returns:
            None

        """
        await self.update_status(
            task_id=task_id,
            task_type=task_type,
            task_function=task_function,
            status=status_utils.Status.cancelled,
            userid=userid,
            details=f"Task cancelled by {userid}",
        )

    async def get_highest_task_revision(self) -> Optional[int]:
        return await self._backend.get_highest_task_revision()

    async def get_changed_tasks_between_revisions(self, after: int, ending_with: int) -> List[str]:
        return await self._backend.get_changed_tasks_between_revisions(after=after, ending_with=ending_with)

    async def process_bulk_status_update(
        self,
        task_id: str,
        status: status_utils.Status,
        details: str,
        userid: str,
    ) -> Union[BulkUpdateSuccess, BulkUpdateError]:
        """Process a bulk status update for a single task."""
        try:
            await self.update_status(
                task_id=task_id,
                status=status,
                details=details,
                userid=userid,
            )
            return {"task_id": task_id, "status": "success"}
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }

    async def get_tasks_bulk(
        self,
        task_ids: List[str],
        statuses: Optional[List[status_utils.Status]] = None,
    ) -> List[Dict]:
        """Return information about multiple tasks.

        Args:
            task_ids (List[str]): List of task IDs to retrieve
            statuses (Optional[List[Status]]): Optional list of statuses to filter by

        Returns:
            List[Dict]: List of task information dictionaries
        """
        validated_statuses = []
        if statuses:
            validated_statuses = [
                status.value if isinstance(status, enum.Enum) else status
                for status in statuses
            ]

        return await self._backend.get_tasks_bulk(
            task_ids=task_ids,
            statuses=validated_statuses,
        )

    async def update_status_bulk(
        self,
        task_ids: List[str],
        status: status_utils.Status,
    ) -> List[str]:
        """
        Update the status of multiple tasks atomically.

        Args:
            task_ids: List of task IDs to update
            new_status: The new status to set

        Returns:
            List of task IDs that were successfully updated
        """
        validated_status = status_utils.validate_status(status)

        # Validate all tasks in parallel
        validation_results = await asyncio.gather(
            *[self._validate_status_update(task_id=task_id, status=validated_status) for task_id in task_ids],
            return_exceptions=True
        )

        # Separate successful validations from errors
        tasks_to_update = []
        for result in validation_results:
            if not isinstance(result, Exception):
                current_task_state, task_updates = result
                tasks_to_update.append((current_task_state, task_updates))

        # Return early if no tasks are valid for update
        if not tasks_to_update:
            return []

        task_ids_to_update = [task_updates["task_id"] for _, task_updates in tasks_to_update]

        # Update the status of the tasks that were successfully validated
        updated_task_ids = await self._backend.update_tasks_status_bulk(
            task_ids=task_ids_to_update,
            new_status=validated_status.value,
        )

        # Push update events for successfully updated tasks
        await asyncio.gather(*[
            self._push_update_status_event(status=validated_status, old_task_state=current_task_state)
            for current_task_state, _ in tasks_to_update
        ])

        return updated_task_ids

    async def _validate_status_update(
        self,
        task_id: str,
        status: status_utils.Status,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        userid: Optional[str] = None,
        details: Optional[str] = None,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        agent_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        metadata: Optional[dict] = None,
        labels: Optional[List] = None
    ) -> Tuple[Dict, Dict]:
        """Validate and reconcile a status update.

        Args:
            task_id: Unique identifier of the task to update
            status: New status to set
            task_type: Type of the task to update
            task_function: Function of the task to update
            userid: Unique identifier of the User who submitted the task
            details: Details about the task to update
            metrics: Metrics of the task to update
            progress: Progress of the task to update
            agent_id: Unique identifier of the agent that updated the task
            task_comment: Comment about the task
            task_function_args: Arguments to supply to the task function
            priority: Priority of the task (0 being the highest priority)
            metadata: Any additional information required for this task
            labels: Task labels that will steer them towards specific agents

        Returns:
            Tuple[Dict, Dict]: The current task and the task with updated status

        Raises:
            KeyError: If the task cannot be found
            InvalidStatusException: If the status is invalid
            StatusTransitionException: If the status transition is invalid
        """
        current_task = await self.get_task(
            task_id=task_id,
            task_type=task_type,
            task_function=task_function,
        )

        _, next_status = status_utils.validate_next_status(current_task["status"], status)

        # userid is required to call update_task because update_task also updates the revision history.
        # If the userid is not provided, we use "unknown" as the default.
        userid = userid or "unknown"

        # This is here for backward compatibility. This logic used to be part of update_status but was moved here
        # so it could be shared with update_status_bulk. We may want to revisit this in the future and possibly remove.
        if status_utils.is_final_state(next_status):
            task_function_args = None
            priority = None

        task_updates = {
            "task_id": task_id,
            "status": next_status,
            "task_type": task_type,
            "task_function": task_function,
            "userid": userid,
            "details": details,
            "metrics": metrics,
            "progress": progress,
            "agent_id": agent_id,
            "task_comment": task_comment,
            "task_function_args": task_function_args,
            "priority": priority,
            "metadata": metadata,
            "labels": labels,
        }

        return current_task, task_updates
