# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Job Types."""

from typing import List

from .base import BaseJob
from .kit import KitJob, KitServiceJob


_job_type_registry = {
    "base": BaseJob,
    "kit": KitJob,
    "kit-service": KitServiceJob
}


class JobTypeNotFoundError(Exception):
    """Raised when a job type is requested that does not exist."""


class DuplicateJobNameError(Exception):
    """Raised when a job_type has already been registered under this name."""


class InvalidBaseClassError(Exception):
    """Raised when the job_type is not of a BaseJob subclass."""


def get_job_type(name: str) -> BaseJob:
    """For a given job type name get the corresponding Job class.

    Args"
        name (str): Name of the job type

    Returns:
        BaseJob: A class inheriting from BaseJob that represents a valid job.
    """
    try:
        return _job_type_registry[name]
    except KeyError:
        raise JobTypeNotFoundError(f"{name} is not recognized as a valid job type. Make sure to check the spelling and that this job type is registered")


def get_job_types() -> List[str]:
    """Return the names of all registered job types."""
    return list(_job_type_registry.keys())


def register_job_type(name: str, job_type: BaseJob) -> None:
    """Register a new job type.

    Args:
        name (str): Name of the job type to register
        job_type (BaseJob): Class representing the job. Needs to be a subclass of BaseJob

    Raises:
       DuplicateJobNameError: Raised if a job_type has already been registered under this name
       InvalidBaseClassError: Raised if the job_type is not a subclass of BaseJob
    """
    if name in _job_type_registry:
        raise DuplicateJobNameError(f"{name} has already been registered as a job-type. Deregister the existing job type or rename this job type")

    if not issubclass(job_type, BaseJob):
        raise InvalidBaseClassError(f"{str(job_type)} is not a subclass of BaseJob")

    _job_type_registry[name] = job_type


def deregister_job_type(name: str) -> None:
    """Deregister a job type of a given name.

    Args:
        name (str): Name of the job type to deregister.
    """
    # Remove the job type but do not raise if it isn't registered.
    _job_type_registry.pop(name, None)
