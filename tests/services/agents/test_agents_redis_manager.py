# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import platform
import socket

from unittest import skipUnless, IsolatedAsyncioTestCase
from unittest.mock import patch

from nv.svc.farm.services.agents.facilities.managers.redis import RedisAgentManager


class TestRedisAgentManager(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self._bind_address = "/tmp/tmp_redis.sock"
        self._sock = socket.socket(socket.AF_UNIX)

    def tearDown(self) -> None:
        self._sock.detach()
        self._sock.close()

    def _get_manager(self, check_interval: int = 0, lost_timeout: int = 0) -> RedisAgentManager:
        return RedisAgentManager(
            check_interval,
            lost_timeout,
            "http://127.0.0.1:1234/queue/management/tasks",
            connection_string=f"unix://{self._bind_address}"
        )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_update_agent(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return None

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.update(
                        agent_id="foo",
                        active_tasks=["task_1"],
                        task_types=["foo-bar"],
                        resources={},
                        labels=[]
                    )

                mock_set.assert_called_once_with(
                    'agent_foo',
                    '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "active", "resources": {}, "errored_task_count": 0, "labels": []}',
                    ex=None,
                    nx=False,
                    xx=False
                )

                mock_get.assert_called_once_with('agent_foo')

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_get_agent_key(self):
        manager = self._get_manager()
        self.assertEqual(manager._get_agent_key("foo"), "agent_foo")

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_remove(self):
        manager = self._get_manager()

        async def mock_delete(*args, **kwargs):
            pass

        with patch("redis.asyncio.Redis.delete", wraps=mock_delete) as mock_delete:
            await manager.remove(
                agent_id="foo"
            )

            mock_delete.assert_called_once_with('agent_foo')

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_list(self):
        manager = self._get_manager()

        async def mock_scan_iter(*args, **kwargs):
            for key in ["agent_foo"]:
                yield key

        async def mock_get(*args, **kwargs):
            return '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "active", "resources": {}, "errored_task_count": 0}'

        with patch.object(manager._redis, "scan_iter", mock_scan_iter):
            with patch.object(manager._redis, "get", mock_get) as mock_get:
                res = await manager.list()

                self.assertEqual(
                    res,
                    {
                        "foo": {
                            "active_tasks": ["task_1"],
                            "task_types": ["foo-bar"],
                            "checkin_time": 123,
                            "status": "active",
                            "resources": {},
                            "errored_task_count": 0
                        }
                    }
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_list_byte_strings(self):
        manager = self._get_manager()

        async def mock_scan_iter(*args, **kwargs):
            for key in [b"agent_foo"]:
                yield key

        async def mock_get(*args, **kwargs):
            return '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "active", "resources": {}, "errored_task_count": 0, "labels": []}'

        with patch.object(manager._redis, "scan_iter", mock_scan_iter):
            with patch.object(manager._redis, "get", mock_get) as mock_get:
                res = await manager.list()

                self.assertEqual(
                    res,
                    {
                        "foo": {
                            "active_tasks": ["task_1"],
                            "task_types": ["foo-bar"],
                            "checkin_time": 123,
                            "status": "active",
                            "resources": {},
                            "errored_task_count": 0,
                            "labels": []
                        }
                    }
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_update_evicted_agent(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return json.dumps({"status": "evicted"})

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.update(
                        agent_id="foo",
                        active_tasks=["task_1"],
                        task_types=["foo-bar"],
                        resources={}
                    )

                mock_set.assert_called_once_with(
                    'agent_foo',
                    '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "evicted", "resources": {}, "errored_task_count": 0, "labels": []}',
                    ex=None,
                    nx=False,
                    xx=False
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_update_none_evicted_agent(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return json.dumps({"status": "idle"})

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.update(
                        agent_id="foo",
                        active_tasks=["task_1"],
                        task_types=["foo-bar"],
                        resources={},
                        labels=[]
                    )

                mock_set.assert_called_once_with(
                    'agent_foo',
                    '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "active", "resources": {}, "errored_task_count": 0, "labels": []}',
                    ex=None,
                    nx=False,
                    xx=False
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_update_evicted_agent_remains_evicted(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return json.dumps({"status": "evicted"})

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.update(
                        agent_id="foo",
                        active_tasks=[],
                        task_types=["foo-bar"],
                        resources={},
                        labels=[]
                    )

                mock_set.assert_called_once_with(
                    'agent_foo',
                    '{"active_tasks": [], "task_types": ["foo-bar"], "checkin_time": 123, "status": "evicted", "resources": {}, "errored_task_count": 0, "labels": []}',
                    ex=None,
                    nx=False,
                    xx=False
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_eviction(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return json.dumps(
                {
                    "active_tasks": ["task_1"],
                    "task_types": ["foo-bar"],
                    "checkin_time": 123,
                    "status": "active",
                    "resources": {},
                    "errored_task_count": 0,
                    "labels": []
                }
            )

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.evict("foo")

                mock_set.assert_called_once_with(
                    'agent_foo',
                    '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "evicted", "resources": {}, "errored_task_count": 0, "labels": []}',
                    ex=None,
                    nx=False,
                    xx=True
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_reenable(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return json.dumps(
                {
                    "active_tasks": ["task_1"],
                    "task_types": ["foo-bar"],
                    "checkin_time": 123,
                    "status": "evicted",
                    "resources": {},
                    "errored_task_count": 0,
                    "labels": []
                }
            )

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.enable("foo")

                mock_set.assert_called_once_with(
                    'agent_foo',
                    '{"active_tasks": ["task_1"], "task_types": ["foo-bar"], "checkin_time": 123, "status": "idle", "resources": {}, "errored_task_count": 0, "labels": []}',
                    ex=None,
                    nx=False,
                    xx=True
                )

    @skipUnless(
        platform.system().lower() == "linux",
        "A unix socket is needed for these tests. Windows does not support these."
    )
    async def test_reenable_only_affects_evicted(self):
        manager = self._get_manager()

        async def mock_set(*args, **kwargs):
            pass

        def mock_time():
            return 123

        async def mock_get(*args, **kwargs):
            return json.dumps(
                {
                    "active_tasks": ["task_1"],
                    "task_types": ["foo-bar"],
                    "checkin_time": 123,
                    "status": "active",
                    "resources": {},
                    "errored_task_count": 0,
                    "labels": []
                }
            )

        with patch("redis.asyncio.Redis.set", wraps=mock_set) as mock_set:
            with patch("redis.asyncio.Redis.get", wraps=mock_get) as mock_get:
                with patch("time.time", wraps=mock_time):
                    await manager.enable("foo")

                mock_set.assert_not_called()
