# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""SQL database adapter."""

from enum import Enum
from pathlib import Path
import logging
from types import TracebackType
from typing import Any, AsyncGenerator, Dict, List, Mapping, Optional, Type

from databases import Database

from nv.svc.farm import utils


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


class SupportedSqlSchemes(str, Enum):
    """List of SQL-like schemes supported by the underlying database technology."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

    @classmethod
    def list_schemes(cls) -> List[str]:
        """
        Return the list of all supported SQL schemes.

        Args:
            None

        Returns:
            List[str]: The list of all supported SQL schemes.

        """
        return [member.value for _, member in cls.__members__.items()]


class SqlDatabase(BaseDatabase):
    """
    Adapter for SQL databases (PostgreSQL, MySQL, or SQLite).

    Note:
        The underlying package for managing database connections is PIP's ``databases``. See the package's documentation
        at https://www.encode.io/databases/ for additional information.

    Example:
        This brief sample provides an overview of the SQL database's API by:
          * Creating a database instance, and connecting to it.
          * Creating a table.
          * Inserting data into the newly-created table.
          * Finally, running a query to retrieve the newly-inserted data.

        .. code-block:: python
            :linenos:

            from databases import Database

            database = Database("sqlite:///example.db")
            await database.connect()

            query = "CREATE TABLE HighScores (id INTEGER PRIMARY KEY, name VARCHAR(100), score INTEGER)"
            await database.execute(query=query)

            query = "INSERT INTO HighScores(name, score) VALUES (:name, :score)"
            values = [
                {"name": "Daisy", "score": 92},
                {"name": "Neil", "score": 87},
                {"name": "Carol", "score": 43},
            ]
            await database.execute_many(query=query, values=values)

            query = "SELECT * FROM HighScores"
            rows = await database.fetch_all(query=query)
            print("High Scores:", rows)

    """

    """List of SQL-like schemes supported by the underlying database technology."""
    supported_sql_schemes: List[str] = SupportedSqlSchemes.list_schemes()

    def __init__(self, connection_string: str, **kwargs: Dict[str, Any]) -> None:
        """
        Database constructor.

        Note:
            Additional arguments to the connection can be supplied either as querystring parameters, or using named
            arguments. See https://www.encode.io/databases/connections_and_transactions/#connection-options for
            additional information.

        Examples:
            To use an SSL connection to PostgreSQL:

            .. code-block:: python
                :linenos:

                database = Database("postgresql://localhost/example?ssl=true")

            To use a MySQL connection pool of between 5 and 20 connections:

            .. code-block:: python
                :linenos:

                database = Database("mysql://localhost/example?min_size=5&max_size=20")

            Alternatively, using named parameters:

            .. code-block:: python
                :linenos:

                database = Database("postgresql://localhost/example", ssl=True, min_size=5, max_size=20)

        Args:
            connection_string (str): Connection string of the database.
            **kargs (Dict[str, Any]): Optional named arguments used by the underlying database technology.

        """
        super().__init__()
        self._database = Database(url=self._load_connection_string(connection_string), **kwargs)

    def _load_connection_string(self, connection_string: str) -> str:
        if "FARM_USER_DATA_DIR" in connection_string:
            connection_string = connection_string.format(FARM_USER_DATA_DIR=utils.FARM_USER_DATA_DIR)
            logging.debug(f"Creating {utils.FARM_USER_DATA_DIR} if it does not exist.")
            try:
                Path(utils.FARM_USER_DATA_DIR).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error(f"Unable to create directory {utils.FARM_USER_DATA_DIR} - error {e}")
                raise
        return connection_string

    @property
    def is_connected(self):
        """
        Return a flag indicating whether a connection to the database is currently established.

        Args:
            None

        Returns:
            bool: A flag indicating whether a connection to the database is currently established.

        """
        return self._database.is_connected

    @property
    def url(self) -> str:
        """
        Return the URL used as connection string to the underlying database.

        Args:
            None

        Returns:
            str: The URL used as connection string to the underlying database.

        """
        return str(self._database.url)

    @property
    def is_postgresql(self) -> bool:
        """
        Return a flag indicating whether the SQL Database is PostgreSQL.

        Args:
            None

        Returns:
            bool: A flag indicating whether the SQL Database is PostgreSQL.

        """
        return self.url.lower().startswith(SupportedSqlSchemes.POSTGRESQL.value)

    @property
    def is_mysql(self) -> bool:
        """
        Return a flag indicating whether the SQL Database is MySQL.

        Args:
            None

        Returns:
            bool: A flag indicating whether the SQL Database is MySQL.

        """
        return self.url.lower().startswith(SupportedSqlSchemes.MYSQL.value)

    @property
    def is_sqlite(self) -> bool:
        """
        Return a flag indicating whether the SQL Database is SQLite.

        Args:
            None

        Returns:
            bool: A flag indicating whether the SQL Database is SQLite.

        """
        return self.url.lower().startswith(SupportedSqlSchemes.SQLITE.value)

    async def connect(self) -> None:
        """Establish a connection to the database, and initialize connection pools."""
        if not self.is_connected:
            await self._database.connect()

    async def disconnect(self) -> None:
        """Close all connections from the connection pool."""
        if self.is_connected:
            await self._database.disconnect()

    async def __aenter__(self) -> "SqlDatabase":
        """Initialize an asynchronous context manager for the database connection."""
        await self._database.__aenter__()
        return self

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
        await self._database.__aexit__(exception_type, exception_value, traceback)

        # To force sqlite writing out its buffer.
        # This needs to stay specific to sqlite, as __aexit__ for mysql/postgres already calls `disconnect` on __aexit__
        # which would lead to it hanging indefinitely.
        if self.is_sqlite:
            await self.disconnect()

    async def fetch_all(self, query: str, values: dict = None) -> List[Mapping]:
        """
        Return the list of all rows matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            List[Mapping]: The list of rows matching the given query.

        """
        return await self._database.fetch_all(query, values)

    async def fetch_one(self, query: str, values: dict = None) -> Optional[Mapping]:
        """
        Return one row matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            Optional[Mapping]: The row matching the given query, if any.

        """
        return await self._database.fetch_one(query, values)

    async def fetch_val(self, query: str, values: dict = None, column: Any = 0) -> Any:
        """
        Return the value at the given column index for the row matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            Any: The value at the given column index for the row matching the given query.

        """
        return await self._database.fetch_val(query, values, column)

    async def execute(self, query: str, values: dict = None) -> Any:
        """
        Execute the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            Any: The return value depends on the underlying database technology used.

        """
        return await self._database.execute(query, values)

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
        await self._database.execute_many(query, values)

    async def iterate(self, query: str, values: dict = None) -> AsyncGenerator[Mapping, None]:
        """
        Asynchronously yield rows matching the given query.

        Args:
            query (str): Query to perform.
            values (dict): Values to insert into the query to perform.

        Returns:
            AsyncGenerator[Mapping, None]: A series of rows matching the given query.

        """
        return await self._database.iterate(query, values)

    def connection(self) -> Any:
        """
        Return a reference to the database's underlying connection.

        Args:
            None

        Returns:
            Any: A reference to the database's underlying connection.

        """
        return self._database.connection()

    def transaction(self, **kwargs: Any) -> Any:
        """
        Return a transaction context allowing the rollback of failed queries.

        Args:
            **kwargs (Any): Transaction parameters (depends on the underlying database technology used).

        Returns:
            Any: A transaction context allowing the rollback of failed queries.

        """
        return self._database.transaction(**kwargs)
