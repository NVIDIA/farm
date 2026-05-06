# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import platform
import tempfile

from typing import Dict, Tuple, List, Any
from unittest import skipUnless, IsolatedAsyncioTestCase, mock

from nv.svc.core.client.http import HTTPClientSession

from nv.svc.farm.services.capacity.managers.settings import SettingsAgentCapacityManager

from nv.svc.farm.services.controller.facilities.bays import FileBasedMultiSlotBay, OneSlotBay, MultiSlotBay
from nv.svc.farm.services.controller.facilities.bays.capacity import CapacityBasedBay

from tests.services.capacity.custom_test_case import CustomIsolatedAsyncioTestCase


class TestOnSlotBay(IsolatedAsyncioTestCase):

    async def test_available_capacity(self):
        bay_manager = OneSlotBay()

        task_data = {("foo", "bar"): []}

        tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
        self.assertEqual(tasks, [("foo", "bar")])
        self.assertEqual(capacity, {})

    async def test_noavailable_capacity(self):
        bay_manager = OneSlotBay()

        task_data = {("foo", "bar"): [], ("baz", "qux"): ["12345"]}

        tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
        self.assertEqual(tasks, [])
        self.assertEqual(capacity, {})


class TestMultiSlotBay(IsolatedAsyncioTestCase):

    async def test_available_capacity(self):
        bay_manager = MultiSlotBay(max_capacity=5)

        task_data = {("foo", "bar"): []}

        tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
        self.assertEqual(tasks, [("foo", "bar")])
        self.assertEqual(capacity, {})

    async def test_noavailable_capacity(self):
        bay_manager = MultiSlotBay(max_capacity=2)

        task_data = {("foo", "bar"): ["67890"], ("baz", "qux"): ["12345"]}

        tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
        self.assertEqual(tasks, [])
        self.assertEqual(capacity, {})


class TestFileBasedMultiSlotBay(IsolatedAsyncioTestCase):

    @skipUnless(
        platform.system().lower() == "linux",
        "TC agents on Windows doesn't support temp directories"
    )
    async def test_available_capacity(self):
        with tempfile.NamedTemporaryFile(mode="w+") as file:
            json.dump({"max_capacity": 2}, file)
            file.flush()

            bay_manager = FileBasedMultiSlotBay(file.name)

            task_data = {("foo", "bar"): []}

            tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
            self.assertEqual(tasks, [("foo", "bar")])
            self.assertEqual(capacity, {})

    @skipUnless(
        platform.system().lower() == "linux",
        "TC agents on Windows doesn't support temp directories"
    )
    async def test_noavailable_capacity(self):
        with tempfile.NamedTemporaryFile(mode="w+") as file:
            json.dump({"max_capacity": 2}, file)
            file.flush()

            bay_manager = FileBasedMultiSlotBay(file.name)

            task_data = {("foo", "bar"): ["67890"], ("baz", "qux"): ["12345"]}

            tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
            self.assertEqual(tasks, [])
            self.assertEqual(capacity, {})

    @skipUnless(
        platform.system().lower() == "linux",
        "TC agents on Windows doesn't support temp directories"
    )
    async def test_update_capacity(self):
        with tempfile.NamedTemporaryFile(mode="wt") as file:
            json.dump({"max_capacity": 2}, file)
            file.flush()

            bay_manager = FileBasedMultiSlotBay(file.name)

            task_data = {("foo", "bar"): ["67890"], ("baz", "qux"): ["12345"]}

            tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
            self.assertEqual(tasks, [])
            self.assertEqual(capacity, {})

        with tempfile.NamedTemporaryFile(mode="wt") as file:

            json.dump({"max_capacity": 10}, file)
            file.flush()
            bay_manager._capacity_file = file.name

            tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=[])
            self.assertEqual(tasks, [("foo", "bar"), ("baz", "qux")])
            self.assertEqual(capacity, {})


class TestCapacityBay(CustomIsolatedAsyncioTestCase):

    def setUp(self) -> None:

        self._manager = SettingsAgentCapacityManager([], [])

        class FakeResponse:
            def __init__(self, data=None):
                self.data = data or {}

            async def json(self):
                return self.data

        async def _fake_capacity_list_request(*args, **kwargs):
            available = kwargs["json"].get("available", None)
            ignore_strict = kwargs["json"].get("ignore_strict", None)

            data = []
            for k, v in self._manager._capacities.items():
                raw = await v.to_dict()
                raw["identifier"] = k
                data.append(raw)

            if not available:
                return FakeResponse(data)

            filtered_data = []
            for capacity in data:
                if capacity["has_capacity"]:
                    filtered_data.append(capacity)
                    continue

                if capacity["strict"] and not ignore_strict:
                    return FakeResponse([])

            return FakeResponse(filtered_data)

        self.client_session_patcher = mock.patch.object(HTTPClientSession, "_request", _fake_capacity_list_request)
        self.client_session_patcher.start()

        self._bay_manager = CapacityBasedBay("http://localhost:1234")

    def tearDown(self) -> None:
        self._manager.stop()
        self._manager = None
        self._bay_manager = None
        self.client_session_patcher.stop()

    async def _configure_capacities(self, capacities: Dict[str, Dict], root):
        self.dynaconf_setup(config_name=None)
        for key, capacity in capacities.items():
            self._settings.set(key, capacity)
        self._manager.updateSettings(self._settings)

        await self._manager._load_settings_capacities([root])

    async def test_no_capacity(self):
        """Test that if there is no capacity no tasks can be spawned"""

        task_data = {("foo", "bar"): []}
        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=[])
        self.assertEqual(tasks, [])
        self.assertEqual(capacity, {})

    async def test_simple_capacity(self):
        """Test that if there is capacity but no job requirements, the tasks can run."""

        self.dynaconf_setup(config_name="list_capacities.toml")
        self._manager.updateSettings(self._settings)
        await self._manager._load_settings_capacities(["farm.test.root"])

        task_data = {("foo", "bar"): []}

        # Slimmed down version of a job definition.
        job_definitions = [{"name": "foo", "task_function": "bar", "capacity_requirements": {}}]

        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions)
        self.assertEqual(tasks, [("foo", "bar")])
        self.assertIn("foo.bar.limit", capacity)

    async def test_no_mandatory_capacity(self):
        """Test that if there is capacity but no job requirements but there are mandatory capacity requirements that can't be fulfilled, tasks can't run."""
        self._bay_manager = CapacityBasedBay("http://localhost:1234", mandatory_capacity=["my.mandatory.capacity"])

        self.dynaconf_setup(config_name="list_capacities.toml")
        self._manager.updateSettings(self._settings)
        await self._manager._load_settings_capacities(["farm.test.root"])

        task_data = {("foo", "bar"): []}

        # Slimmed down version of a job definition.
        job_definitions = [{"name": "foo", "task_function": "bar", "capacity_requirements": {}}]

        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions)
        self.assertEqual(tasks, [])
        self.assertIn("foo.bar.limit", capacity)

    async def test_mandatory_capacity(self):
        """Test that if there is capacity but no job requirements but there are mandatory capacity requirements that can be fulfilled, tasks can run."""
        self._bay_manager = CapacityBasedBay("http://localhost:1234", mandatory_capacity=["mandatory"])

        await self._configure_capacities(
            {
                'farm.test.root.simple': {"strict": False, "capacity": 10},
                'farm.test.root.mandatory': {"strict": False, "capacity": 10}
            },
            "farm.test.root"
        )

        task_data = {("foo", "bar"): []}

        # Slimmed down version of a job definition.
        job_definitions = [{"name": "foo", "task_function": "bar", "capacity_requirements": {}}]

        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions)
        self.assertEqual(tasks, [("foo", "bar")])
        self.assertIn("simple", capacity)
        self.assertIn("mandatory", capacity)

    async def test_can_run_with_capacity(self):
        """Test that tasks can run when there is capacity matching their resources."""

        await self._configure_capacities(
            {
                "testing.simple": {"strict": False, "capacity": 10},
                "testing.other": {"strict": False, "capacity": 10}
            },
            "testing"
        )

        task_data = {("foo", "bar"): []}

        # Slimmed down version of a job definition.
        job_definitions = [{"name": "foo", "task_function": "bar", "capacity_requirements": {"simple": 1}}]

        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions)
        self.assertEqual(tasks, [("foo", "bar")])
        self.assertIn("simple", capacity)
        self.assertIn("other", capacity)

    async def test_cannot_run_without_capacity(self):
        """Test that tasks cannot run when there is capacity matching their resources."""

        await self._configure_capacities(
            {
                "testing.simple": {"strict": False, "capacity": 0},
                "testing.other": {"strict": False, "capacity": 10}
            },
            "testing"
        )

        task_data = {("foo", "bar"): []}

        # Slimmed down version of a job definition.
        job_definitions = [{"name": "foo", "task_function": "bar", "capacity_requirements": {"simple": 1}}]

        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions)
        self.assertEqual(tasks, [])
        self.assertNotIn("simple", capacity)
        self.assertIn("other", capacity)

    async def test_tasks_are_filtered_on_capacity(self):
        """Test that tasks without capacity are filtered out."""

        await self._configure_capacities(
            {
                "testing.simple": {"strict": False, "capacity": 0},
                "testing.other": {"strict": False, "capacity": 10}
            },
            "testing"
        )

        task_data = {("foo", "bar"): []}

        # Slimmed down version of a job definition.
        job_definitions = [
            {"name": "foo", "task_function": "bar", "capacity_requirements": {"simple": 1}},
            {"name": "baz", "task_function": "qux", "capacity_requirements": {"other": 1}}
        ]

        tasks, capacity = await self._bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions)
        self.assertEqual(tasks, [("baz", "qux")])
        self.assertNotIn("simple", capacity)
        self.assertIn("other", capacity)

    async def test_multislot_gpu_label_parsing(self):
        """Test that the multislot bay parses gpu counts properly from gpuSpecification labels."""

        bay_manager = MultiSlotBay(max_capacity=10)

        # unknown instance label formats should fall back to 1
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="unknown"), 1)
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="unknown_xanything"), 1)

        # nvidia k8s gpu operator style instance type labels
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="nvidia.com/gpu_4x"), 4)
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="nvidia.com/gpu_1x"), 1)

        # nvidia dgx cloud style instance type labels
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="DGX-CLOUD.GPU.L40_1x"), 1)
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="DGX-CLOUD.GPU.L40_2x"), 2)
        self.assertEqual(bay_manager._get_gpu_count(gpu_instance_type="DGX-CLOUD.GPU.L40_4x"), 4)

    async def test_multislot_tasks_are_filtered_on_gpu_capacity_not_full(self):
        """Test the multislot bay tasks are filtered out when there is GPU capacity."""

        bay_manager = MultiSlotBay(max_capacity=10)

        not_full_task_job_definition_map: Dict[str, str] = {
            "123": "single-gpu",
            "124": "multi-gpu",
            "125": "multi-gpu"
        }
        task_data: Dict[Tuple[str, str], List[str]] = {("kit-service", "render.run"): list(not_full_task_job_definition_map.keys())}
        job_definitions: List[Dict[str, Any]] = [
            {"name": "single-gpu", "job_type": "kit-service", "task_function": "render.run", "capacity_requirements": {"gpuSpecification": {"instanceType": "nvidia.com/gpu_1x"}}},
            {"name": "multi-gpu", "job_type": "kit-service", "task_function": "render.run", "capacity_requirements": {"gpuSpecification": {"instanceType": "nvidia.com/gpu_4x"}}}
        ]

        tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions, taskid_to_job_definition_map=not_full_task_job_definition_map)
        self.assertEqual(tasks, [("kit-service", "render.run")])
        self.assertEqual(capacity, {})

    async def test_multislot_tasks_are_filtered_on_gpu_capacity_full(self):
        """Test the multislot bay tasks are filtered out when there is no GPU capacity."""

        bay_manager = MultiSlotBay(max_capacity=10)

        # this list of tasks should exceed the gpu capacity, but if we're not calculating gpus properly, it'll fit when tasks:gpus are 1:1.
        full_task_job_definition_map: Dict[str, str] = {
            "123": "single-gpu",
            "124": "multi-gpu",
            "125": "multi-gpu",
            "126": "multi-gpu",
            "127": "multi-gpu",
            "128": "multi-gpu"
        }
        task_data: Dict[Tuple[str, str], List[str]] = {("kit-service", "render.run"): list(full_task_job_definition_map.keys())}
        job_definitions: List[Dict[str, Any]] = [
            {"name": "single-gpu", "job_type": "kit-service", "task_function": "render.run", "capacity_requirements": {"gpuSpecification": {"instanceType": "nvidia.com/gpu_1x"}}},
            {"name": "multi-gpu", "job_type": "kit-service", "task_function": "render.run", "capacity_requirements": {"gpuSpecification": {"instanceType": "nvidia.com/gpu_4x"}}}
        ]

        tasks, capacity = await bay_manager.get_capacity(tasks=task_data, job_definitions=job_definitions, taskid_to_job_definition_map=full_task_job_definition_map)
        self.assertEqual(tasks, [])
        self.assertEqual(capacity, {})
