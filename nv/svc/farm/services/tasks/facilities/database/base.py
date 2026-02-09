# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base database interface."""

from types import TracebackType
from typing import Any, AsyncGenerator, List, Optional, Mapping, Type


class BaseDatabase:
    """Base database interface."""

    @property
    def is_connected(self):
        """
        Return a flag indicating whether a connection to the database is currently established.

        Args:
            None

        Returns:
            bool: A flag indicating whether a connection to the database is currently established.

        """
        return False

    @property
    def url(self) -> str:
        """
        Return the URL used as connection string to the underlying database.

        Args:
            None

        Returns:
            str: The URL used as connection string to the underlying database.
        """
        raise NotImplementedError()

    async def connect(self) -> None:
        """Establish a connection to the database, and initialize connection pools."""
        raise NotImplementedError()

    async def disconnect(self) -> None:
        """Close all connections from the connection pool."""
        raise NotImplementedError()

    async def __aenter__(self) -> "BaseDatabase":
        """Initialize an asynchronous context manager for the database connection."""
        raise NotImplementedError()

    async def __aexit__(
        self,
        exception_type: Type[BaseException] = None,
        exception_value: BaseException = None,
        traceback: TracebackType = None
    ) -> None:
        """
        Cleanup the asynchronous context manager for the database connection.

        Args:
            exception_type (Type[BaseException]): Type of the exeception thrown in the context, if any.
            exception_value (BaseException): Instance of the exception thrown in the context, if any.
            traceback (TracebackType): Stack traceback of the exception thrown in the context, if any.

        Returns:
            None

        """
        raise NotImplementedError()

    async def fetch_all(self, query: str, values: dict = None) -> List[Mapping]:
        """
        Return the list of all rows matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            List[Mapping]: The list of rows matching the given query.

        """
        raise NotImplementedError()

    async def fetch_one(self, query: str, values: dict = None) -> Optional[Mapping]:
        """
        Return one row matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            Optional[Mapping]: The row matching the given query, if any.

        """
        raise NotImplementedError()

    async def fetch_val(self, query: str, values: dict = None, column: Any = 0) -> Any:
        """
        Return the value at the given column index for the row matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            Any: The value at the given column index for the row matching the given query.

        """
        raise NotImplementedError()

    async def execute(self, query: str, values: dict = None) -> Any:
        """
        Execute the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            Any: The return value depends on the underlying database technology used.

        """
        raise NotImplementedError()

    async def execute_many(self, query: str, values: list) -> None:
        """
        Successively execute the given query for all the given values.

        Rows are expected to be fetched using data retrieval APIs such as ``fetch_all()``.

        Args:
            query (str): Query to perform.
            values (list): List of values to successively insert into the query to perform.

        Returns:
            None

        """
        raise NotImplementedError()

    async def iterate(self, query: str, values: dict = None) -> AsyncGenerator[Mapping, None]:
        """
        Asynchronously yield rows matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            AsyncGenerator[Mapping, None]: A series of rows matching the given query.

        """
        raise NotImplementedError()

    def connection(self) -> Any:
        """
        Return a reference to the database's underlying connection.

        Args:
            None

        Returns:
            Any: A reference to the database's underlying connection.

        """
        raise NotImplementedError()

    def transaction(self, **kwargs: Any) -> Any:
        """
        Return a transaction context allowing the rollback of failed queries.

        Args:
            **kwargs (Any): Transaction parameters (depends on the underlying database technology used).

        Returns:
            Any: A transaction context allowing the rollback of failed queries.

        """
        raise NotImplementedError()
