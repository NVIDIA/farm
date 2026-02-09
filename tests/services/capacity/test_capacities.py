# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch, MagicMock
from unittest import IsolatedAsyncioTestCase

import nv.svc.farm.services.capacity as _capacities


class TestCPUCapacities(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        data = await _capacities.CPU.async_init()
        self._identifier = list(data.keys())[0]
        self._capacity = data[self._identifier]

    async def asyncTearDown(self) -> None:
        self._identifier = None
        self._capacity = None

    async def test_identifier(self):
        self.assertEqual("cpu", self._identifier) 
        self.assertEqual("cpu", self._capacity.identifier)

    async def test_capacity_value(self):
        self.assertTrue(self._capacity.capacity > 0)

    async def test_has_capacity(self):
        self.assertTrue(await self._capacity.has_capacity())

    async def test_acquire_capacity(self):
        self.assertTrue(await self._capacity.acquire_capacity())

    async def test_release_capacity(self):
        self.assertTrue(await self._capacity.release_capacity())


class TestGPUCapacities(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:

        def _handle(index: int):
            return index

        def _get_name(index: int):
            data = {
                0: b"NVIDIA GeForce GT 710",
                1: b"NVIDIA GeForce RTX 3090",
                2: b"NVIDIA GeForce RTX 3090",
            }
            return data[index]

        with patch("pynvml.nvmlDeviceGetCount", return_value=3):
            with patch("pynvml.nvmlDeviceGetHandleByIndex", wraps=_handle):
                with patch("pynvml.nvmlDeviceGetName", wraps=_get_name):
                    with patch("pynvml.nvmlInit", MagicMock(return_value=None)):
                        data = await _capacities.GPU.async_init()

        self._keys = list(data.keys())
        self._data = data

    async def asyncTearDown(self) -> None:
        self._keys = None
        self._data = None

    async def test_collected_gpus(self):
        self.assertEqual(2, len(self._keys))

    async def test_identifier(self):
        key_0 = self._keys[0]
        key_1 = self._keys[1]

        self.assertEqual(key_0, "nvidia.geforce.gt.710")
        self.assertEqual(key_1, "nvidia.geforce.rtx.3090")

        self.assertEqual(self._data[key_0].identifier, "nvidia.geforce.gt.710")
        self.assertEqual(self._data[key_1].identifier, "nvidia.geforce.rtx.3090")

    async def test_capacity_value_gpu0(self):
        self.assertEqual(self._data["nvidia.geforce.gt.710"].capacity, 1)

    async def test_capacity_value_gpu1(self):
        self.assertEqual(self._data["nvidia.geforce.rtx.3090"].capacity, 2)

    async def test_has_capacity(self):
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].has_capacity())

    async def test_acquire_capacity(self):
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].has_capacity())
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].acquire_capacity())
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].has_capacity())

    async def test_no_capacity(self):
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].acquire_capacity())
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].acquire_capacity())
        self.assertFalse(await self._data["nvidia.geforce.rtx.3090"].has_capacity())

    async def test_acquire_to_much_capacity(self):
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].acquire_capacity())
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].acquire_capacity())

        with self.assertRaises(_capacities.NoCapacityError):
            await self._data["nvidia.geforce.rtx.3090"].acquire_capacity()

    async def test_release_capacity(self):
        self.assertEqual(self._data["nvidia.geforce.rtx.3090"]._remaining_capacity, 2)
        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].acquire_capacity())
        self.assertEqual(self._data["nvidia.geforce.rtx.3090"]._remaining_capacity, 1)

        self.assertTrue(await self._data["nvidia.geforce.rtx.3090"].release_capacity())
        self.assertEqual(self._data["nvidia.geforce.rtx.3090"]._remaining_capacity, 2)

    async def test_release_to_much_capacity(self):
        with self.assertRaises(_capacities.CapacityReleaseError):
            await self._data["nvidia.geforce.rtx.3090"].release_capacity()


class TestMemoryCapacities(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        data = await _capacities.Memory.async_init()

        self._identifier = list(data.keys())[0]
        self._capacity = data[self._identifier]

    async def asyncTearDown(self) -> None:
        self._identifier = None
        self._capacity = None

    async def test_identifier(self):
        self.assertEqual("memory", self._identifier) 
        self.assertEqual("memory", self._capacity.identifier)

    async def test_capacity_value(self):
        self.assertTrue(self._capacity.capacity > 0)

    async def test_has_capacity(self):
        self.assertTrue(await self._capacity.has_capacity())

    async def test_acquire_capacity(self):
        self.assertTrue(await self._capacity.acquire_capacity())

    async def test_release_capacity(self):
        self.assertTrue(await self._capacity.release_capacity())

    async def test_has_no_capacity(self):
        self._capacity._minimum_ram_required = 1 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024  # Lots of RAM needed
        self.assertFalse(await self._capacity.has_capacity())
