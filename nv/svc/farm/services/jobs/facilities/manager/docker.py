# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Job Manager Docker."""

__all__ = ["ProcessManager"]


import asyncio
import subprocess
import logging

from typing import Any, Callable, Dict, List, Optional

import aiodocker


from nv.svc.farm.services.jobs.facilities.manager.base import ProcessManager as BaseProcessManager
from nv.svc.farm.services.jobs.facilities.store.base import BaseJobStore
from nv.svc.farm.services.jobs.facilities.manager.base import BaseInstance


class DockerInstance(BaseInstance):

    def __init__(
        self,
        command: str,
        container: str,
        args: List[str],
        env: Dict[str, Any] = None,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        subprocess_kwargs=None,
        on_stdout_message: Callable[[str], None] = None,
        on_stderr_message: Callable[[str], None] = None,
        success_return_codes: List[str] = None,
        working_directory: str = None,
        task_id: str = None,
    ):
        super().__init__(
            command=command,
            container=container,
            args=args,
            env=env,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            subprocess_kwargs=None,
            on_stdout_message=on_stdout_message,
            on_stderr_message=on_stderr_message,
            success_return_codes=success_return_codes,
            working_directory=working_directory,
            task_id=task_id
        )
        self._docker = aiodocker.Docker()
        self._return_code = None

    @property
    def returncode(self):
        return self._return_code

    def spawn(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        raise NotImplementedError("Docker tasks cannot be spawned in a threaded mode")

    async def spawn_async(self, requirements: Optional[Dict] = None, metadata: Optional[Dict] = None):
        self._stop = asyncio.Event()

        requirements = requirements or {}
        metadata = metadata or {}

        requirements.update(metadata.get("requirements", {}))
        env_list = [f"{key}={value}" for key, value in self._env.items()]

        config = {
            "Cmd": self._command,
            "Env": env_list,
            "Image": self._container_image,
        }

        config.update(requirements)

        self._process = await self._docker.containers.create_or_replace(
            name=self._task_id,
            config=config
        )

        await self._process.start()
        self._active_thread = asyncio.ensure_future(self._communicate_async())
        return self._process

    async def _read_stream(self, stream, callback: Callable[[str], None]) -> None:
        """
        Read content from the given stream an capture the output.

        Args:
            stream (StreamReader): Reader from which to collect the output.
            callback (Callable[[str], None]): Callback function to execute upon reading a line from the stream.

        Returns:
            None

        """
        async for line in stream:
            if line:
                callback(
                    line.decode("utf-8") if isinstance(line, bytes) else line
                )

    async def _install_log_listeners(self) -> None:
        """Install the log listeners on the output streams of the process."""
        listeners: List[Callable[[str], None]] = []
        if self._on_stdout_message:
            listeners.append(
                asyncio.create_task(self._read_stream(self._process.log(stdout=True, stderr=False, follow=True), self._on_stdout_message))
            )
        if self._on_stderr_message:
            listeners.append(
                asyncio.create_task(self._read_stream(self._process.log(stdout=False, stderr=True, follow=True), self._on_stdout_message))
            )

        if listeners:
            await asyncio.wait(listeners)

    async def _communicate_async(self) -> None:
        log_handlers = None
        try:
            log_handlers = asyncio.ensure_future(self._install_log_listeners())
            data = await self._process.wait()
            self._return_code = data["StatusCode"]
            error = data["Error"]

            # stats = await self._process.stats(stream=False)
            # show = await self._process.show()

            log_string = f"Process exited with return code: {self.returncode}"

            if self.returncode not in self.success_return_codes:
                error_string = f"{log_string}. Error: {error}"
                logging.error(error_string)
            else:
                logging.info(log_string)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logging.error(f"Failed to communicate with process: {str(type(exc))}, {str(exc)}")
        finally:
            if log_handlers:
                log_handlers.cancel()

    async def stop_async(self):
        self.shutdown()
        await self._process.stop()
        self._return_code = -1
        return self.returncode

    async def kill_async(self):
        self.shutdown()
        await self._process.kill()
        self._return_code = -1
        return self.returncode

    def stop(self):
        asyncio.ensure_future(self.stop_async())
        return -1

    def kill(self):
        return self.stop()

    @property
    def process_id(self) -> Optional[str]:
        """
        Unique identifier of the process being executed, if it has been spawned.

        Args:
            None

        Returns:
            Optional[str]: The unique identifier of the process that was spawned, or ``None`` otherwise.

        """
        if not self._process:
            return None
        return str(self._process.id)

    @property
    def status(self) -> Optional[str]:
        if not self._process:
            return None

        return "running" if not self.returncode else "finished"

    def _resolve_is_active(self) -> bool:
        """Resolve if a instance is active."""
        # TODO
        return self.returncode is None


class ProcessManager(BaseProcessManager):
    """Start, monitor and manage processes."""

    _instance_type_cls = DockerInstance

    def __init__(
        self,
        job_store: BaseJobStore,
        log_upload_interval: int = 10,
        log_upload_endpoint: str = "http://127.0.0.1:8011/queue/management/logs/upload",
    ):
        super().__init__(job_store, log_upload_interval, log_upload_endpoint)

    async def stop_process_async(self, process_type, process_id, kill=False) -> int:
        """Stop a process asynchroniously."""
        return self.stop_process(process_type, process_id, kill=kill)
