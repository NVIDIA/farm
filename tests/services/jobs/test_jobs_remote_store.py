# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import patch, AsyncMock

from nv.svc.core import main

from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.facilities.store.remote import RemoteJobStore


class TestRemoteJobStore(unittest.IsolatedAsyncioTestCase):

    def setUp(self):

        self._job_data = {
            "test-job": JobDefinition(name="test-job", job_type="kit-service", command="foo").to_dict(),
            "test-job2": JobDefinition(name="test-job2", job_type="kit-service", command="foo").to_dict()
        }

        async def load_jobs():
            return self._job_data

        mock_data = AsyncMock(name="mock-data")
        mock_data.json.side_effect = load_jobs

        mock_response = AsyncMock(name="mock-response")
        mock_response.get.return_value = mock_data

        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_response

        self.client_session_patcher = patch("nv.svc.core.client.http.HTTPClientSession", return_value=mock_session)
        self.client_session_patcher.start()

    def tearDown(self) -> None:
        self.client_session_patcher.stop()

    async def test_job_loading(self):
        job_store = RemoteJobStore("http://localhost:1234/queue/management/jobs/load", fetch_interval=0)
        await job_store.load_jobs()

        self.assertIn("test-job", job_store.job_specs.keys())
        self.assertEqual(job_store.job_specs["test-job"].command, "foo")

    async def test_job_loading_does_not_update_if_no_change(self):
        job_store = RemoteJobStore("http://localhost:1234/queue/management/jobs/load", fetch_interval=0)
        res = await job_store._load_jobs()
        self.assertTrue(res)

        res = await job_store._load_jobs()
        self.assertFalse(res)

    async def test_job_loading_does_update_if_changed_extra_job(self):
        job_store = RemoteJobStore("http://localhost:1234/queue/management/jobs/load", fetch_interval=0)
        await job_store.load_jobs()
        self.assertNotIn("test-job3", job_store.job_specs.keys())

        self._job_data["test-job3"] = JobDefinition("test-job", "kit-service", "foo", None).to_dict()
        res = await job_store._load_jobs()
        self.assertTrue(res)
        self.assertIn("test-job3", job_store.job_specs.keys())

    async def test_job_loading_does_update_if_job_changed(self):
        job_store = RemoteJobStore("http://localhost:1234/queue/management/jobs/load", fetch_interval=0)
        await job_store.load_jobs()

        assert job_store._current_job_specifications["test-job2"]["name"] == "test-job2"

        self._job_data["test-job2"] = JobDefinition("foo", "kit-service", "foo").to_dict()

        res = await job_store._load_jobs()

        self.assertTrue(res)
        self.assertEqual("foo", job_store.job_specs["test-job2"].name)

    async def test_ensure_saving_does_not_get_implemented(self):
        "Make sure that saving does not work as it should not be supported for remote stores due to security risks"
        job_store = RemoteJobStore("http://localhost:1234/queue/management/jobs/load", fetch_interval=0)

        with self.assertRaises(NotImplementedError):
            await job_store.save_job(None)

    async def test_ensure_change_settings_does_not_get_implemented(self):
        "Make sure that changing job store settings does not work as it should not be supported for remote stores due to security risks"
        job_store = RemoteJobStore("http://localhost:1234/queue/management/jobs/load", fetch_interval=0)

        with self.assertRaises(NotImplementedError):
            await job_store.update_settings(None)
