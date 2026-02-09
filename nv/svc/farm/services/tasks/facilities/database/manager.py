# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Database Manager Facility."""

from contextlib import asynccontextmanager
import logging
from typing import Any, Callable, Coroutine, Dict, Generator, List
from urllib.parse import urlparse

from nv.svc.core.facilities import base

from nv.svc.farm.services.tasks.config import FarmTasksConfig
from nv.svc.farm.sql import SqlDatabase
from .base import BaseDatabase


class _DatabaseMetadata():
    """Metadata information about database settings provided in TOML files."""

    def __init__(self, connection_string: str, **kwargs: Any) -> None:

        self.connection_string: str = connection_string
        self.kwargs: Any = kwargs


class DatabaseManagerFacility(base.Facility):
    """Database Manager Facility."""

    def __init__(self):
        """Database manager constructor."""

        self._database_registry: Dict[str, Callable[[Any], BaseDatabase]] = {}
        self._config = FarmTasksConfig(auto_configure_logging=False)

        self._database_configurations = self._config.tasks.dbs

        self._settings: Dict[str, _DatabaseMetadata] = self._load_database_registry()
        self._instances: Dict[str, BaseDatabase] = {}

        # Register common SQL-like databases supported by default:
        for supported_sql_scheme in SqlDatabase.supported_sql_schemes:
            self.register_database(supported_sql_scheme, SqlDatabase)

    def _load_database_registry(self) -> Dict[str, _DatabaseMetadata]:
        """
        Scan the settings for User-provided configuration information about databases.

        Returns:
            Dict[str, _DatabaseMetadata]: Database configuration settings read from configuration files.

        """
        if not self._database_configurations:
            logging.warning("No databases were configured.")

        sanitized_database_settings: Dict[str, _DatabaseMetadata] = {}
        for database_handle, database_configuration in self._database_configurations.items():
            if "connection_string" not in database_configuration:
                logging.error(f"Expected to find required \"connection_string\" property for configuration of \"{database_handle}\" database.")
                continue

            connection_string = database_configuration.pop("connection_string")
            sanitized_database_settings[database_handle] = _DatabaseMetadata(
                connection_string=connection_string,
                **database_configuration,
            )

        return sanitized_database_settings

    def register_database(self, database_scheme: str, constructor: Callable[[Any], BaseDatabase]) -> bool:
        if database_scheme in self._database_registry:
            logging.warning(f"Database with handle \"{database_scheme}\" was already registered.")
            return False

        self._database_registry[database_scheme] = constructor
        return True

    def get_registered_database_schemes(self) -> List[str]:
        """
        Return the list of registered database schemes.

        (e.g. "postgresql", "mysql", "sqlite", or one of the other SQL-like schemes registered by Users).

        Args:
            None

        Returns:
            List[str]: The list of registered database schemes.

        """
        return self._database_registry.keys()

    async def connect(self, database_handle: str) -> Coroutine[Any, Any, None]:
        """
        Connect to the database with the given handle.

        Args:
            database_handle (str): Handle of the database to connect to.

        Returns:
            Coroutine[Any, Any, None]: ``await``-able response while connecting.

        """
        if database_handle not in self._settings:
            raise RuntimeError(f"Database with handle \"{database_handle}\" was not registered.")

        if database_handle not in self._instances:
            database_metadata = self._settings[database_handle]
            scheme = self._get_scheme_from_connection_string(database_metadata.connection_string)
            if scheme not in self._database_registry:
                raise RuntimeError(f"Unable to construct connector for \"{database_handle}\" database of scheme \"{scheme}\".")
            constructor = self._database_registry[scheme]
            self._instances[database_handle] = constructor(database_metadata.connection_string, **database_metadata.kwargs)

        await self._instances[database_handle].connect()

    async def disconnect(self, database_handle: str) -> Coroutine[Any, Any, None]:
        """
        Disconnect from the database with the given handle.

        Args:
            database_handle (str): Handle of the database from which to disconnect.

        Returns:
            Coroutine[Any, Any, None]: An ``await``-able response while disconnecting.

        """
        if database_handle not in self._instances:
            raise RuntimeError(f"No database instance registered for handle \"{database_handle}\".")
        await self._instances[database_handle].disconnect()

    @asynccontextmanager
    async def get(self, database_handle: str) -> Generator[BaseDatabase, Any, Any]:
        """
        Return an asynchronous context to the underlying database technology.

        Args:
            database_handle (str): Handle of the database to connect to.

        Returns:
            Coroutine[BaseDatabase, Any, Any]: An ``await``-able response to the underlying database.

        """
        await self.connect(database_handle=database_handle)
        yield self._instances[database_handle]

    def _get_scheme_from_connection_string(self, connection_string: str) -> str:
        """
        Return the scheme from the given database connection string.

        (e.g. "postgresql", "mysql", "sqlite", or one of the other SQL-like schemes registered by Users).

        Args:
            connection_string (str): Connection string of the database for which to return the scheme.

        Returns:
            str: Scheme of the database connection string.

        """
        parsed_data = urlparse(connection_string)
        return parsed_data.scheme

    def stop(self) -> None:
        """Stop the facility."""

        self._database_registry = {}
        self._settings = {}
        self._instances = {}
