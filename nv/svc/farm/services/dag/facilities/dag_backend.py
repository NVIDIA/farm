# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm DAG Database Backend."""

import abc
import asyncio
import logging
from typing import Dict, List, Tuple, Optional, Any

from nv.svc.farm.sql import SqlDatabase

logger = logging.getLogger(__name__)


class DAGNotFound(Exception):
    """Exception raised when a DAG is not found."""

    def __init__(self, dag_id: str):
        """Initialize the DAGNotFound exception."""
        self.dag_id = dag_id
        super().__init__(f"DAG {dag_id} not found")


class BaseDagBackend(abc.ABC):
    """Base class for DAG backend persistence solutions."""

    @abc.abstractmethod
    def __init__(self) -> None:
        """Initialize the DAG backend."""
        pass

    @abc.abstractmethod
    async def start(self) -> None:
        """Start the backend."""
        pass

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop the backend."""
        pass

    @abc.abstractmethod
    async def add_edges(
        self,
        dag_id: str,
        edges: List[Dict[str, str]],
        name: Optional[str] = None
    ) -> None:
        """Add multiple edges to the graph in a single transaction.

        Args:
            dag_id: ID of the DAG these edges belong to
            edges: List of edges, each containing source_task_id and target_task_id
            name: Optional name for the DAG (for display purposes)
        """
        pass

    @abc.abstractmethod
    async def get_all_edges(self, dag_id: str) -> List[Tuple[str, str]]:
        """Get all edges in the graph.

        Args:
            dag_id: ID of the DAG to get edges for

        Returns:
            List[Tuple[str, str]]: List of (source_id, target_id) tuples
        """
        pass

    @abc.abstractmethod
    async def get_dag_version(self, dag_id: str) -> int:
        """Get the current version of the DAG.

        Args:
            dag_id: ID of the DAG to get version for

        Returns:
            int: Current version of the DAG
        """
        pass

    @abc.abstractmethod
    async def delete_dag(self, dag_id: str) -> None:
        """Delete a DAG and all its edges.

        Args:
            dag_id: ID of the DAG to delete
        """
        pass


class DagDatabaseBackend(BaseDagBackend):
    """Database backend for DAG persistence."""

    def __init__(self, connection_string: str, **kwargs):
        """Initialize the DAG backend with a database connection.

        Args:
            connection_string: Database connection string
            **kwargs: Additional arguments passed to the database connection
        """
        self._database = SqlDatabase(connection_string=connection_string, **kwargs)
        self._graph_table_name = "task_graph"
        self._graph_index_name = "task_graph_idx"
        self._version_table_name = "task_graph_version"

        # Check database type
        self._is_mysql = 'mysql' in connection_string
        self._is_postgresql = 'postgresql' in connection_string

    def _get_id_column_type(self) -> str:
        """Get the appropriate column type for ID fields based on database type."""
        if self._is_postgresql:
            return "UUID"
        return "VARCHAR(36)"

    def _get_mysql_upsert_query(self, name: Optional[str] = None) -> str:
        """Get MySQL-specific upsert query.

        Args:
            name: Optional name for the DAG. If None, preserves existing name.

        Returns:
            str: MySQL upsert query
        """
        if name is not None:
            return (
                f"INSERT INTO {self._version_table_name} (dag_id, version, name) "
                "VALUES (:dag_id, 1, :name) "
                "ON DUPLICATE KEY UPDATE version = version + 1, name = :name"
            )
        return (
            f"INSERT INTO {self._version_table_name} (dag_id, version) "
            "VALUES (:dag_id, 1) "
            "ON DUPLICATE KEY UPDATE version = version + 1"
        )

    def _get_postgresql_upsert_query(self, name: Optional[str] = None) -> str:
        """Get PostgreSQL-specific upsert query.

        Args:
            name: Optional name for the DAG. If None, preserves existing name.

        Returns:
            str: PostgreSQL upsert query
        """
        if name is not None:
            return (
                f"INSERT INTO {self._version_table_name} (dag_id, version, name) "
                "VALUES (:dag_id, 1, :name) "
                f"ON CONFLICT (dag_id) DO UPDATE SET version = {self._version_table_name}.version + 1, name = :name"
            )
        return (
            f"INSERT INTO {self._version_table_name} (dag_id, version) "
            "VALUES (:dag_id, 1) "
            f"ON CONFLICT (dag_id) DO UPDATE SET version = {self._version_table_name}.version + 1"
        )

    def _get_sqlite_upsert_query(self, name: Optional[str] = None) -> str:
        """Get SQLite-specific upsert query.

        Args:
            name: Optional name for the DAG. If None, preserves existing name.

        Returns:
            str: SQLite upsert query
        """
        if name is not None:
            return (
                f"INSERT OR REPLACE INTO {self._version_table_name} (dag_id, version, name) "
                f"VALUES (:dag_id, COALESCE((SELECT version + 1 FROM {self._version_table_name} "
                f"WHERE dag_id = :dag_id), 1), :name)"
            )
        return (
            f"INSERT OR REPLACE INTO {self._version_table_name} (dag_id, version, name) "
            f"VALUES (:dag_id, COALESCE((SELECT version + 1 FROM {self._version_table_name} "
            f"WHERE dag_id = :dag_id), 1), (SELECT name FROM {self._version_table_name} "
            f"WHERE dag_id = :dag_id))"
        )

    async def _upsert_version(self, dag_id: str, name: Optional[str] = None) -> None:
        """Update version with database-specific syntax.

        Args:
            dag_id: ID of the DAG to update version for
            name: Optional name for the DAG. If None, preserves existing name.
        """
        values = {"dag_id": dag_id}
        if name is not None:
            values["name"] = name

        if self._is_mysql:
            query = self._get_mysql_upsert_query(name)
        elif self._is_postgresql:
            query = self._get_postgresql_upsert_query(name)
        else:
            query = self._get_sqlite_upsert_query(name)

        await self._database.execute(query=query, values=values)

    async def _initialize_database(self) -> None:
        """Initialize the database schema."""
        id_type = self._get_id_column_type()

        # Create table for storing graph edges
        table_columns = [
            f"dag_id {id_type} NOT NULL",
            f"source_task_id {id_type} NOT NULL",
            f"target_task_id {id_type} NOT NULL",
            "PRIMARY KEY (dag_id, source_task_id, target_task_id)",
        ]
        query = f"CREATE TABLE IF NOT EXISTS {self._graph_table_name} ({', '.join(table_columns)});"
        await self._database.execute(query=query)

        # Create index for faster lookups (dialect aware)
        try:
            if self._is_mysql:
                await self._create_mysql_graph_index()
            else:
                await self._create_graph_index()
        except Exception as exc:
            logging.warning(f"Unable to create table index for DAG store: {str(exc)}")

        # Create version tracking table
        version_columns = [
            f"dag_id {id_type} NOT NULL",
            "version INTEGER NOT NULL DEFAULT 0",
            "name VARCHAR(255)",
            "PRIMARY KEY (dag_id)"
        ]
        query = f"CREATE TABLE IF NOT EXISTS {self._version_table_name} ({', '.join(version_columns)});"
        await self._database.execute(query=query)

    async def _create_mysql_graph_index(self) -> None:
        """Create the task graph index in MySQL (emulate IF NOT EXISTS)."""
        # Check if index exists
        show_idx_query = (
            f"SHOW INDEX FROM {self._graph_table_name} WHERE Key_name = '{self._graph_index_name}'"
        )
        rows = await self._database.fetch_all(query=show_idx_query)
        if rows:
            return
        create_idx_query = (
            f"CREATE INDEX {self._graph_index_name} "
            f"ON {self._graph_table_name} (dag_id, source_task_id, target_task_id)"
        )
        await self._database.execute(query=create_idx_query)

    async def _create_graph_index(self) -> None:
        """Create the task graph index for dialects that support IF NOT EXISTS (PostgreSQL/SQLite)."""
        create_idx_query = (
            f"CREATE INDEX IF NOT EXISTS {self._graph_index_name} "
            f"ON {self._graph_table_name} (dag_id, source_task_id, target_task_id);"
        )
        await self._database.execute(query=create_idx_query)

    async def start(self) -> None:
        """Start the backend and initialize database schema."""
        await self._database.connect()
        await self._initialize_database()

    async def stop(self) -> None:
        """Stop the backend."""
        await self._database.disconnect()

    async def add_edges(
        self,
        dag_id: str,
        edges: List[Dict[str, str]],
        name: Optional[str] = None
    ) -> None:
        """Add multiple edges to the graph in a single transaction.

        Args:
            dag_id: ID of the DAG these edges belong to
            edges: List of edges, each containing source_task_id and target_task_id
            name: Optional name for the DAG (for display purposes)
        """
        async with self._database.transaction():
            # First delete existing edges for this DAG
            query = f"DELETE FROM {self._graph_table_name} WHERE dag_id = :dag_id"
            await self._database.execute(query=query, values={"dag_id": dag_id})

            # Prepare values for bulk insert
            values = [
                {
                    "dag_id": dag_id,
                    "source_task_id": edge["source_task_id"],
                    "target_task_id": edge["target_task_id"]
                }
                for edge in edges
            ]

            # Bulk insert edges
            query = (
                f"INSERT INTO {self._graph_table_name} "
                "(dag_id, source_task_id, target_task_id) "
                "VALUES (:dag_id, :source_task_id, :target_task_id)"
            )
            await self._database.execute_many(query=query, values=values)

            # Increment version using database-specific upsert
            await self._upsert_version(dag_id, name)

    async def get_all_edges(self, dag_id: str) -> List[Tuple[str, str]]:
        """Get all edges in the graph.

        Args:
            dag_id: ID of the DAG to get edges for

        Returns:
            List[Tuple[str, str]]: List of (source_id, target_id) tuples
        """
        query = (
            f"SELECT source_task_id, target_task_id "
            f"FROM {self._graph_table_name} "
            f"WHERE dag_id = :dag_id "
            f"ORDER BY source_task_id, target_task_id"
        )

        rows = await self._database.fetch_all(query=query, values={"dag_id": dag_id})
        return [(row[0], row[1]) for row in rows]

    async def get_dag_version(self, dag_id: str) -> int:
        """Get the current version of the DAG.

        Args:
            dag_id: ID of the DAG to get version for

        Returns:
            int: Current version of the DAG
        """
        query = f"SELECT version, name, dag_id FROM {self._version_table_name} WHERE dag_id = :dag_id"

        row = await self._database.fetch_one(query=query, values={"dag_id": dag_id})
        return row[0] if row else 0

    async def get_dag_info(self, dag_id: str) -> Dict[str, Any]:
        """Get DAG metadata (name, version) and edges for the given DAG.

        Args:
            dag_id: ID of the DAG to retrieve

        Returns:
            Dict[str, Any]: A dictionary containing:
                - dag_id: The DAG identifier
                - name: Optional name of the DAG (or None if unset)
                - version: Current version number (0 if not present)
                - edges: List of edges as dicts with source_task_id/target_task_id

        Raises:
            DAGNotFound: If the DAG is not found
        """
        # Fetch name+version and edges concurrently
        version_row, edge_tuples = await asyncio.gather(
            self._database.fetch_one(
                query=f"SELECT version, name FROM {self._version_table_name} WHERE dag_id = :dag_id",
                values={"dag_id": dag_id},
            ),
            self.get_all_edges(dag_id=dag_id),
        )

        if not version_row:
            raise DAGNotFound(dag_id=dag_id)

        version = version_row["version"]
        name = version_row["name"]
        edges = [
            {"source_task_id": src, "target_task_id": dst} for (src, dst) in edge_tuples
        ]

        return {
            "dag_id": dag_id,
            "name": name,
            "version": version,
            "edges": edges,
        }

    async def delete_dag(self, dag_id: str) -> None:
        """Delete a DAG and all its edges.

        Args:
            dag_id: ID of the DAG to delete
        """
        async with self._database.transaction():
            # Delete edges
            query = f"DELETE FROM {self._graph_table_name} WHERE dag_id = :dag_id"
            await self._database.execute(query=query, values={"dag_id": dag_id})

            # Delete version
            query = f"DELETE FROM {self._version_table_name} WHERE dag_id = :dag_id"
            await self._database.execute(query=query, values={"dag_id": dag_id})
