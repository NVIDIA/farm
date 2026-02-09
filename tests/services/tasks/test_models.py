# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from pydantic import ValidationError

from nv.svc.farm.services.tasks.router import TaskProgressModel


class TestTaskProgressModel(TestCase):
    def test_valid_complete_model(self):
        data = {
            "current_step_index": 5,
            "total_step_count": 10,
            "progress": 0.5,
            "status_message": "Processing step 5/10",
            "time_remaining": 300.5
        }
        model = TaskProgressModel(**data)
        self.assertEqual(model.current_step_index, 5)
        self.assertEqual(model.total_step_count, 10)
        self.assertEqual(model.progress, 0.5)
        self.assertEqual(model.status_message, "Processing step 5/10")
        self.assertEqual(model.time_remaining, 300.5)

    def test_valid_minimal_model(self):
        # All fields are optional
        data = {}
        model = TaskProgressModel(**data)
        self.assertIsNone(model.current_step_index)
        self.assertIsNone(model.total_step_count)
        self.assertIsNone(model.progress)
        self.assertIsNone(model.status_message)
        self.assertIsNone(model.time_remaining)

    def test_invalid_progress_range(self):
        data = {
            "progress": 1.5  # Should be <= 1.0
        }
        with self.assertRaises(ValidationError) as context:
            TaskProgressModel(**data)
        self.assertIn("Input should be less than or equal to 1", str(context.exception))

    def test_invalid_negative_values(self):
        data = {
            "current_step_index": -1,  # Should be >= 0
            "total_step_count": -5,    # Should be >= 0
            "time_remaining": -10.0    # Should be >= 0
        }
        with self.assertRaises(ValidationError) as context:
            TaskProgressModel(**data)
        self.assertIn("Input should be greater than or equal to 0", str(context.exception))

    def test_invalid_type_values(self):
        data = {
            "current_step_index": "not an integer",
            "total_step_count": "not an integer",
            "progress": "not a float",
            "time_remaining": "not a float"
        }
        with self.assertRaises(ValidationError) as context:
            TaskProgressModel(**data)
        self.assertIn("Input should be a valid integer", str(context.exception))

    def test_none_values_accepted(self):
        data = {
            "current_step_index": None,
            "total_step_count": None,
            "progress": None,
            "status_message": None,
            "time_remaining": None
        }
        model = TaskProgressModel(**data)
        self.assertIsNone(model.current_step_index)
        self.assertIsNone(model.total_step_count)
        self.assertIsNone(model.progress)
        self.assertIsNone(model.status_message)
        self.assertIsNone(model.time_remaining)

    def test_omitted_values_default_to_none(self):
        data = {}  # All fields omitted
        model = TaskProgressModel(**data)
        self.assertIsNone(model.current_step_index)
        self.assertIsNone(model.total_step_count)
        self.assertIsNone(model.progress)
        self.assertIsNone(model.status_message)
        self.assertIsNone(model.time_remaining)
