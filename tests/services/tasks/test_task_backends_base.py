# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for task backend implementations.

This module contains test cases for the various task backend implementations,
including the dictionary-based and task ID-based backends.
"""

import asyncio
import random

from unittest import IsolatedAsyncioTestCase

from nv.svc.farm.services.tasks.facilities.tasks import backends


class TestDictBasedBackend(IsolatedAsyncioTestCase):
    """Test cases for dictionary-based task backend implementations."""

    async def asyncSetUp(self, backend_cls: backends.BaseTaskBackend = None) -> None:
        if backend_cls is None:
            backend_cls = backends.DictTaskBackend()
        self._backend = backend_cls
        await self._backend.start()

    async def create_mock_data(
        self,
        status: str,
        amount=1,
        base_task_id=None,
        task_type="foo",
        task_function="bar",
        userid="",
        task_comment="",
        task_submission_time=123456789,
        labels=None
    ):
        for x in range(amount):
            task_id = f"{base_task_id}_{x}" if base_task_id else None
            await self._backend.add_task(
                userid=userid,
                status=status,
                task_type=task_type,
                task_args={"arg1": 1, "arg2": 2, "arg3": 3},
                task_function=task_function,
                task_function_args={"function_arg1": 1, "function_arg2": 2, "function_arg3": 3},
                task_requirements={},
                task_id=task_id,
                task_comment=task_comment,
                task_submission_time=task_submission_time,
                labels=labels
            )

    async def test_get_task_with_task_type(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["status"], "running")

    async def test_get_task_with_task_id_only(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0")

        self.assertEqual(task["status"], "running")

    async def test_get_task_with_task_id_no_task_function(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="")

        self.assertEqual(task["status"], "running")

    async def test_raises_get_task_wrong_task_type(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")

        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="task_0", task_type="bar", task_function="bar")

    async def test_raises_get_task_wrong_task_function(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")

        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="task_0", task_type="foo", task_function="foo")

    async def test_get_tasks_single_task_type(self):
        await self.create_mock_data("running", amount=3, task_type="foo", task_function="bar")
        await self.create_mock_data("submitted", amount=3, task_type="foo", task_function="bar")

        tasks = await self._backend.get_tasks("foo", "bar", statuses=["running"])

        self.assertEqual(3, len(tasks))

    async def test_get_tasks_different_task_type(self):
        await self.create_mock_data("running", amount=2, task_type="foo", task_function="bar")
        await self.create_mock_data("running", amount=3, task_type="bar", task_function="foo")

        tasks = await self._backend.get_tasks("foo", "bar", statuses=["running"])

        self.assertEqual(2, len(tasks))

    async def test_get_task_no_function(self):
        await self.create_mock_data("running", amount=2, task_type="foo", task_function="")
        await self.create_mock_data("running", amount=3, task_type="foo", task_function="bar")

        tasks = await self._backend.get_tasks("foo", "", statuses=["running"])

        self.assertEqual(2, len(tasks))

    async def test_creating_a_task_also_creates_a_revision_history(self):
        await self.create_mock_data("submitted", amount=1, base_task_id="task", task_type="foo", task_function="bar", userid="user_id")

        task_revision_history = await self._backend.get_task_revision_history(task_id="task_0")

        self.assertEqual(1, len(task_revision_history))
        # Revision #1 (initial task submission):
        self.assertEqual("task_0", task_revision_history[0].task_id)
        self.assertEqual("submitted", task_revision_history[0].status)
        self.assertEqual("user_id", task_revision_history[0].user_id)

    async def test_updating_a_task_adds_a_revision_history(self):
        await self.create_mock_data("submitted", amount=1, base_task_id="task", task_type="foo", task_function="bar")

        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="userid", details="lorem", metrics="ipsum")
        task_revision_history = await self._backend.get_task_revision_history(task_id="task_0")

        self.assertEqual(2, len(task_revision_history))
        # Revision #1 (initial task submission):
        self.assertEqual("task_0", task_revision_history[0].task_id)
        self.assertEqual("submitted", task_revision_history[0].status)
        # Revision #2 (task transitionned to "running"):
        self.assertEqual("task_0", task_revision_history[1].task_id)
        self.assertEqual("running", task_revision_history[1].status)
        self.assertEqual("lorem", task_revision_history[1].details)

    async def test_task_revision_histories_are_stored_chronologically(self):
        await self.create_mock_data("submitted", amount=1, base_task_id="task", task_type="foo", task_function="bar", userid="user_id")

        await asyncio.sleep(0.1)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", details="lorem_0", metrics="ipsum_0")
        await asyncio.sleep(0.1)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="finished", userid="user_id", details="lorem_1", metrics="ipsum_1")
        task_revision_history = await self._backend.get_task_revision_history(task_id="task_0")

        self.assertEqual(3, len(task_revision_history))
        # Revision #1 (initial task submission):
        self.assertEqual("task_0", task_revision_history[0].task_id)
        self.assertEqual("submitted", task_revision_history[0].status)
        self.assertEqual("user_id", task_revision_history[0].user_id)
        # Revision #2 (task transitionned to "running"):
        self.assertEqual("task_0", task_revision_history[1].task_id)
        self.assertEqual("running", task_revision_history[1].status)
        self.assertEqual("user_id", task_revision_history[1].user_id)
        self.assertEqual("lorem_0", task_revision_history[1].details)
        # Revision #3 (task transitionned to "finished"):
        self.assertEqual("task_0", task_revision_history[2].task_id)
        self.assertEqual("finished", task_revision_history[2].status)
        self.assertEqual("user_id", task_revision_history[2].user_id)
        self.assertEqual("lorem_1", task_revision_history[2].details)
        # Validate chronological order of events:
        self.assertGreater(task_revision_history[1].time, task_revision_history[0].time)
        self.assertGreater(task_revision_history[2].time, task_revision_history[1].time)

    async def test_task_revision_is_changing(self):
        await self.create_mock_data("submitted", amount=1, base_task_id="task", task_type="foo", task_function="bar", userid="user_id")

        await asyncio.sleep(0.001)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", details="lorem_0", metrics="ipsum_0")
        await asyncio.sleep(0.001)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="finished", userid="user_id", details="lorem_1", metrics="ipsum_1")

        self.assertGreater(await self._backend.get_highest_task_revision(), 0)

    async def test_task_revisions_have_different_ids(self):
        await self.create_mock_data("submitted", amount=1, base_task_id="task", task_type="foo", task_function="bar", userid="user_id")

        await asyncio.sleep(0.001)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", details="lorem_0", metrics="ipsum_0")
        await asyncio.sleep(0.001)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="finished", userid="user_id", details="lorem_1", metrics="ipsum_1")
        task_revision_history = await self._backend.get_task_revision_history(task_id="task_0")

        self.assertNotEqual(task_revision_history[0].revision_id, task_revision_history[1].revision_id)

    async def test_tasks_returned_using_revisions_is_not_zero(self):
        task_count = 4
        await self.create_mock_data("submitted", amount=task_count, base_task_id="task", task_type="foo", task_function="bar", userid="user_id")

        await asyncio.sleep(0.001)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", details="lorem_0", metrics="ipsum_0")
        await asyncio.sleep(0.001)  # Ensure updates have different timestamps
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="finished", userid="user_id", details="lorem_1", metrics="ipsum_1")

        task_ids = await self._backend.get_changed_tasks_between_revisions(0, await self._backend.get_highest_task_revision() or 0)
        self.assertEqual(len(task_ids), task_count)

    async def test_get_status(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")
        status = await self._backend.get_status("task_0", "foo", "bar")

        self.assertEqual(status, "running")

    async def test_raises_get_status_wrong_task_function(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")

        with self.assertRaises(KeyError):
            await self._backend.get_status("task_0", "foo", "foo")

    async def test_update_task(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")
        status = await self._backend.get_status("task_0", "foo", "bar")
        self.assertEqual(status, "running")

        await self._backend.update_task("task_0", task_type="foo", task_function="bar", status="errored", userid="user_id", details="Issue with task")
        status = await self._backend.get_status("task_0", "foo", "bar")
        self.assertEqual(status, "errored")

    async def test_a_task_has_progress_information_by_default(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertIsNotNone(task["progress"])
        self.assertIsInstance(task["progress"], dict)

    async def test_updating_the_progress_of_a_task_persists_it(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        new_progress = {
            "current_step_index": 1,
            "total_step_count": 2,
            "progress": 0.5,
            "status_message": "Processing task 1 of 2",
        }
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", progress=new_progress)
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["progress"], new_progress)

    async def test_updating_a_errored_task_to_submitted_works(self):
        await self.create_mock_data("errored", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "errored")

        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="submitted", userid="user_id")

        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "submitted")

    async def test_updating_a_finished_task_to_submitted_works(self):
        await self.create_mock_data("finished", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "finished")

        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="submitted", userid="user_id")

        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "submitted")

    async def test_updating_a_finished_task_to_running_race_condition(self):
        await self.create_mock_data("finished", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "finished")
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id")

        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "finished")

    async def test_updating_a_finished_task_to_starting_race_condition(self):
        await self.create_mock_data("finished", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "finished")
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="starting", userid="user_id")

        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "finished")

    async def test_updating_a_errored_task_to_running_race_condition(self):
        await self.create_mock_data("errored", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "errored")

        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id")

        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "errored")

    async def test_updating_a_errored_task_to_starting_race_condition(self):
        await self.create_mock_data("errored", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "errored")

        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="starting", userid="user_id")

        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["status"], "errored")

    async def test_updating_a_task_with_no_progress_does_not_clear_its_progress(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        first_progress = {
            "current_step_index": 1,
            "total_step_count": 2,
            "progress": 0.5,
            "status_message": "Processing task 1 of 2",
        }
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", progress=first_progress)

        second_progress = None
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", progress=second_progress)
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["progress"], first_progress)

    async def test_updating_a_task_stores_its_revision_history_with_it(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        new_progress = {
            "current_step_index": 1,
            "total_step_count": 2,
            "progress": 0.5,
            "status_message": "Processing task 1 of 2",
        }
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", progress=new_progress)
        task_revision_history = await self._backend.get_task_revision_history(task_id="task_0")

        self.assertEqual(2, len(task_revision_history))
        self.assertEqual(task_revision_history[0].progress, None)
        self.assertEqual(task_revision_history[1].progress, new_progress)

    async def test_adding_empty_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["labels"], [])

    async def test_adding_configured_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["labels"], ["foo", "bar"])

    async def test_updating_task_no_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id")
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["labels"], ["foo", "bar"])

    async def test_updating_task_with_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", labels=["taz"])
        task = await self._backend.get_task(task_id="task_0", task_type="foo", task_function="bar")
        self.assertEqual(task["labels"], ["taz"])

    async def test_updating_task_with_invalid_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        with self.assertRaises(backends.InvalidLabelError):
            await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id", labels=["invalid,"])

    async def test_creating_task_with_invalid_labels(self):
        with self.assertRaises(backends.InvalidLabelError):
            await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar", "invalid,"])

    async def test_creating_task_with_invalid_label(self):
        with self.assertRaises(backends.InvalidLabelError):
            await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=[","])

    async def test_ensure_creating_many_tasks_discards_oldest_task(self):
        batch_size = 5_000
        discardable_statuses = ['finished', 'errored']
        batches = ['batch1']
        for batch in batches:
            await self.create_mock_data(random.choice(discardable_statuses), amount=batch_size, base_task_id=batch, task_type="foo", task_function="bar", userid="user_id")
        await self.create_mock_data("submitted", amount=100, base_task_id="protected", task_type="foo", task_function="bar", userid="user_id")
        batches = ['batch2', 'batch3', 'batch4']
        for batch in batches:
            await self.create_mock_data(random.choice(discardable_statuses), amount=batch_size, base_task_id=batch, task_type="foo", task_function="bar", userid="user_id")

        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="doesnt exist", task_type="foo", task_function="bar")
        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="batch1_0", task_type="foo", task_function="bar")
        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="batch2_0", task_type="foo", task_function="bar")

        good_tasks = ['protected_50', 'batch3_160', 'batch4_140']
        for good_task in good_tasks:
            self.assertEqual((await self._backend.get_task(task_id=good_task, task_type="foo", task_function="bar"))["task_id"], good_task)

    async def test_slow_dont_deadlock_when_we_cant_remove_tasks(self):
        '''
        fill the task store with tasks that we won't delete, then keep stuffing more of those in ...
        this adds a lot of time to the unittests (~40 seconds) and is testing the that we won't spin indefinitely trying to discard tasks.
        '''
        await self.create_mock_data('submitted', amount=15_000, base_task_id="protected", task_type="foo", task_function="bar", userid="user_id")

    async def test_update_tasks_status_bulk_basic(self):
        """Test basic bulk status update functionality."""
        # Create test tasks
        task_ids = []
        for i in range(3):
            task_id = await self._backend.add_task(
                status="submitted",
                task_type="foo",
                task_function="bar",
                userid="test_user",
                task_args={"arg": i}
            )
            task_ids.append(task_id)

        # Update tasks in bulk
        updated_ids = await self._backend.update_tasks_status_bulk(
            task_ids=task_ids,
            new_status="running"
        )

        # Verify updates
        self.assertEqual(len(updated_ids), 3)
        for task_id in updated_ids:
            task = await self._backend.get_task(task_id)
            self.assertEqual(task["status"], "running")

    async def test_update_tasks_status_bulk_nonexistent_tasks(self):
        """Test bulk update with nonexistent tasks."""
        # Create one real task
        task_id = await self._backend.add_task(
            status="submitted",
            task_type="foo",
            task_function="bar",
            userid="test_user",
            task_args={"arg": 1}
        )

        # Try to update with mix of real and nonexistent tasks
        updated_ids = await self._backend.update_tasks_status_bulk(
            task_ids=[task_id, "nonexistent_1", "nonexistent_2"],
            new_status="running"
        )

        # Should only update the existing task
        self.assertEqual(len(updated_ids), 1)
        self.assertEqual(updated_ids[0], task_id)
        task = await self._backend.get_task(task_id)
        self.assertEqual(task["status"], "running")


class TestIDTaskBasedBackend(IsolatedAsyncioTestCase):
    """Test cases for the ID-based task backend implementation."""

    async def asyncSetUp(self):
        self._backend = backends.TaskIdDictBackend()
        await self._backend.start()

    async def test_ensure_creating_many_tasks_discards_oldest_task(self):
        batch_size = 5_000
        discardable_statuses = ['finished', 'errored']
        batches = ['batch1']
        for batch in batches:
            await self.create_mock_data(random.choice(discardable_statuses), amount=batch_size, base_task_id=batch, task_type="foo", task_function="bar", userid="user_id")
        await self.create_mock_data("submitted", amount=100, base_task_id="protected", task_type="foo", task_function="bar", userid="user_id")
        batches = ['batch2', 'batch3', 'batch4']
        for batch in batches:
            await self.create_mock_data(random.choice(discardable_statuses), amount=batch_size, base_task_id=batch, task_type="foo", task_function="bar", userid="user_id")

        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="doesnt exist", task_type="foo", task_function="bar")
        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="batch1_0", task_type="foo", task_function="bar")
        with self.assertRaises(KeyError):
            await self._backend.get_task(task_id="batch2_0", task_type="foo", task_function="bar")

        good_tasks = ['protected_50', 'batch3_160', 'batch4_140']
        for good_task in good_tasks:
            self.assertEqual((await self._backend.get_task(task_id=good_task, task_type="foo", task_function="bar"))["task_id"], good_task)

    async def test_slow_dont_deadlock_when_we_cant_remove_tasks(self):
        await self.create_mock_data('submitted', amount=15_000, base_task_id="protected", task_type="foo", task_function="bar", userid="user_id")

    async def create_mock_data(
        self,
        status: str,
        amount=1,
        base_task_id=None,
        task_type="foo",
        task_function="bar",
        userid="",
        task_comment="",
        task_submission_time=123456789,
        labels=None
    ):
        for x in range(amount):
            task_id = f"{base_task_id}_{x}" if base_task_id else None
            await self._backend.add_task(
                userid=userid,
                status=status,
                task_type=task_type,
                task_args={"arg1": 1, "arg2": 2, "arg3": 3},
                task_function=task_function,
                task_function_args={"function_arg1": 1, "function_arg2": 2, "function_arg3": 3},
                task_requirements={},
                task_id=task_id,
                task_comment=task_comment,
                task_submission_time=task_submission_time,
                labels=labels
            )
