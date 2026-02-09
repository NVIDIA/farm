# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Results Service Managers."""

from .base import BaseResultManager
from .memory import DictResultManager
from .redis import RedisResultManager

__all__ = ["BaseResultManager", "DictResultManager", "RedisResultManager"]
