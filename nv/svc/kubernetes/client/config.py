# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework config settings."""

from pathlib import Path

from nv.svc.core.utils.config import Config, setting

DEFAULT_DATA_PATH = str(Path(__file__).resolve().parent / "data")
PACKAGE_NAME = "nv.svc.kubernetes.client"


@setting(
    "load_in_cluster_config",
    cast=bool,
    default=True,
    description="Automatically load in-cluster configuration.",
)
@setting(
    "verify_ssl",
    cast=bool,
    default=True,
    description="Enables/Disables secure/insecure SSL verification when connected to Kube API",
)
@setting(
    "kube_config_path",
    cast=str,
    default="",
    description="Path to a Kube Config file, usually used when request is coming from outside of the cluster the Kube API is located in",
)
@setting(
    "kube_config_context",
    cast=str,
    default="ov-local",
    description="The Kube Context inside of the Kube Config that should be used",
)
def ServicesCoreConfig(*validators) -> Config:
    """Omni Services Core configuration settings."""
    return Config(package_name=PACKAGE_NAME, validators=list(validators), raise_on_package_not_found_error=False)
