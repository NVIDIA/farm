# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from pydantic import ValidationError

from nv.svc.farm.services.controller.router import TaskCheckinModel


class TestTaskCheckinModel(TestCase):
    def test_valid_complete_model(self):
        data = {
            "task_id": "abc123",
            "status": "running",
            "comment": "test comment",
            "metrics": "test metrics",
            "current_step_index": 5,
            "total_step_count": 10,
            "progress": 0.5,
            "status_message": "Processing step 5/10",
            "time_remaining": 300.5
        }
        model = TaskCheckinModel(**data)
        self.assertEqual(model.task_id, "abc123")
        self.assertEqual(model.current_step_index, 5)
        self.assertEqual(model.progress, 0.5)
        self.assertEqual(model.time_remaining, 300.5)

    def test_valid_minimal_model(self):
        # Only task_id is required, all other fields can be None or empty
        data = {
            "task_id": "abc123",
            "status": "",
            "comment": "",
            "metrics": "",
        }
        model = TaskCheckinModel(**data)
        self.assertEqual(model.task_id, "abc123")
        self.assertIsNone(model.current_step_index)
        self.assertIsNone(model.progress)
        self.assertIsNone(model.time_remaining)

    def test_invalid_progress_range(self):
        data = {
            "task_id": "abc123",
            "progress": 1.5  # Should be <= 1.0
        }
        with self.assertRaises(ValidationError) as context:
            TaskCheckinModel(**data)
        self.assertIn("Input should be less than or equal to 1", str(context.exception))

    def test_invalid_negative_values(self):
        data = {
            "task_id": "abc123",
            "current_step_index": -1,  # Should be >= 0
            "total_step_count": -5,    # Should be >= 0
            "time_remaining": -10.0    # Should be >= 0
        }
        with self.assertRaises(ValidationError) as context:
            TaskCheckinModel(**data)
        self.assertIn("Input should be greater than or equal to 0", str(context.exception))

    def test_missing_required_field(self):
        data = {
            # Missing required task_id
            "status": "running",
            "progress": 0.5
        }
        with self.assertRaises(ValidationError) as context:
            TaskCheckinModel(**data)
        self.assertIn("Field required", str(context.exception))

    def test_invalid_type_values(self):
        data = {
            "task_id": "abc123",
            "current_step_index": "not an integer",
            "progress": "not a float",
            "time_remaining": "not a float"
        }
        with self.assertRaises(ValidationError) as context:
            TaskCheckinModel(**data)
        self.assertIn("Input should be a valid integer", str(context.exception))

    def test_none_values_accepted(self):
        data = {
            "task_id": "abc123",
            "current_step_index": None,
            "total_step_count": None,
            "progress": None,
            "status_message": None,
            "time_remaining": None
        }
        model = TaskCheckinModel(**data)
        self.assertIsNone(model.current_step_index)
        self.assertIsNone(model.total_step_count)
        self.assertIsNone(model.progress)
        self.assertIsNone(model.status_message)
        self.assertIsNone(model.time_remaining)

    def test_omitted_values_default_to_none(self):
        data = {
            "task_id": "abc123",
            # All optional fields omitted
        }
        model = TaskCheckinModel(**data)
        self.assertIsNone(model.current_step_index)
        self.assertIsNone(model.total_step_count)
        self.assertIsNone(model.progress)
        self.assertIsNone(model.status_message)
        self.assertIsNone(model.time_remaining)
