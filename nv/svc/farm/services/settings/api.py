# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Endpoints for the Farm Queue Settings Management service."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from nv.svc.core import routers
from nv.svc.farm.services.settings.facility import ServiceSettingsFacility
from nv.svc.farm.services.settings.utils import get_exposed_settings_key


class GetSettingsResponseModel(BaseModel):
    """Response to the request to retrieve settings from the Farm Queue."""

    settings: Optional[Any] = Field(
        None,
        title="Settings to expose via the Farm Queue.",
        description="Settings provided to the Omniverse Farm Queue, and to be exposed to external services.",
    )


router = routers.ServiceAPIRouter()


@router.get(
    "/settings",
    summary="Expose Farm Queue settings",
    description="Expose settings configured on the Farm Queue for tasks to query.",
    response_model=GetSettingsResponseModel,
)
async def get_settings(
    settings_facility: ServiceSettingsFacility = router.get_facility("settings"),
) -> GetSettingsResponseModel:
    """Retreive exposed settings.

    Args:
        settings_facility (ServiceSettingsFacility, optional): [description]. Defaults to router.get_facility("settings").

    Returns:
        GetSettingsResponseModel: [description]
    """
    settings_key = get_exposed_settings_key(package_name="nv.svc.farm", service_name="settings")
    settings = await settings_facility.get_setting(settings_key)

    return GetSettingsResponseModel(settings=settings)
