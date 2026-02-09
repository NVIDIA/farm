# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the status_utils module."""

import pytest

from nv.svc.farm.services.tasks.utils import status_utils


def test_validate_status():
    """Test validate_status function."""
    # Test with Status enum
    assert status_utils.validate_status(status_utils.Status.running) == status_utils.Status.running

    # Test with string
    assert status_utils.validate_status("running") == status_utils.Status.running

    # Test with invalid status
    with pytest.raises(status_utils.InvalidStatusException):
        status_utils.validate_status("invalid_status")


def test_validate_next_status():
    """Test validate_next_status function."""
    # Test valid transitions
    current, next_status = status_utils.validate_next_status(
        status_utils.Status.submitted,
        status_utils.Status.running
    )
    assert current == status_utils.Status.submitted
    assert next_status == status_utils.Status.running

    # Test invalid transition
    with pytest.raises(status_utils.StatusTransitionException):
        status_utils.validate_next_status(
            status_utils.Status.finished,
            status_utils.Status.running
        )


def test_is_final_state():
    """Test is_final_state function."""
    # Test final states
    assert status_utils.is_final_state(status_utils.Status.finished)
    assert status_utils.is_final_state(status_utils.Status.errored)
    assert status_utils.is_final_state(status_utils.Status.cancelled)

    # Test non-final states
    assert not status_utils.is_final_state(status_utils.Status.running)
    assert not status_utils.is_final_state(status_utils.Status.submitted)
    assert not status_utils.is_final_state(status_utils.Status.waiting)


def test_is_invalid_resume_transition():
    """Test is_invalid_resume_transition function."""
    # Test invalid resume transitions
    assert status_utils.is_invalid_resume_transition(
        status_utils.Status.pausing,
        status_utils.Status.running
    )
    assert status_utils.is_invalid_resume_transition(
        status_utils.Status.cancelling,
        status_utils.Status.running
    )
    assert status_utils.is_invalid_resume_transition(
        status_utils.Status.cancelled,
        status_utils.Status.running
    )

    # Test valid transitions
    assert not status_utils.is_invalid_resume_transition(
        status_utils.Status.paused,
        status_utils.Status.running
    )
    assert not status_utils.is_invalid_resume_transition(
        status_utils.Status.submitted,
        status_utils.Status.running
    )


def test_status_transition_exception():
    """Test StatusTransitionException."""
    exception = status_utils.StatusTransitionException(
        status_utils.Status.finished,
        status_utils.Status.running
    )
    assert str(exception) == "Invalid status transition, finished -> running"
    assert exception.current_status == status_utils.Status.finished
    assert exception.next_status == status_utils.Status.running


def test_invalid_status_exception():
    """Test InvalidStatusException."""
    exception = status_utils.InvalidStatusException("invalid_status")
    assert str(exception) == "Invalid status: invalid_status"
    assert exception.status == "invalid_status"


def test_is_processed():
    """Test is_processed function."""
    # Test processed statuses
    assert status_utils.is_processed(status_utils.Status.unschedulable)
    assert status_utils.is_processed(status_utils.Status.finished)
    assert status_utils.is_processed(status_utils.Status.errored)

    # Test non-processed statuses
    assert not status_utils.is_processed(status_utils.Status.submitted)
    assert not status_utils.is_processed(status_utils.Status.running)
    assert not status_utils.is_processed(status_utils.Status.waiting)


def test_is_task_processed():
    """Test is_task_processed function."""
    # Test processed tasks
    assert status_utils.is_task_processed({"status": status_utils.Status.finished})
    assert status_utils.is_task_processed({"status": status_utils.Status.errored})
    assert status_utils.is_task_processed({"status": status_utils.Status.unschedulable})

    # Test non-processed tasks
    assert not status_utils.is_task_processed({"status": status_utils.Status.submitted})
    assert not status_utils.is_task_processed({"status": status_utils.Status.running})
    assert not status_utils.is_task_processed({"status": status_utils.Status.waiting})


def test_are_tasks_processed():
    """Test are_tasks_processed function."""
    # Test all tasks processed
    tasks = [
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.errored},
        {"status": status_utils.Status.unschedulable}
    ]
    assert status_utils.are_tasks_processed(tasks)

    # Test some tasks not processed
    tasks = [
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.submitted},  # Not processed
        {"status": status_utils.Status.errored}
    ]
    assert not status_utils.are_tasks_processed(tasks)

    # Test empty list
    assert status_utils.are_tasks_processed([])


def test_is_finished():
    """Test is_finished function."""
    # Test finished status
    assert status_utils.is_finished(status_utils.Status.finished)

    # Test non-finished statuses
    assert not status_utils.is_finished(status_utils.Status.running)
    assert not status_utils.is_finished(status_utils.Status.errored)
    assert not status_utils.is_finished(status_utils.Status.submitted)


def test_is_task_finished():
    """Test is_task_finished function."""
    # Test finished task
    assert status_utils.is_task_finished({"status": status_utils.Status.finished})

    # Test non-finished tasks
    assert not status_utils.is_task_finished({"status": status_utils.Status.running})
    assert not status_utils.is_task_finished({"status": status_utils.Status.errored})
    assert not status_utils.is_task_finished({"status": status_utils.Status.submitted})


def test_are_tasks_finished():
    """Test are_tasks_finished function."""
    # Test all tasks finished
    tasks = [
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.finished}
    ]
    assert status_utils.are_tasks_finished(tasks)

    # Test some tasks not finished
    tasks = [
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.running},  # Not finished
        {"status": status_utils.Status.finished}
    ]
    assert not status_utils.are_tasks_finished(tasks)

    # Test empty list
    assert status_utils.are_tasks_finished([])


def test_is_errored():
    """Test is_errored function."""
    # Test errored status
    assert status_utils.is_errored(status_utils.Status.errored)

    # Test non-errored statuses
    assert not status_utils.is_errored(status_utils.Status.finished)
    assert not status_utils.is_errored(status_utils.Status.running)
    assert not status_utils.is_errored(status_utils.Status.submitted)


def test_is_task_errored():
    """Test is_task_errored function."""
    # Test errored task
    assert status_utils.is_task_errored({"status": status_utils.Status.errored})

    # Test non-errored tasks
    assert not status_utils.is_task_errored({"status": status_utils.Status.finished})
    assert not status_utils.is_task_errored({"status": status_utils.Status.running})
    assert not status_utils.is_task_errored({"status": status_utils.Status.submitted})

    # Test task with missing status - should raise InvalidStatusException
    with pytest.raises(status_utils.InvalidStatusException):
        status_utils.is_task_errored({})


def test_are_tasks_errored():
    """Test are_tasks_errored function."""
    # Test some tasks errored
    tasks = [
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.errored},  # One errored
        {"status": status_utils.Status.running}
    ]
    assert status_utils.are_tasks_errored(tasks)

    # Test no tasks errored
    tasks = [
        {"status": status_utils.Status.finished},
        {"status": status_utils.Status.running},
        {"status": status_utils.Status.submitted}
    ]
    assert not status_utils.are_tasks_errored(tasks)

    # Test empty list
    assert not status_utils.are_tasks_errored([])


def test_get_processed_status_list():
    """Test get_processed_status_list function."""
    processed_statuses = status_utils.get_processed_status_list()
    expected_statuses = [
        status_utils.Status.unschedulable,
        status_utils.Status.finished,
        status_utils.Status.errored
    ]
    
    assert len(processed_statuses) == len(expected_statuses)
    for status in expected_statuses:
        assert status in processed_statuses
