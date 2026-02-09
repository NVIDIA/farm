# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Utility methods."""

from functools import lru_cache


@lru_cache()
def get_exposed_settings_key(package_name: str = None, service_name: str = None) -> str:
    """
    Return the root key of the settings structure to be exposed by the service.

    Args:
        package_name: The name of the package to find exposed settings for

    Returns:
        str: The root key of the settings structure to be exposed by the service.

    """
    settings_key_prefix = f"settings.{package_name}"
    if service_name:
        settings_key = f"{settings_key_prefix}.{service_name}.exposed_settings"
    else:
        settings_key = f"{settings_key_prefix}.exposed_settings"
    return settings_key
