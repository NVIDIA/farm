# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""File-based store that persists nodes in a JSON file next to this module."""

from pathlib import Path
from typing import Dict
import json
import copy

from .utils import get_node_data_dict

JSON_PATH = Path(__file__).resolve().parent / "nodes.json"


def _load_all() -> Dict[str, Dict[str, str]]:
    """Load entire node DB from disk, tolerating missing/invalid file."""
    try:
        return json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _save_all(db: Dict[str, Dict[str, str]]) -> None:
    """Write the entire node DB to disk."""
    JSON_PATH.write_text(json.dumps(db, indent=4, ensure_ascii=False), encoding="utf-8")


def save_node(node_name: str, value: Dict[str, str]) -> None:
    """Persist a single node into the JSON store."""
    db = _load_all()
    db[node_name] = value
    _save_all(db)


def load_node(node_name: str) -> Dict[str, str]:
    """Load a node by name, returning a deep copy of stored data."""
    db = _load_all()
    data = db.get(node_name)
    if not data or not isinstance(data, dict):
        return get_node_data_dict(node_name)
    return copy.deepcopy(data)
