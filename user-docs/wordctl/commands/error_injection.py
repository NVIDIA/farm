# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared error-injection helpers for wordctl CLI subcommands."""

import argparse
import random
from typing import Optional


def add_error_args(parser: argparse.ArgumentParser) -> None:
    """Add error injection flags to a subcommand parser."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--error", nargs='?', const=True, default=None, help="Force this task attempt to fail")
    group.add_argument(
        "--random-error",
        nargs='?',
        const=True,
        default=None,
        dest="random_error",
        help="Randomly fail this task attempt (≈66% chance)",
    )
    parser.add_argument(
        "--error-message",
        dest="error_message",
        default=None,
        help="Optional custom message for the forced error",
    )


def maybe_raise_forced_error(command_name: str, args: argparse.Namespace, probability: float = 2.0 / 3.0) -> None:
    """Raise a RuntimeError according to error flags on the CLI args.

    Checks for presence of flags, not their values. This allows both:
        --error          (flag alone)
        --error true     (flag with any value - we just check if it's present)
    """
    if getattr(args, "error", None) is not None:
        message = _message_or_default(args.error_message, command_name, flag="--error")
        raise RuntimeError(message)
    if getattr(args, "random_error", None) is not None:
        if random.random() < probability:
            message = _message_or_default(args.error_message, command_name, flag="--random-error")
            raise RuntimeError(message)


def _message_or_default(custom: Optional[str], command_name: str, flag: str) -> str:
    if custom:
        return custom
    return f"{command_name} failed with forced error using the {flag} flag"
