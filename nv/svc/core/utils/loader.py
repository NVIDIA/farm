# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Resolve a class by import path."""
import importlib
from typing import Type


def load_cls_from_string(import_path: str) -> Type:
    """Resolve a class from an import path .

    Args:
        import_path (str): The class import path to load

    Returns:
        Type: Loaded Python Class
    """
    cls_name = import_path.split(".")[-1]
    import_path = import_path.replace(f".{cls_name}", "")
    module = importlib.import_module(import_path)
    return getattr(module, cls_name)
