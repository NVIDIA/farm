# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework exceptions."""

from fastapi import HTTPException as _HTTPException


class ServicesBaseException(_HTTPException):
    """Base exception for services."""


class ServiceUnavailableError(Exception):
    """Error raised if a service is unavailable (503)."""
