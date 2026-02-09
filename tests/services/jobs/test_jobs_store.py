# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json

import unittest

from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore


class TestBaseJobStore(unittest.IsolatedAsyncioTestCase):

    async def setUp(self) -> None:
        self._job_store = BaseJobStore()


class DummyStore(BaseJobStore):

    async def _load_jobs(self) -> bool:
        return True
