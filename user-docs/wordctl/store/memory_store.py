# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""In-memory store for nodes; useful for tests and ephemeral runs."""

from typing import Dict
import copy

from .utils import get_node_data_dict

_DB: Dict[str, Dict[str, str]] = {}


def save_node(node_name: str, value: Dict[str, str]) -> None:
    """Save a node's value into the in-memory DB."""
    _DB[node_name] = copy.deepcopy(value)


def load_node(node_name: str) -> Dict[str, str]:
    """Load a node's value as a deep copy; return default if missing."""
    data = _DB.get(node_name)
    if not data or not isinstance(data, dict):
        return get_node_data_dict(node_name)
    return copy.deepcopy(data)
