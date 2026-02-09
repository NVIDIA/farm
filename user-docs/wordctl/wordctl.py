# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""CLI entrypoint for `wordctl` to operate on words and reports."""

import argparse

from commands import store, piglatinize, haikuize, bannerize, shadowize, generate_report


def make_parser() -> argparse.ArgumentParser:
    """Create and return the top-level argument parser."""
    p = argparse.ArgumentParser(prog="wordctl", description="Operate on a word: store, transform, report")
    subparsers = p.add_subparsers(dest="command", required=True)

    store.add_parser(subparsers)

    piglatinize.add_parser(subparsers)

    haikuize.add_parser(subparsers)

    bannerize.add_parser(subparsers)

    shadowize.add_parser(subparsers)

    generate_report.add_parser(subparsers)

    return p


def main() -> None:
    """Parse arguments and dispatch to the selected subcommand."""
    parser = make_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
