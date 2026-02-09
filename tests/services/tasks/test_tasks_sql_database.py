# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import tempfile
from unittest import IsolatedAsyncioTestCase

from sqlite3 import OperationalError

from nv.svc.farm.sql import SqlDatabase


class TestSqliteDatabaseFacility(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self._sanitized_temp_dir_path = self._temp_dir.name.replace("\\", "/")
        self._database = SqlDatabase(self._generate_database_file("temp.db"))
        await self._database.connect()

    async def asyncTearDown(self) -> None:
        await self._database.disconnect()
        self._temp_dir = None

    def _generate_database_file(self, filename: str) -> str:
        return f"sqlite:///{self._sanitized_temp_dir_path}/{filename}"

    async def test_a_sqllite_database_is_identified_as_such(self) -> None:
        self.assertTrue(self._database.is_sqlite, "Expected database to be identified as SQLite.")
        self.assertFalse(self._database.is_postgresql, "Expected database not to be identified as PostgreSQL.")
        self.assertFalse(self._database.is_mysql, "Expected database not to be identified as MySQL.")

    async def test_a_connected_database_has_an_appropriate_flag(self) -> None:
        self.assertTrue(self._database.is_connected)

    async def test_a_disconnected_database_has_an_appropriate_flag(self) -> None:
        await self._database.disconnect()
        self.assertFalse(self._database.is_connected)

    async def test_a_connection_is_closed_after_exiting_a_scoped_context(self) -> None:
        db_reference: SqlDatabase = None

        async with SqlDatabase(self._generate_database_file("context_manager.db")) as context_db:
            db_reference = context_db

            # Validate that the database is connected before exiting the scope of the context:
            self.assertTrue(db_reference.is_connected)

        # Validate that the database is disconnected after exiting the scope of the context:
        self.assertIsNotNone(db_reference)
        self.assertFalse(db_reference.is_connected)

    async def test_creating_a_valid_table_does_not_raise_an_error(self) -> None:
        query = "CREATE TABLE TestTable (id INTEGER PRIMARY KEY)"
        await self._database.execute(query=query)

    async def test_an_invalid_query_raises_an_error(self) -> None:
        with self.assertRaises(OperationalError):
            query = "!!! PURPOSEFULLY INVALID SQL !!!"
            await self._database.execute(query=query)

    async def test_inserting_values_into_a_table_does_not_raise_an_error(self) -> None:
        # Create a table:
        query = "CREATE TABLE TestTable (id INTEGER PRIMARY KEY, symbol VARCHAR(16), value INTEGER)"
        await self._database.execute(query=query)

        # Attempt to insert data into the newly-created table:
        query = "INSERT INTO TestTable (symbol, value) VALUES (:symbol, :value)"
        values = [
            {"symbol": "Loneliest number", "value": 1},
            {"symbol": "Answer to life", "value": 42},
        ]
        await self._database.execute_many(query=query, values=values)

        # Attempt to read back the newly-inserted data:
        query = "SELECT * FROM TestTable"
        rows = await self._database.fetch_all(query=query)
        self.assertEqual(len(rows), len(values))
