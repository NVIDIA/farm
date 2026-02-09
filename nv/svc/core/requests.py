# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework requests."""
from typing import Dict, Optional

from fastapi import Request


def get_correlation_id() -> Optional[str]:
    """
    Return a correlation ID to use to uniquely identify requests emitted against the Service.

    Returns:
        Optional[str]: A correlation ID to use to uniquely identify requests emitted against the Service, if the
            component is available.

    """
    try:
        from asgi_correlation_id import correlation_id

        return correlation_id.get()
    except ImportError:
        pass

    return None


def convert_headers_to_dict(request: Request) -> Dict[str, str]:
    """
    Convert the Headers from the given FastAPI Request to an equivalent Python dictionary format.

    NOTE: This implementation accounts for the fact that FastAPI Request Headers can contain multiple identical keys (of
    with mixed casing) due to their format being a list of key-value pairs. The `AsyncClient` implementation, on its
    side, expects Headers to be supplied as a Python dictionary, which can result in keys being erased if proceeding
    with a straight dictionary assignment of the incoming Header values. In order to avoid this potential loss of data,
    this utility method employs section 4.2 of the IETF RFC 2616 in order to merge values sharing a similar key into a
    comma-delimited unique value ordered in the same sequence as the original Request Headers. For more details, see
    https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html

    Args:
        request (Request): The FastAPI Request whose Headers should be converted to an equivalent Python dictionary.

    Returns:
        Dict[str, str]: The Python dictionary equivalent to the Headers included in the given FastAPI Request.

    """
    dict_headers: Dict[str, str] = {}

    for header in request.headers.items():
        key, value = header
        key = key.lower()

        if key in dict_headers:
            dict_headers[key] = f"{dict_headers[key]},{value}"
        else:
            dict_headers[key] = value

    return dict_headers
