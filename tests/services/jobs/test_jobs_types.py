# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import unittest

from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.job_types.kit import KitJob, KitServiceJob


class TestKitTask(unittest.IsolatedAsyncioTestCase):

    def test_KitJob_creation_args_added(self):
        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )
        self.assertIn("--/log/flushStandardStreamOutput=true", job.args)

    def test_KitServiceJob_creation_task_args_added(self):

        port = "1234"
        os.environ["NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT"] = port

        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT")

        self.assertIn("omni.services.farm.agent.runner", job.args)
        self.assertIn(f"--/exts/omni.services.farm.agent.runner/controller=http://127.0.0.1:{port}/agent", job.args)
        self.assertIn("--/log/flushStandardStreamOutput=true", job.args)

    def test_KitJob_creation_controller_args_added(self):
        """Assert that the controller address is passed through to the Kit instance but not the agent.runner"""
        port = "1234"
        os.environ["NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT"] = port

        job = KitJob.from_job_definition(
            JobDefinition("foo", "kit", "create.sh", "path", args=["foo.services.test"])
        )
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT")

        self.assertNotIn("omni.services.farm.agent.runner", job.args)
        self.assertIn(f"--/exts/omni.services.farm.agent.runner/controller=http://127.0.0.1:{port}/agent", job.args)

    def test_KitJob_creation_controller_args_added_custom_protocol(self):
        """Assert that the controller address is passed through to the Kit instance but not the agent.runner"""
        port = "1234"
        protocol = "foo"
        os.environ["NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT"] = port
        os.environ["NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PROTOCOL"] = protocol

        job = KitJob.from_job_definition(
            JobDefinition("foo", "kit", "create.sh", "path", args=["foo.services.test"])
        )
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT")
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PROTOCOL")

        self.assertNotIn("omni.services.farm.agent.runner", job.args)
        self.assertIn(f"--/exts/omni.services.farm.agent.runner/controller={protocol}://127.0.0.1:{port}/agent", job.args)

    def test_KitJob_creation_controller_args_added_custom_host(self):
        """Assert that the controller address is passed through to the Kit instance but not the agent.runner"""
        port = "1234"
        host = "foo"
        os.environ["NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT"] = port
        os.environ["NV__SVC__FARM__JOBS__AGENT_CONTROLLER_HOST"] = host

        job = KitJob.from_job_definition(
            JobDefinition("foo", "kit", "create.sh", "path", args=["foo.services.test"])
        )
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_CONTROLLER_PORT")
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_CONTROLLER_HOST")

        self.assertNotIn("omni.services.farm.agent.runner", job.args)
        self.assertIn(f"--/exts/omni.services.farm.agent.runner/controller=http://{host}:{port}/agent", job.args)

    def test_resolve_environment_variables(self):
        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )

        self.assertIn("OV_FARM_VERSION", job.env)

    def test_default_no_gpu_assigned(self):
        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )

        self.assertNotIn("--/renderer/multiGpu/enabled=false", job.args)

    def test_assign_gpu_to_agent(self):
        assigned_gpu = "5"
        os.environ["NV__SVC__FARM__JOBS__AGENT_ASSIGNED_GPU"] = assigned_gpu

        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_ASSIGNED_GPU")

        self.assertIn("--/renderer/multiGpu/enabled=false", job.args)
        self.assertIn(f"--/renderer/activeGpu={assigned_gpu}", job.args)

    def test_assign_gpu_0_to_agent(self):
        assigned_gpu = "0"
        os.environ["NV__SVC__FARM__JOBS__AGENT_ASSIGNED_GPU"] = assigned_gpu
        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )
        os.environ.pop("NV__SVC__FARM__JOBS__AGENT_ASSIGNED_GPU")

        self.assertIn("--/renderer/multiGpu/enabled=false", job.args)
        self.assertIn(f"--/renderer/activeGpu={assigned_gpu}", job.args)

    def test_KitJob_creation_fastshutdown_added(self):
        job = KitServiceJob.from_job_definition(
            JobDefinition("foo", "kit-service", "create.sh", "path", args=["foo.services.test"])
        )
        self.assertIn("--/app/fastShutdown=true", job.args)
