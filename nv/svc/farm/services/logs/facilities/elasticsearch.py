# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Logs Service Elasticsearch Log Store Facility."""

import logging

from datetime import datetime, timezone
from typing import Dict, List, Set

from elasticsearch import AsyncElasticsearch

from .base import BaseLogStore

SEARCH_SIZE_LIMIT = 10000


class ElasticsearchLogStore(BaseLogStore):
    """Elasticsearch log store."""

    def __init__(self, hosts: List[str] = None, index: str = None, auth: Dict = None, **kwargs) -> None:
        """Elasticsearch log store constructor."""
        super().__init__()
        if not hosts:
            raise Exception(f"No hosts given for Elasticsearch Log store, hosts={hosts}")

        if not auth:
            raise Exception(f"No auth details given for Elasticsearch Log store, auth={auth}")

        # Check Authentication method, API Key will take precedence
        if api_key := auth.get("api_key"):
            logging.info("Using Elasticsearch API Key authentication.")
            kwargs["api_key"] = api_key
        elif (username := auth.get("username")) and (password := auth.get("password")):
            logging.info("Using Elasticsearch Basic authentication.")
            kwargs["basic_auth"] = (username, password)
        else:
            raise KeyError("Invalid Elasticsearch authentication details. Expected 'api_key' or 'username'/'password'.")

        self._client = AsyncElasticsearch(hosts=hosts, **kwargs)
        self._index = index

    async def get_logs(self, task_id: str, agent_id: str = None, latest_only: bool = True, log_entries: int = 50) -> Dict:
        """
        Return the logs for the given task running on the given agent.

        Args:
            task_id (str): Unique identifier of the task for which to return the logs.
            agent_id (str): Unique identifier of the agent running the task for which to return the logs.

        Kwargs
            latest_only (bool): If task has ran on multiple agents than only return the most recent one. Default: True
            log_entries (int): Amount of log entries to return. Default: 50

        Returns:
            Dict: Metadata information about the logs for the given task.

        """
        if log_entries == 0:
            # NOTE: 0 means no limit per logs api, but Elasticsearch has a limit.
            # If there are more than 10000 search results we will need to paginate results (not currently done).
            log_entries = SEARCH_SIZE_LIMIT

        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term":
                            {
                                "labels.task_id": task_id
                            }
                        }
                    ],
                }
            },
            "sort": [
                {
                    "@timestamp":
                    {
                        "order": "asc"
                    }
                }
            ]
        }

        if agent_id:
            search_query["query"]["bool"]["must"].append(
                {
                    "term": {"host.name": agent_id}
                }
            )

        collected_logs = []
        try:
            res = await self._client.search(index=self._index, body=search_query, size=log_entries)
            collected_logs = res["hits"].get("hits", [])
        except Exception as exc:
            logging.error(f"Failed to search logs: {str(type(exc))}: {str(exc)}")

        if not collected_logs:
            raise KeyError(f"No logs found for {task_id}")

        created_at = self._convert_datetime_to_timestamp(collected_logs[0]["_source"]["@timestamp"])
        updated_at = self._convert_datetime_to_timestamp(collected_logs[-1]["_source"]["@timestamp"])
        # TODO: replace this once bulk insert is added.
        logs = "\n".join(self._mangle_logs(collected_logs))

        return {
            "created_at": created_at,
            "updated_at": updated_at,
            "logs": logs
        }

    def _mangle_logs(self, collected_logs: List[str]) -> Set:
        final_logs = []
        for log in collected_logs:
            final_logs.extend(filter(None, log["_source"]["message"].split("\n")))

        return final_logs

    def _convert_datetime_to_timestamp(self, datetime_str: str) -> float:
        date = datetime.fromisoformat(datetime_str)
        return date.timestamp()

    async def set_logs(self, agent_id: str, task_id: str, logs: str) -> None:
        """
        Record logs for the given task running on the given agent.

        Args:
            agent_id (str): Unique identifier of the agent running the task for which logs should be persisted.
            task_id (str): Unique identifier of the task for which logs should be persisted.
            logs (str): Logs to persist about the given task.

        Returns:
            None

        """
        # TODO: should each line be submitted individually?
        await self._index_log_line(logs, agent_id, task_id, datetime.now(timezone.utc))

    async def _index_log_line(self, log_line: str, agent_id: str, task_id: str, timestamp: int) -> None:
        """
        Insert log line into Elasticsearch.

        Args
            log_line (str): The log data.
            agent_id (str): Agent that sent the logs.
            task_id (str): Task id this log belongs to.
            timestamp (str): Time at which the log lines are inserted.

        """
        log_doc = {
            "host.name": agent_id,
            "labels": {"task_id": task_id},
            "@timestamp": timestamp,
            "message": log_line,
        }

        try:
            # await self._client.index(index=self._index, document=log_doc)
            # TODO: Bulk insert of individual lines.
            await self._client.index(index=self._index, body=log_doc)
        except Exception as exc:
            logging.error(f"Failed to update logs for {task_id} on {agent_id}: {str(type(exc))}, {str(exc)}")

    async def close(self):
        """Close the client."""
        await self._client.close()
