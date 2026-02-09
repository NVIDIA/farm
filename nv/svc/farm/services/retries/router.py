# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Retries service router."""

from typing import Dict

from nv.svc.core import routers

router = routers.ServiceAPIRouter()


@router.post(
    "/submit",
    summary="Retries a Task.",
    description="Endpoint through which Tasks can be retried.",
)
async def post_retry(
    payload: Dict,
    retry_manager=router.get_facility("retry_manager"),
):
    """Retry endpoint.

    Args:
        payload: Dictionary containing old_task_state and new_task_state
        retry_manager: The retry manager facility
    """
    return await retry_manager.retry_task(payload["new_task_state"])


@router.get(
    "/status",
    summary="Healthcheck endpoint for retry service.",
    description="Returns 200 and OK if retry service is available.",
)
async def status():
    """Retries service status endpoint."""
    return "OK"
