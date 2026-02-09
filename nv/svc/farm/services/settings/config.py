# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Settings Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "settings.url_prefix",
    default="/queue",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "settings.exposed_settings",
    cast=dict,
    default={},
    description="Prefix URL for the application.",
)
def FarmSettingsConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.settings configuration settings."""
    return Config(package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging)
