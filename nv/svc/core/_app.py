# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI

from ._route import CompressedRoute


class OmniverseService(FastAPI):
    """An Omniverse Service."""

    def __init__(self, *args, **kwargs):
        """Initialize Omniverse Service instance."""
        super().__init__(*args, **kwargs)
        self.router.route_class = CompressedRoute

        # Monkey-patch the FastAPI application in order to address potential discrepancies in the version of
        # `starlette`, where `self._debug` was renamed to `self.debug` in some version:
        self.debug = False


__all__ = ["OmniverseService"]
