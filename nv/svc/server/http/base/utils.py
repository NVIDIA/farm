# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Utility Functions for Server Implementations."""
import platform
import random
import socket


def _check_for_windows(server, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Defaults to 2 seconds on Windows. Reducing to improve startup time.
    sock.settimeout(0.05)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    res = sock.connect_ex((server, port))
    if res == 0:
        raise Exception("socket in use")


def _check_for_unix(server, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, port))
    sock.close()


def validate_port(port, allow_range=True, socket_range=(8000, 8100)) -> int:
    """Validate port and return one in the socket_range.

    Args:
        port (_type_): _description_
        allow_range (bool, optional): _description_. Defaults to True.
        socket_range (tuple, optional): _description_. Defaults to (8000, 8100).

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        int: _description_
    """
    port = int(port) if port else 0
    if port == 0 and allow_range:
        port = random.randint(*socket_range)
    elif port == 0:
        raise Exception(
            "No port provided and not allowed to pick random port within given range"
        )

    server = "localhost"
    for _ in range(20):
        try:
            (
                _check_for_windows(server, port)
                if platform.system().lower() == "windows"
                else _check_for_unix(server, port)
            )
            return port
        except Exception:
            port = random.randint(*socket_range)
    else:
        raise Exception("No ports available")
