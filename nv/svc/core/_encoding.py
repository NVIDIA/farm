# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import typing

_encoders = {}


def register_encoder(name: str, encoder: typing.Any):
    """Register a data encoder.

    The encoder must have a `compress` and `decompress` function
    """
    if not hasattr(encoder, "compress") or not hasattr(encoder, "decompress"):
        raise AttributeError(f"{name} is missing the 'compress' or 'decompress' (or both) function. Cannot register encoder.")
    _encoders[name] = encoder


def get_encoder(name: str):
    """Return the encoder for the given name.

    Raises:
        - KeyError: Raised when given encoder is not found.
    """
    return _encoders[name]


try:
    import gzip

    register_encoder("gzip", gzip)
except Exception as exc:
    logging.error(f"Failed to register gzip as a decoder: {exc}")


try:
    import zlib

    register_encoder("deflate", zlib)
except Exception as exc:
    logging.error(f"Failed to register deflate as a decoder: {exc}")
