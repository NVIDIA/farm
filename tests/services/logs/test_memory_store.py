# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import uuid
from typing import Dict

from unittest import IsolatedAsyncioTestCase

from nv.svc.farm.services.logs.facilities.memory import MemoryLogStore


LOGS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Integer tincidunt lacus nec arcu malesuada, sed congue diam dignissim.",
    "In ac est at risus consectetur commodo et sit amet mauris.",
    "In eget erat a ante rutrum viverra vel quis turpis.",
]

LOGS_DORIAN_GRAY = [
    "The studio was filled with the rich odour of roses, ",
    "and when the light summer wind stirred amidst the trees of the garden, ",
    "there came through the open door the heavy scent of the lilac, ",
    "or the more delicate perfume of the pink-flowering thorn.",
]


class TestMemoryLogStore(IsolatedAsyncioTestCase):
    def _get_log_store(self) -> MemoryLogStore:
        return MemoryLogStore()

    async def test_set_logs(self):
        """Test that logs are set when writing logs"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)

        result: Dict[str, str] = await store.get_logs(task_id, agent_id=agent_id)
        self.assertTrue(result["logs"].endswith(logs))

    async def test_append_additional_logs(self):
        """Test that additional logs are appended"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs="additional logs")

        result: Dict[str, str] = await store.get_logs(task_id, agent_id=agent_id)

        self.assertTrue(result["logs"].endswith(logs + "additional logs"))

    async def test_updated_at_time_change_on_additional_logs(self):
        """Test that the 'updated_at' field increases when new logs are appended"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)

        result = await store.get_logs(task_id, agent_id=agent_id)
        created_at = result["created_at"]
        updated_at = result["updated_at"]

        self.assertEqual(created_at, updated_at)

        await asyncio.sleep(0.1)
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs="additional logs")

        result = await store.get_logs(task_id, agent_id=agent_id)

        self.assertEqual(result["created_at"], created_at)
        self.assertTrue(result["updated_at"] > updated_at)

    async def test_raises_when_no_logs_are_found(self):
        agent_id = "foo"
        task_id = str(uuid.uuid4())

        store = self._get_log_store()
        with self.assertRaises(KeyError):
            await store.get_logs(task_id, agent_id=agent_id)

    async def test_get_latest_single_agent_no_agent_id(self):
        """Test that the logs returned when no agent ID is given and there has been only a single agent returns those logs when latest_only is True"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)

        result: Dict[str, str] = await store.get_logs(task_id)
        self.assertTrue(result["logs"].endswith(logs))

    async def test_get_all_multi_agent(self):
        """Test that all logs are returned when no agent ID is given and latest_only is false and multiple agents worked on the task"""

        agent_id = "foo"
        task_id = str(uuid.uuid4())

        logs = "".join(LOGS)
        dorian = "".join(LOGS_DORIAN_GRAY)

        store = self._get_log_store()
        await store.set_logs(agent_id=agent_id, task_id=task_id, logs=logs)

        await asyncio.sleep(0.1)
        await store.set_logs(agent_id="bar", task_id=task_id, logs=dorian)

        result = await store.get_logs(task_id, latest_only=False)
        self.assertIn(logs, result["logs"])
        self.assertIn(dorian, result["logs"])

    async def test_overflow_tasks(self):
        """Test that the list of tasks is constrained"""

        logs = "".join(LOGS)

        store = self._get_log_store()

        for _x in range(0, 2_000):
            await store.set_logs(agent_id="", task_id=str(uuid.uuid4()), logs=logs)

        # we have no method to inspect the number of log entries externally, so we're peeking at the logs directly.
        self.assertLessEqual(len(store._logs), 1_001)  # type: ignore

    async def test_overflow_logs(self):
        """Test that the log length is contrained"""

        store = self._get_log_store()

        id = str(uuid.uuid4())

        start = 0
        end = 2_000

        for x in range(start, end + 1):
            await store.set_logs(agent_id="", task_id=id, logs=f"{x}\n")

        result = await store.get_logs(id)

        self.assertFalse(str(result["logs"]).startswith(f"{start}\n"))  # truncated from the start
        self.assertTrue(str(result["logs"]).endswith(f"{end}\n"))

    async def test_overflow_oldest_removed(self):
        """Test that when the job list overflows, that the oldest jobs are discarded first"""

        store = self._get_log_store()
        logs = "".join(LOGS)
        first_id = str(uuid.uuid4())
        await store.set_logs(agent_id="", task_id=first_id, logs=logs)

        start = 0
        end = 1_100

        for _x in range(start, end + 1):
            await store.set_logs(agent_id="", task_id=str(uuid.uuid4()), logs=logs)

        with self.assertRaisesRegex(KeyError, "No logs found"):
            await store.get_logs(task_id=first_id)
