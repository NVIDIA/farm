# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Read-only store settings interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseReadOnlySettingStore(ABC):
    """Read-only store settings interface."""

    @abstractmethod
    async def get_setting(self, path: str) -> Any:
        """
        Return the setting at the given path.

        Args:
            path (str): Path of the setting to return.

        Returns:
            Any: The setting at the given path.

        """
        pass
