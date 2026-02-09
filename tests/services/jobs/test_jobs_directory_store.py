# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import tempfile
import unittest

from typing import Dict
from contextlib import asynccontextmanager

from nv.svc.farm.services.jobs.facilities.store.directory import DirectoryJobStore


_sample_toml = """
[package]
authors = ["NVIDIA"]
category = "farm-jobs"
description="Agent render job."
readme  = "Agent Render Job"
repository = ""
title = "Agent Render Job"
version = "0.1.0"


keywords = ["job"]

[settings.app.exts.folders]
'++' = ["${{job}}/exts-folder"]

[dependencies]
"services.render" = {{}}
"services.farm.agent.runner" = {{}}


[job.{name}]
job_type = "kit-task"
name = "create-render"
command = "{command}"
args = [
    "--enable", "services.render",
    "--enable", "services.farm.agent.runner",
    "--ext-folder", "/data/git/farm/services.farm.agent.runner/_build/linux-x86_64/release/exts",
    # Example code to set up pushing metrics to a Prometheus push gateway.
    #"--/exts/services.monitoring.metrics/push_metrics=true",
    #"--/exts/services.monitoring.metrics/job_name=create_render",
    #"--/exts/services.monitoring.metrics/push_gateway=http://localhost:9091"
]
task_function = "render.run"
no_window = false
env = {{}}
log_to_stdout = true

########################################################################################################################
# BEGIN GENERATED PART (Remove from 'BEGIN' to 'END' to regenerate)
########################################################################################################################

# Version lock for all dependencies:
[settings.app.exts]
enabled = [
    "foo.bar.baz-0.1.0"
]

########################################################################################################################
# END GENERATED PART
########################################################################################################################%

"""

@asynccontextmanager
async def async_temporary_directory():
    temp_dir = tempfile.TemporaryDirectory()
    try:
        yield temp_dir.name
    finally:
        temp_dir.cleanup()


class TestDirectoryJobStore(unittest.IsolatedAsyncioTestCase):
    async def test_job_directory_loading(self):
        job_store = await self._load_job_definitions({"job.test.config.kit": self._template_sample_toml()})
        job_definition = list(job_store.job_specs.values())[0]
        self.assertEqual(job_definition.name, "create-render")

    async def test_job_directory_loading_invalid_command(self):
        job_store = await self._load_job_definitions({ "job.test.config.command.error.kit": self._template_sample_toml(command="C:\\path\\to\\windows-x86_64\\release.usd_composer.kit.bat", name="create-render-error")})
        job_definitions = list(job_store.job_specs.values())
        self.assertEqual(job_definitions, [])

    async def test_job_directory_loading_safe_load(self):
        job_store = await self._load_job_definitions({
                "job.test.config.kit": self._template_sample_toml(),
                "job.test.config.command.error.kit": self._template_sample_toml(command="C:\\path\\to\\windows-x86_64\\release.usd_composer.kit.bat", name="create-render-error")
            })

        job_definitions = list(job_store.job_specs.values())
        self.assertEqual(len(job_definitions), 1)
        self.assertEqual(job_definitions[0].name, "create-render")

    async def test_job_directory_loading_multiple_jobs(self):
        job_store = await self._load_job_definitions({
                "job.test.config.kit": self._template_sample_toml(),
                "another.job.test.config.kit": self._template_sample_toml(name="another-create-render")
            })

        job_definitions = list(job_store.job_specs.values())
        job_definition_names = sorted([job.name for job in job_definitions])
        self.assertEqual(len(job_definition_names), 2)
        exp_job_definition_names = sorted(["create-render", "another-create-render"])
        self.assertEqual(job_definition_names, exp_job_definition_names)

    async def _load_job_definitions(self, files: Dict[str, str]):
        """
        Helper function to create multiple TOML files in the specified jobs directory.
        """

        async with async_temporary_directory() as temp_dir:
            for filename, content in files.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, mode="w") as file:
                    file.write(content)

            job_store = DirectoryJobStore(new_job_definition_save_location=temp_dir)
            # fake job_store.start without using the fetch_from_local coroutine.
            from watchdog.observers import Observer
            job_store._observer = Observer()
            job_store._observer.start()
            await job_store._load_jobs()

            return job_store

    def _template_sample_toml(self, command="launcher:///create", name="create-render") -> str:
        """
        Creates a TOML string based on the provided parameters.
        """
        return _sample_toml.format(command=command, name=name)
