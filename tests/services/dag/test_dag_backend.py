# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the DAG backend."""

import os
import uuid
from unittest import IsolatedAsyncioTestCase
from unittest import mock

from nv.svc.farm.services.dag.facilities.dag_backend import DagDatabaseBackend


class TestDagDatabaseBackend(IsolatedAsyncioTestCase):
    """Test cases for the DAG database backend."""

    async def asyncSetUp(self):
        """Set up test database."""
        self.db_path = f"/tmp/test_dag_backend_{uuid.uuid4()}.db"
        self.backend = DagDatabaseBackend(f"sqlite:///{self.db_path}")
        await self.backend.start()

    async def asyncTearDown(self):
        """Clean up test database."""
        await self.backend.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_add_single_edge(self):
        """Test adding a single edge to the graph."""
        dag_id = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        target_id = str(uuid.uuid4())

        edges = [{"source_task_id": source_id, "target_task_id": target_id}]
        await self.backend.add_edges(dag_id, edges)

        stored_edges = await self.backend.get_all_edges(dag_id)
        self.assertEqual(len(stored_edges), 1)
        self.assertEqual(stored_edges[0], (source_id, target_id))

    async def test_add_multiple_edges(self):
        """Test adding multiple edges in a single transaction."""
        dag_id = str(uuid.uuid4())
        edges = [
            {"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())},
            {"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())},
            {"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())}
        ]
        await self.backend.add_edges(dag_id, edges)

        stored_edges = await self.backend.get_all_edges(dag_id)
        self.assertEqual(len(stored_edges), 3)

        # Convert edges to sets for unordered comparison
        stored_edge_set = set(stored_edges)
        expected_edge_set = {(edge["source_task_id"], edge["target_task_id"]) for edge in edges}
        self.assertEqual(stored_edge_set, expected_edge_set)

    async def test_add_edges_multiple_dags(self):
        """Test adding edges to multiple DAGs."""
        dag_id_1 = str(uuid.uuid4())
        dag_id_2 = str(uuid.uuid4())

        edges_1 = [{"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())}]
        edges_2 = [{"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())}]

        await self.backend.add_edges(dag_id_1, edges_1)
        await self.backend.add_edges(dag_id_2, edges_2)

        stored_edges_1 = await self.backend.get_all_edges(dag_id_1)
        stored_edges_2 = await self.backend.get_all_edges(dag_id_2)

        self.assertEqual(len(stored_edges_1), 1)
        self.assertEqual(len(stored_edges_2), 1)
        self.assertEqual(stored_edges_1[0], (edges_1[0]["source_task_id"], edges_1[0]["target_task_id"]))
        self.assertEqual(stored_edges_2[0], (edges_2[0]["source_task_id"], edges_2[0]["target_task_id"]))

    async def test_get_dag_version(self):
        """Test DAG version increments correctly."""
        dag_id = str(uuid.uuid4())

        # Initial version should be 0
        version = await self.backend.get_dag_version(dag_id)
        self.assertEqual(version, 0)

        # Add edges should increment version to 1
        edges = [{"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())}]
        await self.backend.add_edges(dag_id, edges)
        version = await self.backend.get_dag_version(dag_id)
        self.assertEqual(version, 1)

        # Adding more edges should increment version again
        await self.backend.add_edges(dag_id, edges)
        version = await self.backend.get_dag_version(dag_id)
        self.assertEqual(version, 2)

    async def test_delete_dag(self):
        """Test deleting a DAG removes all edges and version info."""
        dag_id = str(uuid.uuid4())
        edges = [{"source_task_id": str(uuid.uuid4()), "target_task_id": str(uuid.uuid4())}]

        await self.backend.add_edges(dag_id, edges)
        version = await self.backend.get_dag_version(dag_id)
        self.assertEqual(version, 1)

        await self.backend.delete_dag(dag_id)

        # After deletion, should have no edges and version should be 0
        stored_edges = await self.backend.get_all_edges(dag_id)
        version = await self.backend.get_dag_version(dag_id)
        self.assertEqual(len(stored_edges), 0)
        self.assertEqual(version, 0)

    async def test_complex_graph(self):
        """Test storing and retrieving a complex graph structure."""
        dag_id = str(uuid.uuid4())

        # Create a diamond-shaped graph with additional edges
        task_ids = [str(uuid.uuid4()) for _ in range(5)]
        edges = [
            # Diamond shape
            {"source_task_id": task_ids[0], "target_task_id": task_ids[1]},  # A -> B
            {"source_task_id": task_ids[0], "target_task_id": task_ids[2]},  # A -> C
            {"source_task_id": task_ids[1], "target_task_id": task_ids[3]},  # B -> D
            {"source_task_id": task_ids[2], "target_task_id": task_ids[3]},  # C -> D
            # Additional edge
            {"source_task_id": task_ids[3], "target_task_id": task_ids[4]},  # D -> E
        ]

        await self.backend.add_edges(dag_id, edges)
        stored_edges = await self.backend.get_all_edges(dag_id)

        self.assertEqual(len(stored_edges), 5)
        # Verify each edge is stored correctly
        stored_edge_set = {(src, tgt) for src, tgt in stored_edges}
        expected_edge_set = {(edge["source_task_id"], edge["target_task_id"]) for edge in edges}
        self.assertEqual(stored_edge_set, expected_edge_set)

    async def test_replace_existing_edges(self):
        """Test that adding edges to the same DAG replaces existing edges."""
        dag_id = str(uuid.uuid4())
        task_id_1 = str(uuid.uuid4())
        task_id_2 = str(uuid.uuid4())
        task_id_3 = str(uuid.uuid4())

        # Add initial edge
        edges = [{"source_task_id": task_id_1, "target_task_id": task_id_2}]
        await self.backend.add_edges(dag_id, edges)

        # Add new edge with same source but different target
        new_edges = [{"source_task_id": task_id_1, "target_task_id": task_id_3}]
        await self.backend.add_edges(dag_id, new_edges)

        stored_edges = await self.backend.get_all_edges(dag_id)
        self.assertEqual(len(stored_edges), 1)
        self.assertEqual(stored_edges[0], (task_id_1, task_id_3))

    def test_database_type_detection(self):
        """Test that database types are correctly detected from connection strings."""
        # SQLite
        backend = DagDatabaseBackend("sqlite:///test.db")
        self.assertFalse(backend._is_mysql)
        self.assertFalse(backend._is_postgresql)

        # MySQL
        backend = DagDatabaseBackend("mysql://user:pass@localhost/db")
        self.assertTrue(backend._is_mysql)
        self.assertFalse(backend._is_postgresql)

        # PostgreSQL
        backend = DagDatabaseBackend("postgresql://user:pass@localhost/db")
        self.assertFalse(backend._is_mysql)
        self.assertTrue(backend._is_postgresql)

    def test_id_column_type(self):
        """Test that correct ID column types are returned for different databases."""
        # SQLite
        backend = DagDatabaseBackend("sqlite:///test.db")
        self.assertEqual(backend._get_id_column_type(), "VARCHAR(36)")

        # MySQL
        backend = DagDatabaseBackend("mysql://user:pass@localhost/db")
        self.assertEqual(backend._get_id_column_type(), "VARCHAR(36)")

        # PostgreSQL
        backend = DagDatabaseBackend("postgresql://user:pass@localhost/db")
        self.assertEqual(backend._get_id_column_type(), "UUID")

    async def test_upsert_version_mysql(self):
        """Test that upsert version uses correct syntax for MySQL."""
        backend = DagDatabaseBackend("mysql://user:pass@localhost/db")
        
        # Mock the database execute method
        backend._database.execute = mock.AsyncMock()
        
        # Call upsert version
        test_dag_id = str(uuid.uuid4())
        await backend._upsert_version(test_dag_id)
        
        # Verify the SQL contains MySQL-specific syntax
        call_args = backend._database.execute.call_args
        self.assertIn("ON DUPLICATE KEY UPDATE", call_args[1]["query"])
        self.assertEqual(call_args[1]["values"]["dag_id"], test_dag_id)

    async def test_upsert_version_postgresql(self):
        """Test that upsert version uses correct syntax for PostgreSQL."""
        backend = DagDatabaseBackend("postgresql://user:pass@localhost/db")
        
        # Mock the database execute method
        backend._database.execute = mock.AsyncMock()
        
        # Call upsert version
        test_dag_id = str(uuid.uuid4())
        await backend._upsert_version(test_dag_id)
        
        # Verify the SQL contains PostgreSQL-specific syntax
        call_args = backend._database.execute.call_args
        self.assertIn("ON CONFLICT", call_args[1]["query"])
        self.assertEqual(call_args[1]["values"]["dag_id"], test_dag_id)

    async def test_initialize_database_postgresql(self):
        """Test that database initialization uses correct types for PostgreSQL."""
        backend = DagDatabaseBackend("postgresql://user:pass@localhost/db")
        
        # Mock the database execute method
        backend._database.execute = mock.AsyncMock()
        
        # Call initialize database
        await backend._initialize_database()
        
        # Verify the table creation SQL contains UUID type
        calls = backend._database.execute.call_args_list
        create_table_call = next(call for call in calls if "CREATE TABLE" in call[1]["query"])
        self.assertIn("UUID", create_table_call[1]["query"])
