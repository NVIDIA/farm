# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Haikuize command: reshape words into a 5/7/5-style structure."""

import argparse
from typing import Dict, List
from itertools import cycle, islice

from store import load_node, save_node
from .error_injection import add_error_args, maybe_raise_forced_error


def _haikuize(words: List[str]) -> List[str]:
    if not words:
        return ["", "", ""]
    needed = 17
    seq = list(words)
    if len(seq) < needed:
        seq.extend(list(islice(cycle(seq), needed - len(seq))))
    else:
        seq = seq[:needed]
    return [
        " ".join(seq[:5]),
        " ".join(seq[5:12]),
        " ".join(seq[12:17]),
    ]


def _haikuize_data(data: Dict[str, str], node_name: str) -> Dict[str, str]:
    data["node_name"] = node_name
    data["actions"].append("haikuize")
    data["words"] = _haikuize(data["words"])
    return data


def add_parser(subparsers) -> None:
    """Register the 'haikuize' subcommand."""
    sp = subparsers.add_parser("haikuize", help="Haikuize text")
    sp.add_argument("--input-node", required=True, help="Node to read input text from")
    sp.add_argument("--output-node", default="ROOT_NODE", help="Node name to store into")
    add_error_args(sp)
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Execute the haikuize command using the provided CLI ``args``."""
    maybe_raise_forced_error("Haikuize", args)
    input_node = load_node(args.input_node)
    data = _haikuize_data(input_node, args.output_node)
    save_node(args.output_node, data)
