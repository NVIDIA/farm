# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Dashboard Service Settings."""

from nv.svc.core.utils.config import Config, setting


@setting(
    "dashboard.host",
    default="",
    description="Optional host setting for redirection behind a reverse proxy.",
)
@setting(
    "dashboard.url_prefix",
    default="/queue/management/dashboard/",
    cast=lambda v: f"/{v}" if v and not v.startswith("/") else v,
    description="Prefix URL for the application.",
)
@setting(
    "dashboard.starfleet_enabled",
    cast=bool,
    default=False,
    description="Flag for enabling starfleet authentication.",
)
@setting(
    "dashboard.starfleet_client_id",
    default="",
    cast=str,
    description="Client id for interacting with starfleet authentication.",
)
@setting(
    "dashboard.starfleet_login_url",
    default="https://stg.login.nvidia.com",
    cast=str,
    description="Login url for starfleet authentication.",
)
@setting(
    "dashboard.build_dir",
    default="",
    cast=str,
    description="Build directory for serving dashboard `index.html`.",
)
def FarmDashboardConfig(*validators, auto_configure_logging=True) -> Config:
    """nv.svc.farm.dashboard configuration settings."""
    return Config(
        package_name="nv.svc.farm", validators=list(validators), auto_configure_logging=auto_configure_logging
    )
