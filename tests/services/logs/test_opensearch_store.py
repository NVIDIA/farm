# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import unittest
import uuid

from nv.svc.farm.services.logs.facilities.opensearch import OpensearchLogStore


LOGS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Integer tincidunt lacus nec arcu malesuada, sed congue diam dignissim.",
    "In ac est at risus consectetur commodo et sit amet mauris.",
    "In eget erat a ante rutrum viverra vel quis turpis.",
]


class TestElasticsearchLogStore(unittest.IsolatedAsyncioTestCase):

    def _get_log_store(self) -> OpensearchLogStore:
        return OpensearchLogStore(
            hosts=["localhost:9200"],
            index="farm-a",
            use_ssl=True,
            verify_certs=False
        )

    async def _get_logs(self, store: OpensearchLogStore, task_id: str, agent_id: str = None, log_entries=50):
        await asyncio.sleep(1)
        return await store.get_logs(task_id=task_id, agent_id=agent_id, log_entries=log_entries)

    @unittest.skip("Integration test, requires running Opensearch server.")
    async def test_set_logs(self):
        """ Test that logs are set when writing logs"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)

        result = await self._get_logs(store, task_id, agent_id=agent_id)
        self.assertEqual(result["logs"], logs)
        await store.close()

    @unittest.skip("Integration test, requires running Opensearch server.")
    async def test_append_additional_logs(self):
        """Test that additional logs are appended"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs="additional logs")

        result = await self._get_logs(store, task_id, agent_id=agent_id, log_entries=0)
        self.assertEqual(result["logs"], logs + "additional logs")
        await store.close()

    @unittest.skip("Integration test, requires running Opensearch server.")
    async def test_updated_at_time_change_on_additional_logs(self):
        """Test that the 'updated_at' field increases when new logs are appended"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)

        result = await self._get_logs(store, task_id, agent_id=agent_id)
        created_at = result["created_at"]
        updated_at = result["updated_at"]

        self.assertEqual(created_at, updated_at)

        await asyncio.sleep(.1)
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs="additional logs")

        result = await self._get_logs(store, task_id, agent_id=agent_id)

        self.assertEqual(result["created_at"], created_at)
        self.assertTrue(result["updated_at"] > updated_at)
        await store.close()

    @unittest.skip("Integration test, requires running Opensearch server.")
    async def test_raises_when_no_logs_are_found(self):
        agent_id = "foo"
        task_id = str(uuid.uuid4())

        store = self._get_log_store()
        with self.assertRaises(KeyError):
            await store.get_logs(task_id, agent_id=agent_id)
        await store.close()

    @unittest.skip("Dedup has been disabled.")
    async def test_remove_duplicate_log_lines(self):
        store = OpensearchLogStore(["foo"])

        logs = [
            {"_source": {"message": "[0.106s] [ext: foo.bar.pipapi-0.0.0] startup\n[0.111s] [ext: foo.bar.pip_archive-0.0.0] startup\n"}},
            {"_source": {"message": "[0.111s] [ext: foo.bar.pip_archive-0.0.0] startup\n"}},
            {"_source": {"message": "[0.115s] [ext: foo.bar.loop-default-0.1.0] startup\n"}},
        ]

        data = store._mangle_logs(logs)
        self.assertEqual(
            data,
            set(["[0.106s] [ext: foo.bar.pipapi-0.0.0] startup", "[0.111s] [ext: foo.bar.pip_archive-0.0.0] startup", "[0.115s] [ext: foo.bar.loop-default-0.1.0] startup"])
        )
