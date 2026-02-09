# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Utilities shared by store implementations."""

from typing import Dict


def get_node_data_dict(node_name: str) -> Dict[str, str]:
    """Return the default node structure used across stores."""
    return {
        "node_name": node_name,
        "actions": [],
        "words": [],
    }
