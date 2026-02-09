# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OS Capacity."""

import platform

from .base import StringCapacity


class OS(StringCapacity):
    """OS String Capacity."""

    def __init__(self, strict: bool = False) -> None:

        # TODO: use hostnamectl to parse the distribution and version.
        identifier = f"os.{platform.system().lower()}"
        super().__init__(identifier, strict=strict)
