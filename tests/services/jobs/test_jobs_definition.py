# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest

from nv.svc.farm.services.jobs.definitions import JobDefinition


class TestJobsDefinition(unittest.IsolatedAsyncioTestCase):

    def test_slots_and_dict_are_in_sync(self):
        """Test that the slots are reflected in the classes to_dict"""
        # Test will help validate that to_dict and __slots__ are kept in sync.

        jobDef = JobDefinition("foo", "bar", "my-command", "path")
        self.assertEqual(list(jobDef.__slots__), list(jobDef.to_dict().keys()))

    def test_job_spec_path_empty_param(self):
        jobDef = JobDefinition(
            name="foo",
            job_type="bar",
            command="my-command",
            job_spec_path="",
            args=["--foo", "--bar=123"],
            env={"FOO1": "test"},
            extension_paths=["/../exts", "/../exts-extra"]
        )
        self.assertEqual(jobDef.args, ["--foo", "--bar=123"])
        self.assertEqual(jobDef.env, {"FOO1": "test"})
        self.assertEqual(jobDef.extension_paths, ["/../exts", "/../exts-extra"])
