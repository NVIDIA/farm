# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os

backend = os.environ.get("WORDCTL_STORE")

if backend == "memory":
    from .memory_store import load_node, save_node, get_node_data_dict  # noqa: F401
elif backend == "json":
    from .json_store import load_node, save_node, get_node_data_dict  # noqa: F401
else:
    from .farm_apis import load_node, save_node, get_node_data_dict  # noqa: F401
