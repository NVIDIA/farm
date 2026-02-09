# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the database task backend implementation."""

import os
import tempfile
from unittest import IsolatedAsyncioTestCase

from nv.svc.farm.services.tasks.facilities.database.manager import DatabaseManagerFacility
from nv.svc.farm.services.tasks.facilities.tasks.backends import InvalidLabelError
from nv.svc.farm.services.tasks.facilities.tasks.task_backend import TaskDatabaseBackend


class DatabaseTaskBackendTestCase(IsolatedAsyncioTestCase):
    """Test cases for the task database backend implementation."""

    async def asyncSetUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        sanitized_temp_dir_path = os.path.join(self._temp_dir.name, "temp.db").replace("\\", "/")
        connection_string = f"sqlite:///{sanitized_temp_dir_path}"

        os.environ["NV__SVC__FARM__TASKS__DBS__test-handle__connection_string"] = connection_string
        self.database_facility = DatabaseManagerFacility()

        self._backend = TaskDatabaseBackend(
            database_handle="test-handle",
        )
        await self._backend.start()

    def tearDown(self):
        self._teardown_temporary_db()
        os.environ.pop("NV__SVC__FARM__TASKS__DBS__test-handle__connection_string")

    def _teardown_temporary_db(self) -> None:
        self.database_facility.stop()
        self.database_facility = None
        self._temp_dir = None

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

    async def test_get_next_task_prioritised_with_labels(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        task = await self._backend.get_next_task_prioritised(
            [("foo", "bar")],
            "agent_a",
            labels=["foo", "bar"]
        )
        self.assertEqual(task["task_id"], "task_0")

    async def test_get_next_task_prioritised_task_with_labels_no_label_selection(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        task = await self._backend.get_next_task_prioritised(
            [("foo", "bar")],
            "agent_a",
        )
        self.assertEqual(task, None)

    async def test_get_next_task_prioritised_task_without_labels_no_label_selection(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        task = await self._backend.get_next_task_prioritised(
            [("foo", "bar")],
            "agent_a",
        )
        self.assertEqual(task["task_id"], "task_0")

    async def test_get_next_task_prioritised_task_with_labels_different_labels(self):
        """Test task prioritization with different labels."""
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        task = await self._backend.get_next_task_prioritised(
            [("foo", "bar")],
            "agent_a",
            labels=["taz"]
        )
        self.assertEqual(task, None)

    async def test_get_next_task_prioritised_task_with_invalid_labels(self):
        """Test task prioritization with invalid labels."""
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar", labels=["foo", "bar"])
        with self.assertRaises(InvalidLabelError):
            await self._backend.get_next_task_prioritised(
                [("foo", "bar")],
                "agent_a",
                labels=["withacomma,"]
            )

    async def test_updating_a_revision_with_the_same_status_updates_the_revision_rather_than_creating_another_one(self):
        await self.create_mock_data("submitted", base_task_id="task", task_type="foo", task_function="bar")
        for _ in range(5):
            await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id")
        # a different user
        await self._backend.update_task(task_id="task_0", task_type="foo", task_function="bar", status="running", userid="user_id2")
        revisions = await self._backend.get_task_revision_history("task_0")

        self.assertEqual(len(revisions), 3)

    async def test_task_function_args(self):
        """Test that task function args are decoded and returned properly."""
        await self.create_mock_data("submitted")
        task = await self._backend.get_next_task_prioritised([("foo", "bar")], "agent_a",)
        self.assertEqual(task["task_function_args"], {"function_arg1": 1, "function_arg2": 2, "function_arg3": 3})

    async def test_user_id(self):
        """Test that the user-id is retrieved properly."""
        await self.create_mock_data("submitted", userid="john-doe")
        task = await self._backend.get_next_task_prioritised([("foo", "bar")], "agent_a",)
        self.assertEqual(task["userid"], "john-doe")

    async def test_comment(self):
        """Test that comments are retrieved properly."""
        comment = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        await self.create_mock_data("submitted", task_comment=comment)
        task = await self._backend.get_next_task_prioritised([("foo", "bar")], "agent_a",)
        self.assertEqual(task["task_comment"], comment)

    async def test_get_tasks_bulk(self):
        """Test retrieving multiple tasks in bulk."""
        # Create test tasks
        task_ids = []
        for i in range(5):
            task_id = await self._backend.add_task(
                status="submitted",
                task_type="test_type",
                userid="test_user",
                task_args={"arg": i},
                task_id=f"test_task_{i}"
            )
            task_ids.append(task_id)

        # Test retrieving all tasks
        tasks = await self._backend.get_tasks_bulk(task_ids)
        self.assertEqual(len(tasks), 5)
        for task in tasks:
            self.assertIn(task["task_id"], task_ids)

        # Test status filtering
        await self._backend.update_task(
            task_id=task_ids[0],
            task_type="test_type",
            task_function="",
            status="running",
            userid="test_user"
        )
        tasks = await self._backend.get_tasks_bulk(task_ids, statuses=["running"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task_id"], task_ids[0])

    async def test_get_tasks_bulk_not_found(self):
        """Test bulk retrieval with non-existent task IDs."""
        # Create one test task
        task_id = await self._backend.add_task(
            status="submitted",
            task_type="test_type",
            userid="test_user",
            task_args={"arg": 1}
        )

        # Try to retrieve with mix of existing and non-existent IDs
        tasks = await self._backend.get_tasks_bulk([task_id, "non_existent_1", "non_existent_2"])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task_id"], task_id)

    async def test_update_tasks_status_bulk_no_exclusions(self):
        """Test bulk updating task statuses without exclusions."""
        # Create test tasks
        task_ids = []
        for i in range(3):
            task_id = await self._backend.add_task(
                status="submitted",
                task_type="test_type",
                userid="test_user",
                task_args={"arg": i},
                task_id=f"test_task_{i}"
            )
            task_ids.append(task_id)

        # Test bulk update without excluded statuses
        updated_ids = await self._backend.update_tasks_status_bulk(
            task_ids=task_ids,
            new_status="running"
        )

        # Verify all tasks were updated
        self.assertEqual(len(updated_ids), 3)
        tasks = await self._backend.get_tasks_bulk(updated_ids)
        for task in tasks:
            self.assertEqual(task["status"], "running")

    async def test_update_tasks_status_bulk_nonexistent_tasks(self):
        """Test bulk updating with some nonexistent task IDs."""
        # Create one test task
        task_id = await self._backend.add_task(
            status="submitted",
            task_type="test_type",
            userid="test_user",
            task_args={"arg": 1},
            task_id="test_task_0"
        )

        # Try to update mix of existing and non-existent tasks
        updated_ids = await self._backend.update_tasks_status_bulk(
            task_ids=[task_id, "non_existent_1", "non_existent_2"],
            new_status="cancelled"
        )

        # Verify only existing task was updated
        self.assertEqual(len(updated_ids), 1)
        self.assertEqual(updated_ids[0], task_id)
        task = await self._backend.get_task(task_id)
        self.assertEqual(task["status"], "cancelled")
