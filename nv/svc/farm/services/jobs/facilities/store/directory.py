# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Jobs Service Directory Store Facility."""

import asyncio
import glob
import logging
import os
from pathlib import Path
from typing import Awaitable, Dict, List, Optional, Tuple

import toml

from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from .base import BaseJobStore
from nv.svc.farm.services.jobs.definitions import JobDefinition
from nv.svc.farm import utils


DEFAULT_JOB_DEFINITION_SAVE_DIRECTORY = str(Path(utils.FARM_USER_DATA_DIR) / "job-definitions")


class JobFileChangedHandler(PatternMatchingEventHandler):
    """Watch directories for changes to job files."""

    def __init__(self, on_create_callback: Awaitable, on_modified_callback: Awaitable, on_deleted_callback: Awaitable, loop):
        """Job file changed handler constructor."""
        super().__init__(patterns=["*.kit"], ignore_directories=True, case_sensitive=False)

        self._loop = loop
        self._on_create_callback = on_create_callback
        self._on_modified_callback = on_modified_callback
        self._on_deleted_callback = on_deleted_callback

    def on_created(self, event: FileCreatedEvent):
        """Handle FileCreatedEvents."""
        asyncio.run_coroutine_threadsafe(self._on_create_callback(event.src_path), loop=self._loop)
        return super().on_created(event)

    def on_modified(self, event: FileModifiedEvent):
        """Handle FileModifiedEvents."""
        asyncio.run_coroutine_threadsafe(self._on_modified_callback(event.src_path), loop=self._loop)
        return super().on_modified(event)

    def on_deleted(self, event: FileDeletedEvent):
        """Handle FileDeletedEvents."""
        asyncio.run_coroutine_threadsafe(self._on_deleted_callback(event.src_path), loop=self._loop)
        return super().on_deleted(event)


class DirectoryJobStore(BaseJobStore):
    """Manage job configuration."""

    def __init__(
            self,
            new_job_definition_save_location: str = None,
            job_directories: Tuple[str] = None,
            support_path_resolution=True,
            store_updated_callback: Optional[Awaitable] = None,
            **kwargs,
    ):
        """Directory Job store constructor."""
        if kwargs:
            logging.debug(f"Ignoring kwargs: {kwargs}")
        super().__init__(store_updated_callback)

        self._fetch_from_local_interval = 10
        if new_job_definition_save_location is None:
            new_job_definition_save_location = DEFAULT_JOB_DEFINITION_SAVE_DIRECTORY
            logging.debug(
                "No 'new_job_definition_save_location' specified for DirectoryJobStore. "
                f"Defaulting to '{DEFAULT_JOB_DEFINITION_SAVE_DIRECTORY}'"
            )

        self._support_path_resolution = support_path_resolution
        self._jobs = {}
        self._new_job_definition_save_location = self._resolve_new_job_definition_save_location(new_job_definition_save_location)

        self._job_dirs = job_directories or []
        if isinstance(self._job_dirs, List) and self._new_job_definition_save_location:
            self._job_dirs = self._job_dirs + [self._new_job_definition_save_location]
        elif isinstance(self._job_dirs, Tuple) and self._new_job_definition_save_location:
            self._job_dirs = self._job_dirs + (self._new_job_definition_save_location,)

        self._observer = None
        self._directory_watchers = {}
        self._job_defs_per_file = {}
        for jdir in self._job_dirs:
            logging.debug(f"Creating {jdir} if it does not exist.")
            try:
                Path(jdir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error(f"Unable to create directory {jdir} - error {e}")
                raise
            logging.info(f"Job definitions directory: '{jdir}'")

    async def start(self) -> None:
        """Stop the directory watchers and observer."""
        self._observer = Observer()
        self._observer.start()

        try:
            logging.debug("Starting fetch_from_local coroutine.")
            await self._fetch_from_local()
        except asyncio.CancelledError:
            return

    async def _fetch_from_local(self) -> None:
        await asyncio.sleep(self._fetch_from_local_interval)
        while True:
            try:
                await self._load_jobs()
            except Exception as exc:
                logging.error(f"Failed to load local job definitions: {str(type(exc))}, {str(exc)}")
            await asyncio.sleep(self._fetch_from_local_interval)

    async def stop(self) -> None:
        """Stop the directory watchers and observer."""
        self._directory_watchers = None
        self._observer.stop()

    def _resolve_new_job_definition_save_location(self, new_job_definition_save_location) -> str:
        """
        Resolve the location where new job definition files should be stored.

        Args:
            str: the new_job_definition_save_location

        Returns:
            str: The location where new job definition files should be stored.

        """
        if not new_job_definition_save_location:
            return ""

        return new_job_definition_save_location

    def _generate_job_spec_path(self, job_definition: JobDefinition) -> str:
        """
        Generate the job spec path where the given job definition should be persisted.

        Args:
            job_definition (JobDefinition): Metadata information about the job definition for which the spec file should
                be generated.

        Returns:
            str: The job spec path where the given job definition should be persisted.

        """
        new_job_definition_save_path = Path(self._new_job_definition_save_location)
        job_spec_path = new_job_definition_save_path / f"{job_definition.name}.kit"
        if job_spec_path.exists():
            logging.debug(f"{job_spec_path} exists, overwriting.")
            job_spec_path.unlink()
        if not new_job_definition_save_path.exists():
            new_job_definition_save_path.mkdir(parents=True, exist_ok=True)

        self._create_directory_watcher(directory=self._new_job_definition_save_location)
        job_spec_path.touch()
        return job_spec_path.absolute().as_posix()

    def save_job(self, job_definition: JobDefinition) -> None:
        """Save the job definition to disk."""

        job_spec_path = job_definition.job_spec_path
        if not job_spec_path:
            # If `job_spec_path` is not set in the given job definition payload, this means it is a definition of a new
            # job, as its origin does not come from an already-existing KIT file.
            #
            # In that case, a file should be created so the job definition can be persisted to it:
            job_spec_path = self._generate_job_spec_path(job_definition=job_definition)

        if os.path.exists(job_spec_path):
            config = toml.load(job_spec_path)
        else:
            config = {}
        jobs = config.get("job", {})

        if job_definition.unresolved_command_path:
            job_definition.command = job_definition.unresolved_command_path
        job_def_dict = job_definition.to_dict()

        job_def_dict.pop("unresolved_command_path")
        job_def_dict.pop("extension_paths")

        jobs.update({
            job_definition.name: job_def_dict
        })

        config["job"] = jobs

        # Validate the config is valid before writing it out to file.
        toml.dumps(config)

        with open(job_spec_path, "w") as output:
            toml.dump(config, output)

        asyncio.ensure_future(self._on_job_file_modified(job_spec_path))

    async def delete_job(self, job_definition_name: str) -> None:
        """Remove the job definition from disk."""

        def _delete_job_definition_file(job_definition_name, job_spec_path):
            """Delete a job definition file that contains only one job definition."""

            job_def_file = Path(job_spec_path)
            if job_def_file.exists() and job_def_file.is_file():
                try:
                    logging.debug(f"Deleting job definition file {job_spec_path} containing {job_definition_name}")
                    job_def_file.unlink()
                    asyncio.ensure_future(self._on_job_file_deleted(job_def_file))
                except Exception as exe:
                    logging.warning(f"Unable to delete job definition file '{job_spec_path}' containing {job_definition_name}: {type(exe).__name__} - {exe}")
                    return False

            return True

        def _remove_job_definition_from_file(job_definition_name, job_spec_path):
            """Remove a specific job definition from a file that contains several."""

            try:
                logging.debug(f"Removing {job_definition_name} from {job_spec_path}")
                job_def_file = Path(job_spec_path)
                if job_def_file.exists() and job_def_file.is_file():
                    with open(job_spec_path, 'r') as job_definition_file:
                        config = toml.load(job_definition_file)

                    if job_definition_name in config.get('job', {}):
                        config['job'].pop(job_definition_name)

                    with open(job_spec_path, 'w') as job_definition_file:
                        toml.dump(config, job_definition_file)
                    asyncio.ensure_future(self._on_job_file_modified(job_def_file))
            except Exception as exe:
                logging.warning(f"Unable to remove job definition '{job_definition_name}' in {job_spec_path}: {type(exe).__name__} - {exe}")
                return False

            return True

        results = []
        for job_spec_path, job_names in self._job_defs_per_file.items():
            if job_definition_name in job_names:
                if len(job_names) == 1:
                    if _delete_job_definition_file(job_definition_name, job_spec_path):
                        results.append(job_definition_name)
                else:
                    if _remove_job_definition_from_file(job_definition_name, job_spec_path):
                        results.append(job_definition_name)

        if results:
            logging.info(f"removed {len(results)} instance(s) of the job definition '{job_definition_name}'")
        else:
            logging.info(f"No instances of job definition '{job_definition_name}' found for removal")

    def update_settings(self, job_directories, support_path_resolution):
        """Update settings for path resolution."""
        self._support_path_resolution = support_path_resolution
        self._job_dirs = job_directories
        asyncio.ensure_future(self.load_jobs())

    async def _load_job_configurations(self, directory) -> List:
        jobs = {}
        files = []
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path) and os.path.splitext(full_path)[1] in (".kit",):
                files.append(full_path)

        for file in files:
            jobs.update(await self._load_configuration(file))

        self._jobs.update(jobs)
        return jobs

    def _create_directory_watcher(self, directory: str):
        """
        Create a file event watcher for a given directory.

        Args:
            directory (str): Directory to watch
        """
        if directory in self._directory_watchers:
            return

        logging.debug(f"Creating file watcher for {directory}")
        loop = asyncio.get_running_loop()
        handler = JobFileChangedHandler(self._on_job_file_created, self._on_job_file_modified, self._on_job_file_deleted, loop)
        watch = self._observer.schedule(handler, directory, recursive=True)
        self._directory_watchers[directory] = watch

    async def _on_job_file_created(self, path: str):
        jobs = await self._load_configuration(path)
        self._jobs.update(jobs)

    async def _on_job_file_modified(self, path: str):
        keys = self._job_defs_per_file.pop(path, [])
        for key in keys:
            self._jobs.pop(key, None)

        jobs = await self._load_configuration(path)
        self._jobs.update(jobs)

    async def _on_job_file_deleted(self, path: str):
        keys = self._job_defs_per_file.pop(path, [])
        for key in keys:
            self._jobs.pop(key, None)

    async def _load_jobs(self) -> bool:
        self._jobs = {}
        for directory in self._job_dirs:
            sub_dirs = glob.glob(directory)
            for sub_dir in sub_dirs:
                if os.path.isdir(sub_dir):
                    await self._load_job_configurations(sub_dir)
                    self._create_directory_watcher(sub_dir)

        return True

    async def _load_configuration(self, job_spec_path: str) -> Dict[str, JobDefinition]:
        config = self._safe_load_config(job_spec_path)

        jobs = config.get("job", {})
        if not jobs:
            logging.warning(f"No job configurations found in {job_spec_path}")

        job_spec_folder = os.path.dirname(job_spec_path)
        extension_paths = self._resolve_extension_paths(config, "settings.app.exts.folders.++", job_spec_folder)

        job_specs = {}
        for job_name, params in jobs.items():
            try:
                job_definition = await self._generate_job_definition(job_name, params, job_spec_path, extension_paths)
                if job_definition:
                    job_specs[job_name] = job_definition
            except Exception as exc:
                logging.warning(f"Failed to load job definition for '{job_name}'. Exception was: {type(exc)} - {str(exc)}")

        self._job_defs_per_file[job_spec_path] = job_specs.keys()

        return job_specs

    async def _generate_job_definition(self, job_name: str, params: Dict, job_spec_path: str, extension_paths: List) -> JobDefinition:
        return JobDefinition(
            job_name,
            params["job_type"],
            params["command"],
            job_spec_path,
            args=params.get("args", []),
            task_function=params.get("task_function", None),
            headless=params.get("headless", True),
            env=params.get("env", {}),
            log_to_stdout=params.get("log_to_stdout", True),
            allowed_args=params.get("allowed_args", {}),
            unresolved_command_path=params["command"],
            extension_paths=extension_paths,
            success_return_codes=params.get("success_return_codes", [0]),
            capacity_requirements=params.get("capacity_requirements", {}),
            working_directory=params.get("working_directory"),
            container=params.get("container")
        )

    def _resolve_extension_paths(self, config: Dict, key: str, job_spec_folder: str) -> List:
        extension_paths = []
        settings = config
        try:
            for key_chunk in key.split("."):
                settings = settings[key_chunk]
        except KeyError:
            return extension_paths

        for path in settings:
            path = path.format(job=job_spec_folder)
            if path.startswith("$"):
                path = path[1:]
            extension_paths.append(path)

        return extension_paths

    def _safe_load_config(self, file_path: str) -> Dict[str, any]:
        try:
            config = toml.load(file_path)
            return config
        except Exception as exe:
            logging.warning(f"Failed to load TOML configuration from {file_path}: {type(exe).__name__} - {exe}")
            return {}
