# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Status utilities for the farm service tasks."""

import enum
from typing import Union, Tuple, List, Dict


class Status(str, enum.Enum):
    """Standard task statuses."""

    unscheduled = "unscheduled"  # Task definition is complete but not yet ready to be submitted and picked up by a controller(agent).

    unschedulable = "unschedulable"  # Task is unable to be scheduled.

    submitted = "submitted"  # Task is submitted to the queue and ready to be picked up by a controller(agent).

    waiting = "waiting"  # Task is queued for execution by NVCT.

    starting = "starting"  # Task is removed from queue and is waiting to be started by the process manager.

    running = "running"  # Task process manager is running the task

    finished = "finished"  # Task process manager exits with exit code 0

    errored = "errored"  # Task process manager exits with non-zero exit code

    paused = "paused"  # Task is paused (not implemented)

    cancelled = "cancelled"  # Task is cancelled

    archived = "archived"  # Task is no longer active

    cancelling = "cancelling"  # Task is being cancelled

    pausing = "pausing"  # Task is being paused (not implemented)

    pending = "pending"  # Task status is changed to pending only for local controller(agent) store to indicate task is no longer in the queue.

    evicted = "evicted"  # Task has been evicted

    def __str__(self):
        """Fix inconsistent string generation between python 3.10 and 3.12."""
        return f'{self.name}'


# This is the start of identifying stages of identifying points of interest in the task lifecycle.
# The point is to identify places where tasks can exit and reenter the task lifecycle.
TASK_STAGES = {
    # Tasks are ready to be submitted to the queue.
    "ready" : {
        Status.submitted,
        Status.unscheduled,
    },
    # Tasks are being processed by the agent.
    "processing" : {
        Status.starting,
        Status.running
    },
    # The task system is attempting to stop the task.
    "stopping" : {
        Status.cancelling,
        Status.pausing,
    },
    # The task agent has stopped the task.
    "stopped" : {
        Status.cancelled,
        Status.paused,
    },
    # The task agent has completed the task.
    "resolved" : {
        Status.finished,
        Status.errored
    },
    # Task is finished being processed by the task system. This is different from resolved. Tasks that are resolved have completed being processed by the agent,
    # and tasks that are processed have completed being processed by the task system i.e. unschedulable.
    "processed": {
        Status.unschedulable,
        Status.finished,
        Status.errored
    }
}


NEXT_STATUS_DICT = {
    Status.unscheduled: {Status.submitted, Status.unschedulable} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"],
    Status.submitted: {Status.pending, Status.starting, Status.running} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"],
    Status.unschedulable: {Status.submitted, Status.unscheduled} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"],
    Status.waiting: {Status.submitted, Status.starting, Status.running} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"] | TASK_STAGES["resolved"],
    Status.pending: {Status.submitted, Status.starting, Status.running} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"] | TASK_STAGES["resolved"],
    Status.starting: {Status.running} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"] | TASK_STAGES["resolved"],
    Status.running: {Status.starting} | TASK_STAGES["stopping"] | TASK_STAGES["stopped"] | TASK_STAGES["resolved"],
    Status.pausing: {Status.paused} | TASK_STAGES["resolved"],
    Status.cancelling: {Status.cancelled} | TASK_STAGES["resolved"],
    Status.cancelled: {Status.archived} | TASK_STAGES["resolved"] | TASK_STAGES["ready"],
    Status.paused: {Status.starting, Status.cancelling, Status.cancelled} | TASK_STAGES["resolved"],
    Status.finished: {Status.archived} | TASK_STAGES["ready"],
    Status.errored: {Status.archived} | TASK_STAGES["ready"],
    Status.archived: set(),
}

PREV_STATUS_DICT = {
    status: {current_status for current_status, next_statuses in NEXT_STATUS_DICT.items() if status in next_statuses}
    for status in Status
}


class StatusTransitionException(Exception):
    """Exception raised for invalid status transitions."""

    def __init__(self, current_status: Status, next_status: Status):
        self.current_status = current_status
        self.next_status = next_status
        super().__init__(f"Invalid status transition, {current_status} -> {next_status}")


class InvalidStatusException(Exception):
    """Exception raised for invalid status values."""

    def __init__(self, status: str):
        self.status = status
        super().__init__(f"Invalid status: {status}")


def validate_status(status: Union[str, Status]) -> Status:
    """Validate a status and return the corresponding Status enum if valid.

    Args:
        status (Union[str, Status]): The status to validate.

    Returns:
        Status: The validated Status enum.

    Raises:
        InvalidStatusException: If the status is invalid.
    """
    if isinstance(status, Status):
        return status
    try:
        return Status(status)
    except ValueError:
        raise InvalidStatusException(status)


def get_next_status_list(status: Union[str, Status]) -> List[Status]:
    """Get the list of next statuses for a given status."""
    return list(NEXT_STATUS_DICT[validate_status(status)])


def get_prev_status_list(status: Union[str, Status]) -> List[Status]:
    """Get the list of previous statuses for a given status."""
    return list(PREV_STATUS_DICT[validate_status(status)])


def validate_next_status(current_status: Union[str, Status], next_status: Union[str, Status]) -> Tuple[Status, Status]:
    """Validate a status transition and return the validated Status enums if valid.

    Args:
        current_status (Union[str, Status]): The current status.
        next_status (Union[str, Status]): The next status.

    Returns:
        Tuple[Status, Status]: The validated current and next Status enums.

    Raises:
        StatusTransitionException: If the transition is invalid.
    """
    current_status = validate_status(current_status)
    next_status = validate_status(next_status)

    # We allow staying in the same status without raising an exception
    if next_status != current_status and next_status not in NEXT_STATUS_DICT[current_status]:
        raise StatusTransitionException(current_status, next_status)

    return current_status, next_status


def is_final_state(status: Union[str, Status]) -> bool:
    """Check if a status transition is valid for a task in a transitional state.

    Args:
        status (Union[str, Status]): status to check if it is a final state

    Returns:
        bool: True if the transition is valid, False otherwise
    """
    status = validate_status(status)
    return status in TASK_STAGES["resolved"] | {Status.cancelled}


def is_invalid_resume_transition(current_status: Union[str, Status], next_status: Union[str, Status]) -> bool:
    """Check if a status transition is from pausing, cancelling, or cancelled to running.

    Args:
        current_status (Union[str, Status]): The current status.
        next_status (Union[str, Status]): The next status.

    Returns:
        bool: True if the transition is from pausing, cancelling, or cancelled to running, False otherwise.
    """
    current_status = validate_status(current_status)
    next_status = validate_status(next_status)
    return current_status in {Status.pausing, Status.cancelling, Status.cancelled} and next_status == Status.running


def get_processed_status_list() -> List[Status]:
    """Get the list of processed statuses."""
    return list(TASK_STAGES["processed"])


def is_processed(status: Union[str, Status]) -> bool:
    """Check if a status is processed.

    Args:
        status (Union[str, Status]): The status to check.

    Returns:
        bool: True if the status is processed, False otherwise.
    """
    status = validate_status(status)
    return status in TASK_STAGES["processed"]


def is_task_processed(task: Dict) -> bool:
    """Check if a task is processed.

    Args:
        task (Dict): The task to check.

    Returns:
        bool: True if the task is processed, False otherwise.
    """
    return is_processed(task["status"])


def are_tasks_processed(tasks: List[Dict]) -> bool:
    """Check if all tasks are processed.

    Args:
        tasks (List[Dict]): The tasks to check.

    Returns:
        bool: True if all tasks are processed, False otherwise.
    """
    return all(is_task_processed(task) for task in tasks)


def is_finished(status: Union[str, Status]) -> bool:
    """Check if a status is finished.

    Args:
        status (Union[str, Status]): The status to check.

    Returns:
        bool: True if the status is finished, False otherwise.
    """
    status = validate_status(status)
    return status == Status.finished


def is_task_finished(task: Dict) -> bool:
    """Check if a task is finished.

    Args:
        task (Dict): The task to check.

    Returns:
        bool: True if the task is finished, False otherwise.
    """
    return is_finished(task["status"])


def are_tasks_finished(tasks: List[Dict]) -> bool:
    """Check if all tasks are finished.

    Args:
        tasks (List[Dict]): The tasks to check.

    Returns:
        bool: True if all tasks are finished, False otherwise.
    """
    return all(is_task_finished(task) for task in tasks)


def is_errored(status: Union[str, Status]) -> bool:
    """Check if a status is errored.

    Args:
        status (Union[str, Status]): The status to check.

    Returns:
        bool: True if the status is errored, False otherwise.
    """
    status = validate_status(status)
    return status == Status.errored


def is_task_errored(task: Dict) -> bool:
    """Check if a task is errored.

    Args:
        task (Dict): The task to check.

    Returns:
        bool: True if the task is errored, False otherwise.
    """
    status = task.get("status")
    return is_errored(status)


def are_tasks_errored(tasks: List[Dict]) -> bool:
    """Check if any tasks are errored.

    Args:
        tasks (List[Dict]): The tasks to check.

    Returns:
        bool: True if any tasks are errored, False otherwise.
    """
    return any(is_task_errored(task) for task in tasks)
