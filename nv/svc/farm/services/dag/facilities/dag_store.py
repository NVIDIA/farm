# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm DAG Store Facility."""

from typing import Dict, List, Set, Tuple, Optional
import logging
import asyncio
import networkx as nx
from networkx.exception import NetworkXError
from enum import Enum

from nv.svc.core.facilities import base
from nv.svc.farm.services.tasks.utils import status_utils
from nv.svc.farm.utils import post_data, fetch_data

from .dag_backend import BaseDagBackend

logger = logging.getLogger(__name__)


class DependencyResolutionStrategy(Enum):
    """Enum for dependency resolution strategies in DAG metadata."""

    on_success = "on_success"
    always_run = "always_run"


class DAGStore(base.Facility):
    """Facility for managing DAG (Directed Acyclic Graph) operations."""

    def __init__(self, backend: BaseDagBackend, task_service_url: str):
        """Initialize the DAG store.

        Args:
            backend: Backend for storing DAG data
            task_service_url: URL of the task service
        """
        self._backend = backend
        self._task_service_url = task_service_url.rstrip('/')
        self._task_info_endpoint = f"{self._task_service_url}/info"
        self._update_task_endpoint = f"{self._task_service_url}/update"
        self._bulk_update_task_endpoint = f"{self._task_service_url}/update/bulk"
        self._bulk_task_info_endpoint = f"{self._task_service_url}/info/bulk"

    async def start(self) -> None:
        """Start the DAG store facility."""
        await self._backend.start()

    async def stop(self) -> None:
        """Stop the DAG store facility."""
        await self._backend.stop()

    async def _get_task_info(self, task_id: str) -> Dict:
        """Get task information from the task service.

        Args:
            task_id: ID of the task to get info for

        Returns:
            Dict containing task information including status
        """
        try:
            return await fetch_data(f"{self._task_info_endpoint}/{task_id}")
        except Exception as e:
            logging.error(f"Failed to get task info for {task_id}: {str(e)}")
            return None

    async def _get_bulk_task_info(self, task_ids: List[str]) -> Dict:
        """Get bulk task info from the task service.

        Args:
            task_ids: List of task IDs to get info for

        Returns:
            Dict containing task information including status
        """
        try:
            bulk_task_info = await post_data(self._bulk_task_info_endpoint, data={"task_ids": task_ids})
            return bulk_task_info.get("tasks", {})
        except Exception as e:
            logging.error(f"Failed to get bulk task info for {task_ids}: {str(e)}")
            return {}

    async def _update_task_status(self, task_id: str, status: status_utils.Status, task_info: Dict = None) -> None:
        """Update task status in the task service.

        Args:
            task_id: ID of the task to update
            status: New status to set
            task_info: Optional task info to avoid duplicate API calls
        """
        try:
            if task_info is None:
                task_info = await self._get_task_info(task_id)
            if not task_info:
                return

            await post_data(
                self._update_task_endpoint,
                data={
                    "task_id": task_id,
                    "task_type": task_info["task_type"],
                    "task_function": task_info["task_function"],
                    "status": status,
                    "userid": "system",
                    "details": "Task dependencies satisfied"
                }
            )
        except Exception as e:
            logging.error(f"Failed to update task {task_id} to status {status}: {str(e)}")

    async def _bulk_update_task_status(self, task_ids: List[str], status: status_utils.Status) -> None:
        """Update task status in the task service.

        Args:
            task_ids: List of task IDs to update
            status: New status to set
        """
        try:
            await post_data(
                self._bulk_update_task_endpoint,
                data={"task_ids": task_ids, "status": status}
            )
        except Exception as e:
            logging.error(f"Failed to update task {task_ids} to status {status}: {str(e)}")

    def _is_task_retrying(self, task_info: Dict) -> bool:
        """Check if a task is retrying.

        Args:
            task_info: Task info to check
        """
        retry_metadata = task_info.get("metadata", {}).get("_retry", {})
        is_retryable = retry_metadata.get("is_retryable", False)
        is_done = retry_metadata.get("is_done", False)
        return status_utils.is_task_errored(task_info) and is_retryable and not is_done

    def _are_tasks_retrying(self, tasks_info: List[Dict]) -> bool:
        """Check if any task is retrying.

        Args:
            tasks_info: List of task info to check

        Returns:
            bool: True if any task is retrying, False otherwise
        """
        return any(self._is_task_retrying(task_info) for task_info in tasks_info)

    def _get_dependency_resolution_strategy(
        self,
        task_dict: Dict,
        default: DependencyResolutionStrategy = DependencyResolutionStrategy.on_success
    ) -> DependencyResolutionStrategy:
        """Get the dependency resolution strategy from a task dict.

        Args:
            task_dict: Task dictionary containing metadata
            default: Default enum value to return if conversion fails

        Returns:
            DependencyResolutionStrategy enum instance
        """
        dag_metadata = task_dict.get("metadata", {}).get("dag", {})
        strategy_str = dag_metadata.get("dependency_resolution_strategy", default.value)
        try:
            return DependencyResolutionStrategy(strategy_str.lower())
        except ValueError:
            logger.warning(f"Invalid dependency resolution strategy {strategy_str}, using default {default.value}")
            return default

    async def handle_task_completion(self, task_info: Dict) -> None:
        """Handle completion of a task.

        This method:
        1. Gets the task's DAG ID from its metadata
        2. Finds all child tasks of this task
        3. For each child task, checks if all its parent tasks are complete
        4. If all parent tasks are complete, marks the child task as ready

        Args:
            task_id: The ID of the completed task
        """
        # Get task info to find its DAG ID
        task_id = task_info.get("task_id")
        dag_id = task_info.get("metadata", {}).get("dag", {}).get("id")

        if not dag_id:
            logger.error(f"Task {task_id} has no DAG ID in metadata")
            return

        if self._is_task_retrying(task_info):
            logger.info(f"Task {task_id} is retrying, skipping")
            return

        # Get all child tasks of this task
        child_task_ids = await self.get_task_children(dag_id, task_id)

        if not child_task_ids:
            logger.info(f"No child tasks found for {task_id}, nothing to process")
            return

        # For each child task, get its parent tasks
        child_task_dependency_ids = await asyncio.gather(*[
            self.get_task_parents(dag_id, child_task_id) for child_task_id in child_task_ids
        ])
        flat_child_task_dependency_ids = [item for sublist in child_task_dependency_ids for item in sublist]

        # Remove duplicates and the completed task
        task_ids = list(set(flat_child_task_dependency_ids) - {task_id}) + child_task_ids

        # Get info for all tasks in bulk
        bulk_task_info = await self._get_bulk_task_info(task_ids=task_ids)
        bulk_task_info[task_id] = task_info

        # zip data for ease of processing
        zipped_child_task_data = zip(child_task_ids, child_task_dependency_ids)

        # Track which child tasks are ready
        ready_tasks = {
            status_utils.Status.submitted.value: [],
            status_utils.Status.unschedulable.value: [],
        }

        for task_id, dependency_ids in zipped_child_task_data:
            task_dict = bulk_task_info.get(task_id, {})
            dependency_resolution_strategy = self._get_dependency_resolution_strategy(task_dict)
            dependencies = [bulk_task_info.get(dependency_id, {}) for dependency_id in dependency_ids]
            are_dependencies_retrying = self._are_tasks_retrying(dependencies)

            # skip processing for retrying dependencies
            if are_dependencies_retrying:
                continue

            # submit any task where all tasks have finished processing and dependency resolution strategy is on_success
            if status_utils.are_tasks_finished(dependencies) and dependency_resolution_strategy == DependencyResolutionStrategy.on_success:
                ready_tasks[status_utils.Status.submitted.value].append(task_id)
                continue

            are_tasks_processed = status_utils.are_tasks_processed(dependencies)
            # submit any task where all tasks have finished processing and dependency resolution strategy is always_run
            if are_tasks_processed and dependency_resolution_strategy == DependencyResolutionStrategy.always_run:
                ready_tasks[status_utils.Status.submitted.value].append(task_id)
            # skip processing of tasks where all tasks have finished processing
            elif are_tasks_processed:
                ready_tasks[status_utils.Status.unschedulable.value].append(task_id)

        # Update all ready tasks to submitted state in bulk
        status_updates = [self._bulk_update_task_status(task_ids=task_ids, status=status) for status, task_ids in ready_tasks.items() if task_ids]
        if status_updates:
            await asyncio.gather(*status_updates)

    def _build_graph(self) -> nx.DiGraph:
        """Build a directed graph from the edges in the store.

        Returns:
            A networkx DiGraph object
        """
        return nx.DiGraph()

    async def _build_graph_for_task(self, dag_id: str, task_id: str) -> nx.DiGraph:
        """Build a graph containing the task and its relationships.

        Args:
            dag_id: ID of the DAG containing the task
            task_id: ID of the task

        Returns:
            nx.DiGraph: The graph containing the task and its relationships
        """
        edges = await self._backend.get_all_edges(dag_id)
        if not edges:
            return nx.DiGraph()

        graph = nx.DiGraph()

        # First pass: add all edges to find connected components
        for source_id, target_id in edges:
            graph.add_edge(source_id, target_id)

        # If task_id isn't in graph, return empty graph
        if task_id not in graph:
            return nx.DiGraph()

        # Find the connected component containing our task
        component = nx.node_connected_component(graph.to_undirected(), task_id)

        # Create a new graph with just this component
        return graph.subgraph(component).copy()

    async def add_graph(self, dag_id: str, edges: List[Dict[str, str]], name: Optional[str] = None) -> None:
        """Add a task dependency graph.

        Args:
            dag_id: Unique identifier for the DAG
            edges: List of edges defining task dependencies
                  Each edge is a dict with source_task_id and target_task_id
            name: Optional name for the DAG (for display purposes)

        Raises:
            ValueError: If the graph contains cycles
        """
        # Create a directed graph
        graph = nx.DiGraph()

        # Add all edges
        for edge in edges:
            source = edge["source_task_id"]
            target = edge["target_task_id"]
            graph.add_edge(source, target)

        # Check for cycles
        try:
            nx.find_cycle(graph)
            raise ValueError("Task graph contains cycles")
        except nx.NetworkXNoCycle:
            pass

        # Store the graph
        await self._backend.add_edges(dag_id, edges, name)

    async def get_task_parents(self, dag_id: str, task_id: str) -> List[str]:
        """Get IDs of tasks that this task depends on.

        Args:
            dag_id: ID of the DAG
            task_id: ID of the task

        Returns:
            List of task IDs that are dependencies of this task
        """
        edges = await self._backend.get_all_edges(dag_id)
        if not edges:
            return []

        graph = nx.DiGraph()
        for source, target in edges:
            graph.add_edge(source, target)

        try:
            return list(graph.predecessors(task_id))
        except NetworkXError:
            return []

    async def get_task_children(self, dag_id: str, task_id: str) -> List[str]:
        """Get IDs of tasks that depend on this task.

        Args:
            dag_id: ID of the DAG
            task_id: ID of the task

        Returns:
            List of task IDs that depend on this task
        """
        edges = await self._backend.get_all_edges(dag_id)
        if not edges:
            return []

        graph = nx.DiGraph()
        for source, target in edges:
            graph.add_edge(source, target)
            # Also add nodes without edges to handle isolated tasks
            graph.add_node(source)
            graph.add_node(target)

        try:
            return list(graph.successors(task_id))
        except NetworkXError:
            return []

    async def get_subgraph_tasks(self, dag_id: str, task_id: str) -> Set[str]:
        """Get all tasks that are descendants of the given task.

        Args:
            dag_id: ID of the DAG
            task_id: ID of the task to start from

        Returns:
            Set of task IDs that are descendants of the given task
        """
        edges = await self._backend.get_all_edges(dag_id)
        if not edges:
            return {task_id}

        graph = nx.DiGraph()
        for source, target in edges:
            graph.add_edge(source, target)

        try:
            descendants = nx.descendants(graph, task_id)
            return descendants
        except NetworkXError:
            return {task_id}

    async def delete_dag(self, dag_id: str) -> None:
        """Delete a DAG and all its edges.

        Args:
            dag_id: ID of the DAG to delete
        """
        # Delete from backend first
        await self._backend.delete_dag(dag_id)

        # Clear any in-memory graph data
        graph = await self._build_graph_for_task(dag_id, "")
        if graph:
            graph.clear()

        # Ensure the graph is empty after deletion
        graph = await self._build_graph_for_task(dag_id, "")
        if graph and len(graph.edges) > 0:
            raise RuntimeError(f"Failed to delete DAG {dag_id}")

    async def get_all_edges(self, dag_id: str) -> List[Tuple[str, str]]:
        """Get all edges in the DAG.

        Args:
            dag_id: ID of the DAG to get edges for

        Returns:
            List of (source_task_id, target_task_id) tuples
        """
        return await self._backend.get_all_edges(dag_id)

    async def get_dag_info(self, dag_id: str) -> Dict:
        """Get information about a DAG.

        Args:
            dag_id: ID of the DAG to get info for

        Returns:
            Dict containing DAG information
        """
        dag_info = await self._backend.get_dag_info(dag_id)
        return {
            "dag_id": dag_info["dag_id"],
            "name": dag_info["name"],
            "version": dag_info["version"],
            "edges": dag_info["edges"],
        }
