# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Piglatinize command: transform words to Pig Latin while preserving case."""

import argparse
from typing import Dict

from store import load_node, save_node
from .error_injection import add_error_args, maybe_raise_forced_error


def _to_piglatin(word: str) -> str:
    if not word:
        return word
    vowels = "aeiou"
    w = word
    lower = w.lower()
    if lower[0] in vowels:
        pig = lower + "yay"
    else:
        i, n = 0, len(lower)
        while i < n and lower[i] not in vowels:
            if lower[i] == 'q' and i + 1 < n and lower[i + 1] == 'u':
                i += 2
                break
            i += 1
        pig = lower[i:] + lower[:i] + "ay"
    if w[0].isupper():
        pig = pig.capitalize()
    return pig


def _piglatinize_data(data: Dict[str, str], node_name: str) -> Dict[str, str]:
    data["node_name"] = node_name
    data["actions"].append("piglatinize")
    data["words"] = [_to_piglatin(word) for word in data["words"]]
    return data


def add_parser(subparsers) -> None:
    """Register the 'piglatinize' subcommand."""
    sp = subparsers.add_parser("piglatinize", help="Piglatinize text")
    sp.add_argument("--input-node", required=True, help="Node to read input text from")
    sp.add_argument("--output-node", default="ROOT_NODE", help="Node name to store into")
    add_error_args(sp)
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Execute the piglatinize command using the provided CLI ``args``."""
    maybe_raise_forced_error("Piglatinize", args)
    input_node = load_node(args.input_node)
    data = _piglatinize_data(input_node, args.output_node)
    save_node(args.output_node, data)
