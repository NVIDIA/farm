# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework facilities."""


class Facility:
    """
    Base class for all stateful type objects (pooling, etc.) that can be injected into services at runtime.

    When registered with the `ServiceAPIRouter`, they can be retrieved from service function handlers through dependency
    injection.
    """

    def stop(self):
        """Stop the facility."""
        pass
