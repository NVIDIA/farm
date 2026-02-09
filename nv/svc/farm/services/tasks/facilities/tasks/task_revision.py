# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Task revision history."""

import time as t
from typing import Dict, Optional, Union


class TaskRevision:
    """Task revision history."""

    def __init__(
        self,
        task_id: str,
        status: str,
        userid: Union[str, bytes],
        revision_id: Optional[int] = None,
        agent_id: Optional[Union[str, bytes]] = None,
        details: Optional[str] = None,
        progress: Optional[Dict] = None,
        time: Optional[float] = None,
    ) -> None:
        """
        Task revision history.

        Args:
            task_id (str): Unique identifier of the task to which this revision is a snapshot of.
            status (str): Status of the task at the moment the revision is stored.
            userid (str): Unique identifier of the User who made the last change to the task.
            revision_id (Optional[str]): Unique identifier of the task revision, if read from the
              backend datastore. Not required when creating new revisions as this is generated on insert.
            agent_id (Optional[str]): Unique identifier of the Agent that processed the task, if any.
            details (Optional[str]): Details about the task.
            progress (Optional[Dict]): Progress information about the task.
            time (Optional[float]): Unix timestamp of the change.

        Returns:
            None

        """
        self._task_id = task_id
        self._status = status
        self._user_id = userid.decode("utf-8") if isinstance(userid, bytes) else userid
        self._revision_id = revision_id
        self._agent_id = agent_id.decode("utf-8") if isinstance(agent_id, bytes) else agent_id
        self._details = details
        self._progress = progress
        self._time = time or t.time()

    @property
    def revision_id(self) -> Optional[int]:
        """Unique identifier of the task revision."""
        return self._revision_id

    @property
    def task_id(self) -> str:
        """Unique identifier of the task to which this revision is a snapshot of."""
        return self._task_id

    @property
    def status(self) -> str:
        """Status of the task at the moment the revision is stored."""
        return self._status

    @property
    def user_id(self) -> str:
        """Unique identifier of the User who made the last change to the task."""
        return self._user_id

    @property
    def agent_id(self) -> Optional[str]:
        """Unique identifier of the Agent that processed the task, if any."""
        return self._agent_id

    @property
    def details(self) -> Optional[str]:
        """Details about the task."""
        return self._details

    @property
    def progress(self) -> Optional[Dict]:
        """Progress information about the task."""
        return self._progress

    @property
    def time(self) -> float:
        """Unix timestamp of the change."""
        return self._time
