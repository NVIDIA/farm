# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service router."""

import logging
import re

from fastapi.responses import JSONResponse
import pydantic

from nv.svc.core import routers

from nv.svc.farm.services.jobs.config import FarmJobsConfig
from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore
from nv.svc.farm.utils import ApiKeyHeader


router = routers.ServiceAPIRouter()
_CONFIG = FarmJobsConfig(auto_configure_logging=False)


async def _validate_from_settings(api_key: str):
    if not api_key:
        raise Exception("No valid API key was set for this service")

    stored_api_key = _CONFIG.jobs.api_key
    if api_key != stored_api_key:
        raise Exception("401: Unauthorized")


def _name_validator(cls, v):
    # The job name ends up as an URL, FastAPI doesn't like _ in URLs.
    if "_" in v:
        raise ValueError("Job name cannot contain underscore.")
    # jobs are referenced via task.task_type which is limited to 32 chars
    if len(v) > 32:
        raise ValueError("Job name cannot exceed 32 characters.")
    return v


name_validator = pydantic.validator("name")(_name_validator)


def _sanitize_filter(user_input):
    # Allow only alphanumeric characters, dots, and asterisks (.* type of patterns)
    safe_input = re.sub(r'[^a-zA-Z0-9.*]', '', user_input)
    return safe_input


def _create_dynamic_model(name: str, kwargs: dict) -> pydantic.BaseModel:
    model_args = {}
    # NOTE: a None, type(None) or Literal(None) only allows None values https://docs.pydantic.dev/usage/types/#standard-library-types
    # default to str type instead.
    for key, value in kwargs.items():
        model_args[key] = (type(value), value) if value is not None else (str, value)

    model = pydantic.create_model(
        name,
        __validators__={"name_validator": name_validator},
        **model_args)
    return model


JobDefinitionModel = _create_dynamic_model(
    "JobDefinitionModel",
    JobDefinition(
        "job-name",
        "base,kit,kit-service",
        "command",
        working_directory=None,
        unresolved_command_path=None,
        job_spec_path=None
    ).to_dict()
)


class JobDefinitionRemoveModel(pydantic.BaseModel):
    """Job definition remove model."""

    job_definition_name: str = pydantic.Field(..., title="Job definition identifier", description="Identifier of the job definition to remove.")


@router.get(
    "/load",
    summary="Load and retrieve the job definitions",
    description="Load and retrieve the job definitions"
)
async def load_job_Definitions(
    filter: str = ".*",
    job_store: BaseJobStore = router.get_facility("job_store"),
):
    """Load all available job definitions."""
    await job_store.load_jobs()
    job_definitions = job_store.job_specs
    sanitized_filter = _sanitize_filter(filter)
    results = {}
    for job_name, job_definition in job_definitions.items():
        if re.search(sanitized_filter, job_name):
            results[job_name] = job_definition.to_dict()
        else:
            logging.info(f"{job_name} does not match {filter}, excluding from list")

    return results


@router.post(
    "/save",
    summary="Store and save a job definition",
    description="Endpoint through which job definitions can be stored",
    dependencies=[ApiKeyHeader(check_functions=[_validate_from_settings])]
)
async def save_job_definition(
    job_definition: JobDefinitionModel,
    job_store: BaseJobStore = router.get_facility("job_store"),
):
    """Save endpoint for storing job definitions."""
    loaded_definition = JobDefinition(**dict(job_definition))
    job_store.save_job(loaded_definition)
    return JSONResponse({
        "job-name": loaded_definition.name,
        "success": True
    })


@router.post(
    "/remove",
    summary="Remove a job definition",
    description="Endpoint through which job definitions can be removed",
    dependencies=[ApiKeyHeader(check_functions=[_validate_from_settings])]
)
async def remove_job_definition(
    job_definition_data: JobDefinitionRemoveModel,
    job_store: BaseJobStore = router.get_facility("job_store"),
):
    """Remove endpoint for deleting job defintions."""
    job_definition_name = job_definition_data.job_definition_name
    await job_store.delete_job(job_definition_name)
    return JSONResponse({
        "job-name": job_definition_name,
        "success": True
    })


@router.get(
    "/status",
    summary="Healthcheck endpoint for jobs service.",
    description="Returns 200 and OK if jobs service is available.",
)
async def status():
    """Service status endpoint."""
    return "OK"
