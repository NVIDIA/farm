# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Bannerize command: render words inside a bordered, padded block."""

import argparse
import textwrap
from typing import Dict, List

from store import load_node, save_node
from .error_injection import add_error_args, maybe_raise_forced_error


def _bannerize(words: List[str], border: str = "*", align: str = "center") -> List[str]:
    width = max([len(word) for word in words]) + 6
    inner = width - 6
    text = " ".join(words).strip()
    wrapped = textwrap.wrap(text, inner, break_long_words=True, drop_whitespace=True) or [""]
    top = border * width
    side = border * 2

    def pad(line: str) -> str:
        line = line.center(inner)
        return f"{side} {line} {side}"
    return [top] + [pad(inner_line) for inner_line in wrapped] + [top]


def _bannerize_data(data: Dict[str, str], node_name: str) -> Dict[str, str]:
    data["node_name"] = node_name
    data["actions"].append("bannerize")
    data["words"] = _bannerize(data["words"])
    return data


def add_parser(subparsers) -> None:
    """Register the 'bannerize' subparser on the given ``subparsers``."""
    sp = subparsers.add_parser("bannerize", help="Bannerize text")
    sp.add_argument("--input-node", required=True, help="Node to read input text from")
    sp.add_argument("--output-node", default="ROOT_NODE", help="Node name to store into")
    add_error_args(sp)
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Execute the bannerize command using the provided CLI ``args``."""
    maybe_raise_forced_error("Bannerize", args)
    input_node = load_node(args.input_node)
    data = _bannerize_data(input_node, args.output_node)
    save_node(args.output_node, data)
