# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Persistence layer that integrates with Omniverse Farm HTTP APIs."""

from __future__ import annotations

import os
import json
import urllib.request
from typing import Dict
from functools import cache

from .utils import get_node_data_dict


HEADERS_JSON = {"Content-Type": "application/json", "Accept": "application/json"}
OV_FARM_RESULTS_ENDPOINT = os.environ.get("OV_FARM_RESULTS_ENDPOINT")
OV_FARM_TASKS_ENDPOINT = os.environ.get("OV_FARM_TASKS_ENDPOINT")
OV_FARM_TASK_ID = os.environ.get("OV_FARM_TASK_ID")

if not OV_FARM_RESULTS_ENDPOINT or not OV_FARM_TASKS_ENDPOINT or not OV_FARM_TASK_ID:
    raise ValueError("OV_FARM_RESULTS_ENDPOINT, OV_FARM_TASKS_ENDPOINT, and OV_FARM_TASK_ID must be set")


def _get_dag_results_endpoint(dag_id: str) -> str | None:
    """Build the DAG results endpoint for the given ``dag_id``."""
    if not OV_FARM_RESULTS_ENDPOINT or not dag_id:
        return None
    return f"{OV_FARM_RESULTS_ENDPOINT.rstrip('/')}/dag/{dag_id}"


def _get_task_endpoint() -> str | None:
    """Build the task info endpoint for the configured task id."""
    if not OV_FARM_TASKS_ENDPOINT or not OV_FARM_TASK_ID:
        return None
    return f"{OV_FARM_TASKS_ENDPOINT.rstrip('/')}/info/{OV_FARM_TASK_ID}"


def _get_task_results_endpoint() -> str | None:
    """Build the task results endpoint for the configured task id."""
    if not OV_FARM_RESULTS_ENDPOINT or not OV_FARM_TASK_ID:
        return None
    return f"{OV_FARM_RESULTS_ENDPOINT.rstrip('/')}/task/{OV_FARM_TASK_ID}"


def _get_task_info() -> Dict[str, str]:
    """Fetch task metadata and extract identifiers used by the store."""
    task_url = _get_task_endpoint()

    with urllib.request.urlopen(urllib.request.Request(task_url, headers=HEADERS_JSON, method="GET"), timeout=10) as resp:
        task_data = resp.read().decode("utf-8")

    task_json = json.loads(task_data)

    return {
        "dag_id": task_json["metadata"].get("dag", {}).get("id", ""),
    }


def _get_dag_results(dag_id: str) -> Dict[str, Dict[str, str]]:
    """Fetch and parse DAG results for ``dag_id`` keyed by node name."""
    dag_results_url = _get_dag_results_endpoint(dag_id)

    with urllib.request.urlopen(urllib.request.Request(dag_results_url, headers=HEADERS_JSON, method="GET"), timeout=10) as resp:
        dag_data = resp.read().decode("utf-8")

    dag_json = json.loads(dag_data)
    parsed_results = [json.loads(node["data"]) for node in dag_json]
    final_results = {node["node_name"]: node for node in parsed_results}

    return final_results


@cache
def _get_state(dag_id: str) -> Dict[str, str]:
    """Cache DAG results state."""
    if not dag_id:
        return {}
    return _get_dag_results(dag_id)


@cache
def _get_task_state() -> Dict[str, str]:
    """Cache task metadata used by the store."""
    return _get_task_info()


def save_node(node_name: str, value: Dict[str, str]) -> None:
    """Persist a node's value for the current task."""
    url = _get_task_results_endpoint()

    payload = {"data": json.dumps(value)}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=HEADERS_JSON, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()


def load_node(node_name: str) -> Dict[str, str]:
    """Load a node by name, falling back to a default structure if missing."""
    task_info = _get_task_state()
    dag_data = _get_state(task_info.get("dag_id", ""))
    return dag_data.get(node_name, get_node_data_dict(node_name))
