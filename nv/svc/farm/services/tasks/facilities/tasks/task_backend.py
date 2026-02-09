# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Database persistence for Task information."""

import asyncio
import datetime
import json
import logging
import uuid

from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Mapping

from ..database.manager import BaseDatabase, DatabaseManagerFacility
from .....sql import SqlDatabase
from .backends import BaseTaskBackend, InvalidTaskFieldException
from nv.svc.farm.services.tasks.utils import status_utils
from .task_revision import TaskRevision


# Fields that can be selected for when listing all tasks. This is meant to
# prevent SQL injection attacks while keeping the payload low for clients
# that are only interested in a subset of data. Setting a field to false
# or not including it in this list will prevent including that field when
# the filter field is being used.
SELECTABLE_FIELDS = {
    "task_id": True,
    "task_type": True,
    "task_args": True,
    "task_function": True,
    "task_function_args": True,
    "task_requirements": True,
    "task_status": True,
    "user_id": True,
    "task_comment": True,
    "task_details": True,
    "task_metrics": True,
    "task_progress": True,
    "task_submission_time": True,
    "priority": True,
    "metadata": True,
    "labels": True
}

# The minimum fields to retrieve and serialize to an API caller if field filtering is enabled.
MINIMUM_FIELDS = [
    "task_id",
    "task_type",
    "task_function",
    "task_status",
    "task_submission_time",
    "priority"
]


def _get_utc_unixtime() -> float:
    """Return the current time as a unix epoch timestamp in the UTC timezone."""
    return datetime.datetime.utcnow().timestamp()


def lock_database_transaction(function: Callable) -> Callable:
    """
    Support database transactions.

    Args:
        function (Callable): Function to execute within the scope of a database transaction.

    Returns:
        Callable: The given function, wrapped in the scope of a database transaction.

    """
    async def wrapper(*args, **kwargs) -> Any:
        database_backend: "TaskDatabaseBackend" = args[0]
        async with database_backend.lock_transaction():
            return await function(*args, **kwargs)
    return wrapper


class TaskDatabaseBackend(BaseTaskBackend):
    """
    Database persistence for Task information.

    The business rules implemented for the CRUD operations of this module are following the ones defined in
    ``TaskIdDictBackend``.

    """

    def __init__(self, database_handle: str) -> None:
        """
        Task database backend constructor.

        Args:
            database_handle (str): Handle of the database to use when performing queries against the database.

        Returns:
            None

        """
        super().__init__()

        self._database_facility: DatabaseManagerFacility = DatabaseManagerFacility()
        self._database_handle: str = database_handle

        self._task_table_name: str = "Tasks"
        self._task_table_index_name: str = "TasksIndex"
        self._task_revision_history_table_name: str = "TaskRevisions"
        self._task_revision_history_index_name: str = "TaskRevisionsIndex"
        self._database_ready = None

    async def start(self):
        self._database_ready = await self._initialize_database()

    async def database_ready(self):
        if self._database_ready is None:
            self._database_ready = asyncio.ensure_future(self._initialize_database())
        return self._database_ready

    def __del__(self) -> None:
        """Handle when the object is deleted."""
        if self._database_ready:
            self._database_ready.cancel()
            self._database_ready = None

    @lock_database_transaction
    async def _initialize_database(self):
        """
        Initialize the database schema(s).

        This includes:
          * Creating a table to store Tasks, if none already exists.
          * Adding foreign keys, if necessary.
          * Adding integrity or cascading clauses, if necessary.
          * Performing database migration steps, if any is needed.
          * etc.

        .. todo::

            Specify length of the various fields based on a more structured, normalized model schema. The size of the
            fields provided here are somewhat arbitrary, and may not match the capabilities of other storage options.

            For example, in-memory backend storage options do not enforce size limitations on any fields, which can
            cause the same API call to fail or succeed based on the size of the request and the storage option being
            used (on top of being a denial-of-service issue in the case of in-memory storage).

            Defining models using ``pydantic`` and sharing fields used by models as part of a ``TaskModel`` Extension
            would benefit extensibility, and ensure stronger feature cohesion across the ecosystem.

        """
        # Determine the schema of the underlying database being used, in order to format the appropriate database
        # queries.
        #
        # TODO: Reconsider using SQLAlchemy in order to abstract away SQL queries, in order to facilitate composition of
        # SQL operations:
        is_mysql_database = False
        is_postgresql_database = False
        is_sqlite_database = False
        async with self._database_facility.get(self._database_handle) as db:
            if isinstance(db, SqlDatabase):
                is_mysql_database = db.is_mysql
                is_postgresql_database = db.is_postgresql
                is_sqlite_database = db.is_sqlite

        # Database directive tokens, based on the specific target dialect.
        AUTO_INCREMENT_TOKEN = ""
        if is_sqlite_database:
            AUTO_INCREMENT_TOKEN = "AUTOINCREMENT"
        elif is_mysql_database:
            AUTO_INCREMENT_TOKEN = "AUTO_INCREMENT"
        elif is_postgresql_database:
            AUTO_INCREMENT_TOKEN = "SERIAL"

        # Define table column characteristics:
        table_columns = [
            "task_id VARCHAR(36) PRIMARY KEY",
            "task_type VARCHAR(512)",
            "task_args VARCHAR(4096)",
            "task_function VARCHAR(128)",
            "task_function_args TEXT(4096)",
            "task_requirements TEXT(4096)",
            "task_status VARCHAR(32)",
            "user_id VARCHAR(2048)",
            "task_comment MEDIUMTEXT",
            "task_details MEDIUMTEXT",
            "task_metrics LONGTEXT",
            "task_progress LONGTEXT",
            "task_submission_time INTEGER",
            "priority INTEGER",
            "metadata LONGTEXT",
            "labels VARCHAR(2048)",
        ]
        query = f"CREATE TABLE IF NOT EXISTS {self._task_table_name} ({', '.join(table_columns)});"

        async with self._database_facility.get(self._database_handle) as db:
            await db.execute(query=query)

        # Task index:
        try:
            if is_mysql_database:
                await self._create_mysql_task_table_index()
            else:
                await self._create_task_table_index()
        except Exception as exc:
            logging.warning(
                f"Unable to create table index for Tasks of database handle \"{self._database_handle}\": {str(exc)}"
            )

        # Task revision history:
        table_columns = [
            f"revision_id INTEGER PRIMARY KEY {AUTO_INCREMENT_TOKEN}",
            "task_id VARCHAR(36)",
            "task_status VARCHAR(32)",
            "task_user_id VARCHAR(2048)",
            "task_agent_id VARCHAR(2048)",
            "task_details LONGTEXT",
            "task_progress LONGTEXT",
            "time REAL",
            f"""
                CONSTRAINT fk_tasks
                    FOREIGN KEY (task_id)
                    REFERENCES {self._task_table_name}(task_id)
                    ON DELETE CASCADE
            """,
        ]
        query = f"CREATE TABLE IF NOT EXISTS {self._task_revision_history_table_name} ({', '.join(table_columns)});"

        async with self._database_facility.get(self._database_handle) as db:
            await db.execute(query=query)

        # Task revision history index:
        try:
            if is_mysql_database:
                await self._create_mysql_task_revisions_index()
            else:
                await self._create_task_revisions_index()
        except Exception as exc:
            logging.warning(
                f"Unable to create table index for Task Revisions of database handle \"{self._database_handle}\": {str(exc)}"
            )

    async def _create_mysql_task_table_index(self) -> None:
        """Create the Tasks index in MySQL, emulating IF NOT EXISTS."""
        async with self._database_facility.get(self._database_handle) as db:
            show_idx_query = (
                f"SHOW INDEX FROM {self._task_table_name} WHERE Key_name = '{self._task_table_index_name}'"
            )
            rows = await db.fetch_all(query=show_idx_query)
            if rows:
                return
            create_idx_query = (
                f"CREATE INDEX {self._task_table_index_name} "
                f"ON {self._task_table_name} (task_type, task_function, task_status)"
            )
            await db.execute(query=create_idx_query)

    async def _create_task_table_index(self) -> None:
        """Create the Tasks index for databases supporting IF NOT EXISTS (e.g., PostgreSQL, SQLite)."""
        query = (
            f"CREATE INDEX IF NOT EXISTS {self._task_table_index_name} "
            f"ON {self._task_table_name} (task_type, task_function, task_status);"
        )
        async with self._database_facility.get(self._database_handle) as db:
            await db.execute(query=query)

    async def _create_mysql_task_revisions_index(self) -> None:
        """Create the TaskRevisions index in MySQL, emulating IF NOT EXISTS."""
        async with self._database_facility.get(self._database_handle) as db:
            show_idx_query = (
                f"SHOW INDEX FROM {self._task_revision_history_table_name} "
                f"WHERE Key_name = '{self._task_revision_history_index_name}'"
            )
            rows = await db.fetch_all(query=show_idx_query)
            if rows:
                return
            create_idx_query = (
                f"CREATE INDEX {self._task_revision_history_index_name} "
                f"ON {self._task_revision_history_table_name} (task_id)"
            )
            await db.execute(query=create_idx_query)

    async def _create_task_revisions_index(self) -> None:
        """Create the TaskRevisions index for databases supporting IF NOT EXISTS."""
        query = (
            f"CREATE INDEX IF NOT EXISTS {self._task_revision_history_index_name} "
            f"ON {self._task_revision_history_table_name} (task_id);"
        )
        async with self._database_facility.get(self._database_handle) as db:
            await db.execute(query=query)

    async def get_task(
        self,
        task_id: str = None,
        task_type: str = None,
        task_function: str = None,
    ):
        values = {}
        if task_id:
            values["task_id"] = task_id
        if task_type:
            values["task_type"] = task_type
        if task_function:
            values["task_function"] = task_function

        column_names = list(values.keys())
        search_query = " AND ".join([f"{col} = :{col}" for col in column_names])
        query = f"""
            SELECT *
            FROM {self._task_table_name}
            WHERE {search_query}
            ORDER BY priority ASC, task_submission_time ASC
        """

        async with self._database_instance() as db:
            rows = await db.fetch_all(query=query, values=values)
            if not rows:
                raise KeyError(f"{task_id} not found for ({task_type}, {task_function})")

            return self._create_task_from_database_row(rows[0])

    async def get_next_task_prioritised(
        self,
        task_keys: List[Tuple],
        agent_id: str,
        capacity: Optional[Dict] = None,
        labels: Optional[List] = None
    ) -> Optional[Dict[str, Any]]:
        self.validate_labels(labels)

        search_query = ""

        queries = []
        for task_type, task_function in task_keys:
            or_query = f'(task_type="{task_type}" AND task_function="{task_function}")'
            queries.append(or_query)

        labels = labels or []
        if not isinstance(labels, list):
            logging.warning(f"Passed through labels are not a list: {labels}, {type(labels)}")
            labels = []

        labels = ",".join(labels)

        # TODO: double check for potential SQL injection possibilities.
        search_query = f'task_status="submitted" AND labels="{labels}"'
        if queries:
            search_query += " AND ("
            search_query += " OR ".join(queries)
            search_query += ")"

        query = f"""
            SELECT *
            FROM {self._task_table_name}
            WHERE {search_query}
            ORDER BY priority ASC, task_submission_time ASC
            LIMIT 1
        """

        async with self._database_instance() as db:
            query = query + " FOR UPDATE SKIP LOCKED" if not db.is_sqlite else query

            async with db._database.connection() as conn:
                async with conn.transaction():
                    row: Optional[Mapping[str, Any]] = await db._database.fetch_one(query=query)
                    if not row:
                        return None

                    task_id = row["task_id"]
                    task_type = row["task_type"]
                    task_function = row["task_function"]

                    fields_to_set = {
                        "task_status": "starting",
                    }

                    query_tokens = ", ".join([f"{f} = :{f}" for f in fields_to_set])
                    where_clause = {
                        "task_id": task_id,
                    }
                    values = {
                        **fields_to_set,
                        **where_clause,
                    }
                    query = f"UPDATE {self._task_table_name} SET {query_tokens} WHERE task_id = :task_id"
                    await db._database.execute(query=query, values=values)

                    return self._create_task_from_database_row(row)

    def _construct_for_in(self, column_name: str, column_names: List[str], values: List[str]):
        column_names.append("task_status")
        formatted_status_enums = [f'"{x}"' for x in values]
        search_query = f" {column_name} in ({', '.join(formatted_status_enums)})"
        return column_names, search_query

    async def get_tasks(
        self,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        capacity: Optional[Dict] = None,
        statuses: List[str] = None,
        fields: Optional[List[str]] = None
    ) -> List:
        values = {}
        if task_type is not None:
            values["task_type"] = task_type
        if task_function is not None:
            values["task_function"] = task_function

        column_names = list(values.keys())
        search_query = " AND ".join([f"{col} = :{col}" for col in column_names])

        if statuses is None:
            statuses = [status_utils.Status.submitted.value]

        # Unfortunately, the PIP `databases` package does not support SQLite's `WHERE ... IN` syntax, which forces using
        # the following workaround (see issue https://github.com/encode/databases/issues/166):
        if statuses:
            # Ensure Users are not trying to "inadvertently" perform SQL injections:
            validated_statuses: List[str] = []
            for status in statuses:
                candidate_status = status_utils.Status(status)
                if isinstance(candidate_status, status_utils.Status):
                    validated_statuses.append(status)
                else:
                    logging.error(f"Attempted to get task with unknown status \"{status}\".")

            if validated_statuses:
                column_names, query = self._construct_for_in(
                    column_name="task_status",
                    column_names=column_names,
                    values=validated_statuses
                )
                if search_query:
                    search_query += f" AND"  # noqa
                search_query += query

        # Default to retrieving all fields.
        field_names = "*"

        if fields is not None:
            # If a set of fields was provided to minimize the return payload, then validate and
            # select only those columns.
            complete_fields = set(fields + MINIMUM_FIELDS)
            validated_fields: List[str] = [field for field in complete_fields if SELECTABLE_FIELDS.get(field, False)]
            difference = complete_fields - set(validated_fields)

            # Handle any unknown fields by raising an exception.
            if len(difference) != 0:
                raise InvalidTaskFieldException(f"Invalid fields {difference}")

            field_names = ", ".join(validated_fields)

        query = f"""
            SELECT {field_names}
            FROM {self._task_table_name}
            {'WHERE' if search_query else ''} {search_query}
            ORDER BY priority ASC, task_submission_time ASC
            """

        async with self._database_instance() as db:
            rows: List[Mapping[str, Any]] = await db.fetch_all(query=query, values=values)
            tasks = [self._create_task_from_database_row(row) for row in rows]
            return tasks

    async def get_task_revision_history(self, task_id: str,) -> List[TaskRevision]:
        query = f"SELECT * FROM {self._task_revision_history_table_name} WHERE task_id = :task_id ORDER BY time ASC"
        values = {
            "task_id": task_id,
        }

        async with self._database_instance() as db:
            rows: List[Mapping[str, Any]] = await db.fetch_all(query=query, values=values)

            task_revision_history = [self._create_task_revision_history_from_database_row(row) for row in rows]
            return task_revision_history

    async def update_task(
        self,
        task_id: str,
        userid: str,
        task_type: Optional[str] = None,
        task_function: Optional[str] = None,
        status: Optional[str] = None,
        details: Optional[str] = None,
        metrics: Optional[str] = None,
        progress: Optional[Dict] = None,
        agent_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_function_args: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None,
    ):
        self.validate_labels(labels)

        fields_to_set = {}

        if task_type:
            fields_to_set["task_type"] = task_type
        if task_function:
            fields_to_set["task_function"] = task_function
        if status:
            fields_to_set["task_status"] = status
        if details:
            fields_to_set["task_details"] = details
        if metrics:
            fields_to_set["task_metrics"] = metrics
        if progress:
            fields_to_set["task_progress"] = json.dumps(progress)
        if task_comment:
            fields_to_set["task_comment"] = task_comment
        if task_function_args:
            fields_to_set["task_function_args"] = json.dumps(task_function_args)
        if priority:
            fields_to_set["priority"] = priority
        if metadata:
            fields_to_set["metadata"] = json.dumps(metadata)
        if labels and isinstance(labels, list):
            fields_to_set["labels"] = ",".join(labels)

        query_tokens = ", ".join([f"{f} = :{f}" for f in fields_to_set])
        where_clause = {
            "task_id": task_id,
        }
        values = {
            **fields_to_set,
            **where_clause,
        }
        query = f"UPDATE {self._task_table_name} SET {query_tokens} WHERE task_id = :task_id"

        if status in (status_utils.Status.running.value, status_utils.Status.starting.value):
            # Prevent race condition from updating a finished task back to running.
            values["finished_status"] = status_utils.Status.finished.value
            values["errored_status"] = status_utils.Status.errored.value
            query = " ".join((query, "AND task_status != :finished_status AND task_status != :errored_status"))

        async with self._database_instance() as db:
            updated_rows = await db.execute(query=query, values=values)

        if updated_rows > 0:
            await self._save_task_revision(
                TaskRevision(
                    task_id=task_id,
                    status=status,
                    userid=userid,
                    agent_id=agent_id,
                    details=details,
                    progress=progress,
                )
            )

    async def _save_task(
        self,
        status: str,
        task_type: str,
        userid: str,
        task_args: Optional[Dict] = None,
        task_function: Optional[str] = None,
        task_function_args: Optional[Dict] = None,
        task_requirements: Optional[Dict] = None,
        task_id: Optional[str] = None,
        task_comment: Optional[str] = None,
        task_submission_time: Optional[int] = None,
        priority: Optional[int] = None,
        metadata: Optional[Dict] = None,
        labels: Optional[List] = None,
    ) -> str:
        self.validate_labels(labels)

        task_id = task_id or str(uuid.uuid4())
        values = {
            "task_id": task_id,
            "task_type": task_type,
            "task_args": json.dumps(task_args) if task_args else "{}",
            "task_function": task_function or "",
            "task_function_args": json.dumps(task_function_args) if task_function_args else "{}",
            "task_requirements": json.dumps(task_requirements) if task_requirements else "{}",
            "task_status": status,
            "user_id": userid,
            "task_comment": task_comment or "",
            "task_details": "",
            "task_metrics": "",
            "task_progress": "{}",
            "task_submission_time": task_submission_time or _get_utc_unixtime(),
            "priority": 65535 if priority is None else priority,
            "metadata": json.dumps(metadata) if metadata else "{}",
            "labels": ",".join(labels) if labels and isinstance(labels, list) else "",
        }

        item_keys = list(values.keys())
        row_names = ', '.join(item_keys)
        row_values_tokens = ', '.join([f":{k}" for k in item_keys])
        query = f"INSERT INTO {self._task_table_name} ({row_names}) VALUES ({row_values_tokens})"

        async with self._database_instance() as db:
            await db.execute(query=query, values=values)

        return task_id

    async def _save_task_revision(self, task_revision: TaskRevision) -> None:
        update_id = None

        # get the revision id and status for the last revision posted for this task
        task_status_query = (f'SELECT revision_id, task_status, task_agent_id, task_user_id FROM '
                             f'{self._task_revision_history_table_name} WHERE '
                             f'task_id="{task_revision.task_id}" ORDER BY revision_id DESC LIMIT 1')
        async with self._database_instance() as db:
            row = await db._database.fetch_one(query=task_status_query)
            # if our new revision matches the old one, then we're going to update the existing row
            if row:
                # clean up the results from the database to better match our task_revision input
                # where the database will return '' for None fields and equality fails
                task_status = row[1] or None
                task_agent_id = row[2] or None
                task_user_id = row[3] or None
                if task_status == task_revision.status and \
                   task_agent_id == task_revision.agent_id and \
                   task_user_id == task_revision.user_id:
                    update_id = row[0]

        values = {
            "task_id": task_revision.task_id,
            "task_status": task_revision.status,
            "task_user_id": task_revision.user_id,
            "task_agent_id": task_revision.agent_id or "",
            "task_details": task_revision.details,
            "task_progress": json.dumps(task_revision.progress) if task_revision.progress else None,
            "time": _get_utc_unixtime(),
        }

        query: str = ""
        if update_id:
            setters = []
            for k in values.keys():
                setters.append(f'{k}=:{k}')
            set_str = ", ".join(setters)
            query = f'UPDATE {self._task_revision_history_table_name} SET {set_str} ' \
                    f'WHERE revision_id={update_id}'
        else:
            item_keys = list(values.keys())
            row_names = ', '.join(item_keys)
            row_values_tokens = ', '.join([f":{k}" for k in item_keys])
            query = f"INSERT INTO {self._task_revision_history_table_name} ({row_names}) VALUES ({row_values_tokens})"

        async with self._database_instance() as db:
            await db.execute(query=query, values=values)

    @asynccontextmanager
    async def _database_instance(self) -> Generator[BaseDatabase, None, None]:
        """
        Return an asynchronous context to the underlying database technology.

        Args:
            None

        Returns:
            Generator[BaseDatabase, Any, Any]: An ``await``-able response to the underlying database.

        """
        await self.database_ready()
        async with self._database_facility.get(self._database_handle) as db:
            yield db

    @asynccontextmanager
    async def lock_transaction(self) -> Generator[Any, None, None]:
        """
        Return an asynchronous context to perform a transaction using the underlying database technology.

        in order to support rolling back a query in case of failure, and to handle concurrent resource access. Should the underlying
        database technology not support transactions, the implementation will fall back to an ``asyncio.Lock``.

        Args:
            None

        Returns:
            Generator[Any, None, None]: An ``await``-able response to a database transaction.

        """
        async with self._database_facility.get(self._database_handle) as db:
            async with db.transaction(isolation="serializable"):
                yield

    def _create_task_from_database_row(self, row: Mapping[str, Any]) -> Dict[str, Any]:
        """
        Convert the given database row into a task model.

        Args:
            row (Tuple): Row information about the task to convert as returned by encode/databases' fetch_one method as
            Mapping type.

        Returns:
            Dict: The task model converted from the given database row.

        """
        row = dict(row)
        row_mutated: Dict[str, Any] = {
            "task_id": row["task_id"],
            "task_type": row["task_type"],
            "task_args": json.loads(row["task_args"]) if "task_args" in row else None,
            "task_function": row["task_function"],
            "task_function_args": json.loads(row["task_function_args"]) if "task_function_args" in row else None,
            "task_requirements": json.loads(row["task_requirements"]) if "task_requirements" in row else None,
            "status": row["task_status"],
            "userid": row["user_id"] if "user_id" in row else None,
            "task_comment": row["task_comment"] if "task_comment" in row else None,
            "task_details": row["task_details"] if "task_details" in row else None,
            "metrics": row["task_metrics"] if "task_metrics" in row else None,
            "progress": json.loads(row["task_progress"]) if "task_progress" in row else None,
            "task_submission_time": row["task_submission_time"],
            "priority": row["priority"],
            "metadata": json.loads(row["metadata"]) if "metadata" in row else None,
            "labels": list(filter(None, row['labels'].split(","))) if "labels" in row and row['labels'] is not None else []
        }

        return row_mutated

    def _create_task_revision_history_from_database_row(self, row: Mapping[str, Any]) -> TaskRevision:
        """
        Convert the given database row into a task revision model.

        Args:
            row (Tuple): Row information about the task revision to convert.

        Returns:
            Dict: The task revision model converted from the given database row.

        """
        # Converting to dict so we can use "if ... in".
        row = dict(row)
        return TaskRevision(
            revision_id=row["revision_id"],
            task_id=row["task_id"],
            status=row["task_status"],
            userid=row["task_user_id"],
            agent_id=row["task_agent_id"],
            details=row["task_details"],
            progress=json.loads(row["task_progress"]) if row["task_progress"] else None,
            time=row["time"],
        )

    async def get_highest_task_revision(self) -> Optional[int]:
        """See base class."""

        query = f"SELECT revision_id FROM {self._task_revision_history_table_name} ORDER BY revision_id DESC LIMIT 1"

        async with self._database_facility.get(self._database_handle) as db:
            row: Optional[Mapping[str, Any]] = await db._database.fetch_one(query=query)
            if row:
                return row["revision_id"]

        return None

    async def get_changed_tasks_between_revisions(self, after: int, ending_with: int) -> List[str]:
        """See base class."""

        query = f"SELECT DISTINCT task_id FROM {self._task_revision_history_table_name} WHERE revision_id > :after AND revision_id <= :ending_with"
        values = {"after": after, "ending_with": ending_with}

        matching_task_ids: List[str] = []

        async with self._database_facility.get(self._database_handle) as db:
            rows: List[Mapping[str, Any]] = await db._database.fetch_all(query=query, values=values)
            for row in rows:
                matching_task_ids.append(row["task_id"])

        return matching_task_ids

    async def get_tasks_bulk(
        self,
        task_ids: List[str],
        statuses: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get multiple tasks by their IDs.

        Args:
            task_ids (List[str]): List of task IDs to retrieve.
            statuses (Optional[List[str]]): Optional list of statuses to filter by.

        Returns:
            List[Dict[str, Any]]: List of task dictionaries.
        """
        # Build the query with database-agnostic parameterization for IN clause
        task_id_params = {f"task_id_{i}": task_id for i, task_id in enumerate(task_ids)}
        placeholders = ','.join([f":task_id_{i}" for i in range(len(task_ids))])
        search_query = f"SELECT * FROM {self._task_table_name} WHERE task_id IN ({placeholders})"
        values = task_id_params

        if statuses:
            status_params = {f"status_{i}": status for i, status in enumerate(statuses)}
            status_placeholders = ','.join([f":status_{i}" for i in range(len(statuses))])
            search_query += f" AND task_status IN ({status_placeholders})"
            values.update(status_params)

        # Execute the query
        async with self._database_instance() as db:
            rows = await db.fetch_all(query=search_query, values=values)
            return [self._create_task_from_database_row(row) for row in rows]

    async def update_tasks_status_bulk(
        self,
        task_ids: List[str],
        new_status: str,
    ) -> List[str]:
        """Update the status of multiple tasks atomically.

        Args:
            task_ids: List of task IDs to update.
            new_status: The new status to set.

        Returns:
            List of task IDs that were actually updated.
        """
        async with self._database_facility.get(self._database_handle) as db:
            # Start a transaction
            async with db.transaction():
                # Build the placeholders for the task IDs
                placeholders = ",".join([":id_" + str(i) for i in range(len(task_ids))])

                # Build the base query
                select_query = f"SELECT task_id FROM {self._task_table_name} WHERE task_id IN ({placeholders})"

                # Add task IDs to values
                select_values = {f"id_{i}": task_id for i, task_id in enumerate(task_ids)}

                # Get the IDs of tasks that match our criteria
                rows = await db._database.fetch_all(query=select_query, values=select_values)
                matching_ids = [row["task_id"] for row in rows]

                if not matching_ids:
                    return []

                # Build the update query for the matching tasks
                update_placeholders = ",".join([":update_id_" + str(i) for i in range(len(matching_ids))])
                update_query = f"UPDATE {self._task_table_name} SET task_status = :new_status WHERE task_id IN ({update_placeholders})"

                # Build the values for the update
                update_values = {
                    "new_status": new_status,
                    **{f"update_id_{i}": task_id for i, task_id in enumerate(matching_ids)}
                }

                # Execute the update
                await db._database.execute(query=update_query, values=update_values)

        # Save revision history for each updated task
        for task_id in matching_ids:
            await self._save_task_revision(
                TaskRevision(
                    task_id=task_id,
                    status=new_status,
                    userid="system",
                    details="Status updated as part of bulk update",
                )
            )

        return matching_ids
