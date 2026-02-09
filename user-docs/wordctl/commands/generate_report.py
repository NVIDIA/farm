# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate a simple report for one or more stored nodes."""

import argparse
from typing import List

from store import load_node
from .error_injection import add_error_args, maybe_raise_forced_error


def _compute_dumb_score(word_count: int, char_count: int, action_count: int) -> int:
    return (word_count * 7 + char_count * 3 + action_count * 11) % 101


def _funny_message(score: int) -> str:
    if score < 20:
        return "meh. add more words and maybe a sprinkle of pizzazz."
    if score < 40:
        return "needs more vowels. y or sometimes y?"
    if score < 60:
        return "acceptable mediocrity achieved."
    if score < 80:
        return "getting spicy. chef is preheating."
    return "chef's kiss. a true masterpiece of questionable metrics."


def _print_report_for_node(node_name: str) -> None:
    data = load_node(node_name)
    words = data["words"]
    actions = data["actions"]
    title = f"Report: {node_name}"
    sep = "=" * len(title)
    content_lines = words
    word_count = sum(len(line.split()) for line in content_lines)
    char_count = sum(len(line) for line in content_lines)
    action_count = len(actions)
    score = _compute_dumb_score(word_count, char_count, action_count)
    msg = _funny_message(score)

    print(title)
    print(sep)
    print("Content:")
    print("\n".join(content_lines))
    print()
    print("Stats:")
    print(f"- word count: {word_count}")
    print(f"- character count: {char_count}")
    print(f"- transformations: {action_count} -> {', '.join(actions) if actions else 'none'}")
    print(f"- score: {score}  ({msg})")
    print()


def generate_report(node_names: List[str]) -> None:
    """Print a human-friendly report for each node in ``node_names``."""
    for idx, node in enumerate(node_names):
        if idx:
            print("\n" + ("-" * 40) + "\n")
        _print_report_for_node(node)


def add_parser(subparsers) -> None:
    """Register the 'generate-report' subcommand."""
    sp = subparsers.add_parser("generate-report", help="Generate reports for one or more nodes")
    sp.add_argument("--input-node", action="append", help="Node to include (repeatable)")
    sp.add_argument("--input-node-list", dest="input_node_list", help="Comma-separated list of nodes to include")
    add_error_args(sp)
    sp.set_defaults(func=run)


def run(args: argparse.Namespace) -> None:
    """Entry point for the generate-report command."""
    maybe_raise_forced_error("Generate Report", args)
    nodes = []
    if getattr(args, "input_node", None):
        nodes.extend(args.input_node)
    if getattr(args, "input_node_list", None):
        nodes.extend([n.strip() for n in args.input_node_list.split(",") if n.strip()])
    if not nodes:
        print("Error: No nodes provided. Use --input-node or --input-node-list to specify nodes.")
        return
    generate_report(nodes)
