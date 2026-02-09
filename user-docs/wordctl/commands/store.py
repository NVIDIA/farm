# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Store command: write raw text into a named node."""

import argparse

from store import save_node, load_node
from .error_injection import add_error_args, maybe_raise_forced_error


def add_parser(subparsers) -> None:
    """Register the 'store' subcommand."""
    sp = subparsers.add_parser("store", help="Store text into a node (default ROOT_NODE)")
    sp.add_argument("text", help="Text to store")
    sp.add_argument("--output-node", dest="output_node", default="ROOT_NODE", help="Node name to store into")
    add_error_args(sp)
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Execute the store command using the provided CLI ``args``."""
    maybe_raise_forced_error("Store", args)
    data = load_node(args.output_node)
    data["words"] = args.text.split(" ")
    save_node(args.output_node, data)
