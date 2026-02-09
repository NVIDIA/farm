# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest

from nv.svc.farm.services.jobs.facilities.manager.docker import DockerInstance

LOGS = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Integer tincidunt lacus nec arcu malesuada, sed congue diam dignissim.",
    "In ac est at risus consectetur commodo et sit amet mauris.",
    "In eget erat a ante rutrum viverra vel quis turpis.",
]


class TestDockerInstance(unittest.IsolatedAsyncioTestCase):
    def _create_mock_docker_instance(self, command="echo hello", container="my-docker:1.0.0", args=["echo", "hello"]):
        return DockerInstance(
            command=command,
            container=container,
            args=args
        )
