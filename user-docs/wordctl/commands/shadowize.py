# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shadowize command: apply a simple drop shadow effect to text."""

import argparse
from typing import Dict, List

from store import load_node, save_node
from .error_injection import add_error_args, maybe_raise_forced_error


def _shadowize(words: List[str], dx: int = 2, dy: int = 1, shade: str = "░") -> List[str]:
    if not words:
        return []
    lines: List[str] = []
    for w in words:
        parts = w.splitlines() if isinstance(w, str) else [str(w)]
        lines.extend(parts or [""])
    base_h = len(lines)
    base_w = max((len(line) for line in lines), default=0)
    canvas_h = base_h + max(0, dy)
    canvas_w = base_w + max(0, dx)
    canvas: List[List[str]] = [[" "] * canvas_w for _ in range(canvas_h)]
    if shade and len(shade) == 1:
        for y, line in enumerate(lines):
            sy = y + dy
            if sy >= canvas_h:
                continue
            for x, ch in enumerate(line):
                sx = x + dx
                if sx < canvas_w and ch != " ":
                    canvas[sy][sx] = shade
    for y, line in enumerate(lines):
        if y >= canvas_h:
            break
        row = canvas[y]
        for x, ch in enumerate(line):
            if x < canvas_w:
                row[x] = ch
    return ["".join(row).rstrip() for row in canvas]


def _shadowize_data(data: Dict[str, str], node_name: str) -> Dict[str, str]:
    data["node_name"] = node_name
    data["actions"].append("shadowize")
    data["words"] = _shadowize(data["words"])
    return data


def add_parser(subparsers) -> None:
    """Register the 'shadowize' subcommand."""
    sp = subparsers.add_parser("shadowize", help="Add drop shadow to text")
    sp.add_argument("--input-node", required=True, help="Node to read input text from")
    sp.add_argument("--output-node", default="ROOT_NODE", help="Node name to store into")
    add_error_args(sp)
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Execute the shadowize command using the provided CLI ``args``."""
    maybe_raise_forced_error("Shadowize", args)
    input_node = load_node(args.input_node)
    data = _shadowize_data(input_node, args.output_node)
    save_node(args.output_node, data)
