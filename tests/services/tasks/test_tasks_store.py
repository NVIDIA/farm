# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the task store implementation."""

import asyncio
import random
from typing import Any, Dict, List, Optional
from unittest import IsolatedAsyncioTestCase

from nv.svc.farm.services.tasks.facilities.tasks import backends, store
from nv.svc.farm.services.tasks.utils import status_utils


def patch_defer_status_update(timeout: int = 1):
    """Patch the _defer_status_update method with a custom timeout."""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            original_method = self._store._defer_status_update

            def patched_method(*a, **kw):
                return original_method(*a, timeout=timeout, **kw)
            self._store._defer_status_update = patched_method
            try:
                await func(self, *args, **kwargs)
            finally:
                self._store._defer_status_update = original_method
        return wrapper
    return decorator


class TestTaskStore_DictBackend(IsolatedAsyncioTestCase):
    """Test cases for the task store with dictionary backend."""

    async def asyncSetUp(self, backend: backends.BaseTaskBackend = backends.DictTaskBackend()) -> None:
        self._store = store.TaskStore(backend)
        await self._store.start()

    async def create_mock_data(
        self,
        status: str,
        amount: int = 1,
        base_task_id: str = None,
        task_type: str = "foo",
        task_function: str = "bar",
        task_comment: str = "",
        task_requirements: Optional[Dict] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = 65535,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None
    ):
        for x in range(amount):
            task_id = f"{base_task_id}_{x}" if base_task_id else None
            await self._store.insert_existing_task(
                task_id=task_id,
                status=status,
                task_type=task_type,
                userid="userid",
                task_args={"arg1": 1, "arg2": 2, "arg3": 3},
                task_function=task_function,
                task_function_args=task_function_args or {"function_arg1": 1, "function_arg2": 2, "function_arg3": 3},
                task_requirements=task_requirements or {},
                task_comment=task_comment,
                priority=priority,
                metadata=metadata,
                labels=labels
            )

    async def test_adding_a_task_returns_an_auto_generated_id(self):
        task_id = await self._store.add_task(
            userid="userid",
            task_type="foo",
        )

        self.assertIsNotNone(task_id)
        self.assertIsInstance(task_id, str)

    async def test_adding_task_with_specific_status(self):
        task_id = await self._store.add_task(
            userid="userid",
            task_type="foo",
            status=status_utils.Status.pending
        )

        status = await self._store.get_task_status(task_id)
        self.assertEqual("pending", status)

    async def test_get_task_with_task_type(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["status"], "running")

    async def test_get_task_with_metadata(self):
        await self.create_mock_data(
            "running",
            base_task_id="task",
            task_type="foo",
            task_function="bar",
            metadata={"extensions": ["foo.bar"], "registries": {"name": "url"}}
        )
        task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["metadata"], {"extensions": ["foo.bar"], "registries": {"name": "url"}})

    async def test_get_next_task(self):
        await self.create_mock_data("submitted", amount=5, base_task_id="task", task_type="foo", task_function="bar")
        task, task_type, task_function = await self._store.get_next_task([("foo", "bar")], {}, "agent_a")

        self.assertEqual(task["status"], "starting")
        self.assertEqual(task_type, "foo")
        self.assertEqual(task_function, "bar")

    async def test_get_next_task_with_capacity(self):
        await self.create_mock_data(
            "submitted",
            amount=5,
            base_task_id="task",
            task_type="foo",
            task_function="bar",
            task_requirements={"users.john-doe": 1}
        )
        task, task_type, task_function = await self._store.get_next_task(
            [("foo", "bar")],
            {
                "users.john-doe": {"strict": False, "capacity": 1},
                "nvidia.gpu.rtx.3090": {"strict": False, "capacity": 1},
            },
            "agent_a"
        )

        self.assertEqual(task["status"], "starting")
        self.assertEqual(task_type, "foo")
        self.assertEqual(task_function, "bar")

    async def test_get_next_task_with_no_capacity_available(self):
        await self.create_mock_data(
            "submitted",
            amount=5,
            base_task_id="task",
            task_type="foo",
            task_function="bar",
            task_requirements={"users.john-doe": 1}
        )
        task, task_type, task_function = await self._store.get_next_task(
            [("foo", "bar")],
            {
                "nvidia.gpu.rtx.3090": {"strict": False, "capacity": 1},
            },
            "agent_a"
        )
        self.assertEqual(task, None)
        self.assertEqual(task_type, None)
        self.assertEqual(task_function, None)

    async def test_get_task_for_which_capacity_available(self):
        """Test that if there are multiple waiting tasks across task types that one is selected if for the first type there is no capacity."""
        await self.create_mock_data(
            "submitted",
            amount=5,
            base_task_id="task",
            task_type="foo",
            task_function="bar",
            task_requirements={"users.john-doe": 1}
        )
        await self.create_mock_data(
            "submitted",
            amount=5,
            base_task_id="task",
            task_type="baz",
            task_function="qux",
            task_requirements={}
        )
        task, task_type, task_function = await self._store.get_next_task(
            [("foo", "bar"), ("baz", "qux")],
            {
                "nvidia.gpu.rtx.3090": {"strict": False, "capacity": 1},
            },
            "agent_a"
        )
        self.assertEqual(task["status"], "starting")
        self.assertEqual(task_type, "baz")
        self.assertEqual(task_function, "qux")

    async def test_update_status(self):
        await self.create_mock_data("submitted", amount=5, base_task_id="task", task_type="foo", task_function="bar")

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("submitted", status)

        await self._store.update_status(
            task_id="task_0",
            task_type="foo",
            task_function="bar",
            status=status_utils.Status.running,
            userid="userid"
        )

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("running", status)

    async def test_updating_a_task_preserves_the_user_and_agent_ids(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        # Provide a user id other than the original.
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_a")
        task_revision_1 = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        # Check that the userid has NOT been updated on the task itself.
        self.assertEqual("userid", task_revision_1["userid"])

    async def test_updating_a_task_can_update_its_function_args_if_in_submitted_status(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        # Update the mock task with custom data, before validating if the task's updated function args were successfully
        # set:
        new_task_function_args = {
            "lorem": "ipsum",
            "dolor": {
                "sit": "amet",
            },
        }
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", task_function_args=new_task_function_args, status="submitted")
        updated_task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(updated_task["task_function_args"], new_task_function_args)

    async def test_updating_a_task_cannot_update_its_function_args_if_in_running_status(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")

        # Validate that the `task_function_args` are not overriden if the task is `running`:
        initial_task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")
        new_task_function_args = {
            "lorem": "ipsum",
            "dolor": {
                "sit": "amet",
            },
        }
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", task_function_args=new_task_function_args, status="running")
        updated_task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(updated_task["task_function_args"], initial_task["task_function_args"])

    async def test_updating_a_task_can_update_its_comment_if_in_submitted_status(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        # Update the mock task with custom data, before validating if the task's updated comment was successfully set:
        new_task_comment = "Lorem ipsum"
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", task_comment=new_task_comment, status="submitted")
        updated_task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(updated_task["task_comment"], new_task_comment)

    async def test_updating_a_task_cannot_update_its_comment_if_in_running_status(self):
        await self.create_mock_data("running", base_task_id="task", task_type="foo", task_function="bar")

        # Validate that the `task_comment` is not overriden if the task is `running`:
        initial_task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")
        new_task_comment = "Lorem ipsum"
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", task_comment=new_task_comment, status="running")
        updated_task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(updated_task["task_comment"], initial_task["task_comment"])

    async def test_update_status_with_metrics(self):
        await self.create_mock_data("submitted", amount=5, base_task_id="task", task_type="foo", task_function="bar")

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("submitted", status)

        await self._store.update_status(
            task_id="task_0",
            task_type="foo",
            task_function="bar",
            status=status_utils.Status.running,
            userid="userid",
            metrics="process_virtual_memory_bytes"
        )

        task = await self._store.get_task("task_0", "foo", "bar")
        self.assertEqual("process_virtual_memory_bytes", task["metrics"])

    async def test_update_cancelling_status(self):
        await self.create_mock_data("cancelling", amount=5, base_task_id="task", task_type="foo", task_function="bar")

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("cancelling", status)

        with self.assertRaises(store.status_utils.StatusTransitionException):
            await self._store.update_status(
                task_id="task_0",
                task_type="foo",
                task_function="bar",
                status=status_utils.Status.running,
                userid="userid"
            )

    async def test_update_cancelling_status_to_cancelled(self):
        await self.create_mock_data("cancelling", amount=5, base_task_id="task", task_type="foo", task_function="bar")

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("cancelling", status)

        await self._store.update_status(
            task_id="task_0",
            task_type="foo",
            task_function="bar",
            status=status_utils.Status.cancelled,
            userid="userid"
        )

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("cancelled", status)

    async def test_update_cancelled_status(self):
        await self.create_mock_data("cancelled", amount=5, base_task_id="task", task_type="foo", task_function="bar")

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("cancelled", status)

        with self.assertRaises(store.status_utils.StatusTransitionException):
            # Make sure that if the task has already been cancelled but still flagged as running by the agent to raise
            # Raising a StatusTransitionException will cause the agent to cancel the task.
            await self._store.update_status(
                task_id="task_0",
                task_type="foo",
                task_function="bar",
                status=status_utils.Status.running,
                userid="userid"
            )

    @patch_defer_status_update(timeout=0)
    async def test_update_cancelling_status_to_cancelled_timeout(self):
        await self.create_mock_data("cancelling", amount=5, base_task_id="task", task_type="foo", task_function="bar")

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("cancelling", status)

        await self._store.update_status(
            task_id="task_0",
            task_type="foo",
            task_function="bar",
            status=status_utils.Status.cancelling,
            userid="userid"
        )
        await asyncio.sleep(0.1)

        status = await self._store.get_task_status("task_0", "foo", "bar")
        self.assertEqual("cancelled", status)

    async def test_get_tasks_count(self):
        await self.create_mock_data("submitted", amount=5, base_task_id="task", task_type="foo", task_function="bar")
        tasks = await self._store.get_tasks("foo", "bar")

        self.assertEqual(len(tasks), 5, "Expected to find 5 tasks matching the given criteria")

    async def test_get_tasks(self):
        await self.create_mock_data("submitted", amount=5, base_task_id="task", task_type="foo", task_function="bar")
        task = await self._store.get_task("task_0", "foo", "bar")

        self.assertEqual(task["task_id"], "task_0")

    async def test_a_task_has_progress_information_by_default(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertIsNotNone(task["progress"])
        self.assertIsInstance(task["progress"], dict)

    async def test_returning_all_tasks_also_returns_their_progress(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        tasks = await self._store.get_tasks(task_type="foo", task_function="bar")

        for task in tasks:
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
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", status="running", progress=new_progress)
        task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["progress"], new_progress)

    async def test_updating_a_task_with_no_progress_does_not_clear_its_progress(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        first_progress = {
            "current_step_index": 1,
            "total_step_count": 2,
            "progress": 0.5,
            "status_message": "Processing task 1 of 2",
        }
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", status="running", progress=first_progress)

        second_progress = None
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", status="running", progress=second_progress)
        task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["progress"], first_progress)

    async def test_updating_a_task_with_no_priority_does_not_clear_it(self):
        priority = 50
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", priority=priority)
        await self._store.update_status(task_id="task_0", task_type="foo", task_function="bar", status="running")
        task = await self._store.get_task(task_id="task_0", task_type="foo", task_function="bar")

        self.assertEqual(task["priority"], priority)

    async def test_archiving_a_task_in_a_supported_status_succeeds(self):
        for archiveable_task_status in status_utils.get_prev_status_list(status_utils.Status.archived):
            base_task_id = f"task_{archiveable_task_status}"
            task_id = f"{base_task_id}_0"
            await self.create_mock_data(archiveable_task_status, base_task_id=base_task_id, task_type="foo", task_function="bar")

            await self._store.archive_task(task_id=task_id, task_type="foo", task_function="bar")

            task = await self._store.get_task(task_id=task_id, task_type="foo", task_function="bar")

            self.assertEqual(task["status"], "archived")

    async def test_archiving_a_task_in_unsupported_status_raises_an_exception(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")

        with self.assertRaises(expected_exception=status_utils.StatusTransitionException) as ctx:
            await self._store.archive_task(task_id="task_0", task_type="foo", task_function="bar")

        assert "Invalid status transition" in str(ctx.exception)

    async def test_get_task_with_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        task, task_type, task_function = await self._store.get_next_task([("foo", "bar")], {}, "agent_a", labels=["foo", "bar"])
        self.assertEqual(task["task_id"], "task_0")

    async def test_get_task_with_labels_set_but_not_used_during_selection(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        task, task_type, task_function = await self._store.get_next_task([("foo", "bar")], {}, "agent_a")
        self.assertEqual(task, None)

    async def test_get_task_with_no_labels_set_but_used_during_selection(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        task, task_type, task_function = await self._store.get_next_task([("foo", "bar")], {}, "agent_a", labels=["foo", "bar"])
        self.assertEqual(task, None)

    async def test_update_status_bulk(self):
        """Test bulk status update functionality."""
        # Create test tasks
        task_ids = []
        for i in range(5):
            task_id = await self._store.add_task(
                status="submitted",
                task_type="foo",
                task_function="bar",
                userid="test_user",
                task_args={"arg": i}
            )
            task_ids.append(task_id)

        # Update first two tasks to running
        await self._store.update_status(task_ids[0], task_type="foo", task_function="bar", status=status_utils.Status.running, userid="userid")
        await self._store.update_status(task_ids[1], task_type="foo", task_function="bar", status=status_utils.Status.running, userid="userid")
        await self._store.update_status(task_ids[0], task_type="foo", task_function="bar", status=status_utils.Status.finished, userid="userid")
        await self._store.update_status(task_ids[1], task_type="foo", task_function="bar", status=status_utils.Status.finished, userid="userid")

        # Bulk update with invalid status transition
        updated_ids = await self._store.update_status_bulk(
            task_ids=task_ids,
            status="cancelled",
        )

        # Should only update the non-finished tasks
        self.assertEqual(len(updated_ids), 3)
        for task_id in updated_ids:
            task = await self._store.get_task(task_id)
            self.assertEqual(task["status"], "cancelled")

        # Verify finished tasks weren't updated
        for task_id in task_ids[:2]:
            task = await self._store.get_task(task_id)
            self.assertEqual(task["status"], "finished")

    async def test_update_status_bulk_no_exclusions(self):
        """Test bulk status update without exclusions."""
        # Create test tasks
        task_ids = []
        for i in range(3):
            task_id = await self._store.add_task(
                status="submitted",
                task_type="foo",
                task_function="bar",
                userid="test_user",
                task_args={"arg": i}
            )
            task_ids.append(task_id)

        # Update all tasks
        updated_ids = await self._store.update_status_bulk(
            task_ids=task_ids,
            status="running"
        )

        # Verify all tasks were updated
        self.assertEqual(len(updated_ids), 3)
        for task_id in updated_ids:
            task = await self._store.get_task(task_id)
            self.assertEqual(task["status"], "running")

    async def test_update_status_bulk_nonexistent_tasks(self):
        """Test bulk status update with nonexistent tasks."""
        # Create one real task
        task_id = await self._store.add_task(
            status="submitted",
            task_type="foo",
            task_function="bar",
            userid="test_user",
            task_args={"arg": 1}
        )

        # Try to update with mix of real and nonexistent tasks
        updated_ids = await self._store.update_status_bulk(
            task_ids=[task_id, "non_existent_1", "non_existent_2"],
            status="running"
        )

        # Should only update the existing task
        self.assertEqual(len(updated_ids), 1)
        self.assertEqual(updated_ids[0], task_id)
        task = await self._store.get_task(task_id)
        self.assertEqual(task["status"], "running")


class TestTaskStore_TestIDDictBackend(IsolatedAsyncioTestCase):
    """Test cases for the task store with test ID dictionary backend."""

    async def asyncSetUp(self):
        self._store = store.TaskStore(backends.TaskIdDictBackend())
        await self._store.start()

    async def test_ensure_creating_many_tasks_discards_oldest_task(self):
        batch_size = 5_000
        discardable_statuses = ['finished', 'errored']
        batches = ['batch1']
        for batch in batches:
            status = random.choice(discardable_statuses)
            await self.create_mock_data(
                status,
                amount=batch_size,
                base_task_id=batch,
                task_type="foo",
                task_function="bar",
                userid="user_id"
            )
        await self.create_mock_data(
            "submitted",
            amount=100,
            base_task_id="protected",
            task_type="foo",
            task_function="bar",
            userid="user_id"
        )
        batches = ['batch2', 'batch3', 'batch4']
        for batch in batches:
            status = random.choice(discardable_statuses)
            await self.create_mock_data(
                status,
                amount=batch_size,
                base_task_id=batch,
                task_type="foo",
                task_function="bar",
                userid="user_id"
            )

        with self.assertRaises(KeyError):
            await self._store.get_task("doesnt exist")
        with self.assertRaises(KeyError):
            await self._store.get_task("batch1_0")
        with self.assertRaises(KeyError):
            await self._store.get_task("batch2_0")

        good_tasks = ['protected_50', 'batch3_160', 'batch4_140']
        for good_task in good_tasks:
            self.assertEqual((await self._store.get_task(good_task))["task_id"], good_task)

    async def test_slow_dont_deadlock_when_we_cant_remove_tasks(self):
        await self.create_mock_data(
            'submitted',
            amount=15_000,
            base_task_id="protected",
            task_type="foo",
            task_function="bar",
            userid="user_id"
        )

    async def create_mock_data(
        self,
        status: str,
        amount: int = 1,
        base_task_id: str = None,
        task_type: str = "foo",
        task_function: str = "bar",
        task_comment: str = "",
        task_requirements: Optional[Dict] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = 65535,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None,
        userid: str = "userid"
    ):
        for x in range(amount):
            task_id = f"{base_task_id}_{x}" if base_task_id else None
            await self._store.insert_existing_task(
                task_id=task_id,
                status=status,
                task_type=task_type,
                userid=userid,
                task_args={"arg1": 1, "arg2": 2, "arg3": 3},
                task_function=task_function,
                task_function_args=task_function_args or {
                    "function_arg1": 1,
                    "function_arg2": 2,
                    "function_arg3": 3
                },
                task_requirements=task_requirements or {},
                task_comment=task_comment,
                priority=priority,
                metadata=metadata,
                labels=labels
            )
