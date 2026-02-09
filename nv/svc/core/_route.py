# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from . import _encoding


class _CompressedRequest(Request):
    """Custom Request class for handling compressed request bodies.

    Extends the base Request class to support decompression of the request body
    based on the specified Content-Encoding headers.

    """

    async def body(self) -> bytes:
        """Retrieve the decompressed request body.

        Returns:
            bytes: The decompressed request body.

        """
        if not hasattr(self, "_body"):
            body = await super().body()

            for encoder_name in self.headers.getlist("Content-Encoding"):
                try:
                    encoder = _encoding.get_encoder(encoder_name)
                    body = encoder.decompress(body)
                    break
                except KeyError:
                    logging.error(f"{encoder_name} is not a registered decoder")

            self._body = body
        return self._body


class CompressedRoute(APIRoute):
    """Custom APIRoute class for handling compressed request bodies.

    Extends the base APIRoute class to use a custom request handler that supports
    decompression of the request body using the _CompressedRequest class.

    """

    def get_route_handler(self) -> Callable:
        """Get the custom route handler for handling compressed requests.

        Returns:
            Callable: The custom route handler.

        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = _CompressedRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler
