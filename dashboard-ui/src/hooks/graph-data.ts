// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
    addEdge,
    applyEdgeChanges,
    applyNodeChanges,
    Connection,
    Edge,
    EdgeChange,
    Node,
    NodeChange,
} from "@xyflow/react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { GraphEdge, GraphUtility } from "~/utilities/graph-utility";
import { theme } from "~/styles/theme.gen.css";
import { Task } from "~/library/task-service";

const nodeDefaults = {
    label: "",
    status: "",
    progress: 0,
    fields: [{ label: "Task Type", value: "" }],
    orientation: "horizontal",
} as const;

function computeDerivedEdges(edges: Edge[], nodes: Node[]): Edge[] {
    const selectedNodeIds = new Set(
        nodes.filter((n) => n.selected).map((n) => n.id)
    );
    return edges.map((edge) => {
        const isSelected =
            selectedNodeIds.has(edge.source) ||
            selectedNodeIds.has(edge.target);

        return {
            ...edge,
            selected: isSelected,
            style: isSelected
                ? {
                      ...(edge.style ?? {}),
                      stroke: theme.color.brandGreen1000,
                      strokeWidth: 3,
                      strokeDasharray: "6 3",
                  }
                : undefined,
        };
    });
}

function computeEdges(edges: GraphEdge[]): Edge[] {
    return edges.map((edge) => {
        return {
            id: `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
        };
    });
}

function computeNodes(
    edges: GraphEdge[],
    tasks: Task[],
    orientation: "vertical" | "horizontal"
): Node[] {
    if (tasks.length === 0) {
        return [];
    }

    const nodeData = tasks.reduce<Record<string, Record<string, unknown>>>(
        (acc, task) => {
            acc[task.id] = {
                label: task.metadata.dag?.name ?? "",
                status: task.status ?? "",
                progress: task.progress?.progress ?? 0,
                fields: [{ label: "Task Type", value: task.type ?? "" }],
                orientation,
            };
            return acc;
        },
        {} as Record<string, Record<string, unknown>>
    );

    const yOffset = orientation === "vertical" ? 400 : 200;
    const xOffset = orientation === "vertical" ? 400 : 600;

    if (edges.length === 0) {
        return Object.entries(nodeData).map(([id, data], i) => ({
            id,
            type: "DagGraphNode",
            data: data ?? nodeDefaults,
            position: { x: 0, y: i * yOffset },
        }));
    }

    return GraphUtility.getGraphUiNodesFromEdges(
        edges,
        xOffset,
        yOffset,
        orientation
    ).map((node) => ({
        ...node,
        type: "DagGraphNode",
        data: nodeData[node.id] ?? nodeDefaults,
    }));
}

interface GraphDataProps {
    dagEdges: GraphEdge[];
    tasks: Task[];
    orientation: "vertical" | "horizontal";
}

export function useGraphData({ dagEdges, tasks, orientation }: GraphDataProps) {
    const graphEdges = useMemo(() => computeEdges(dagEdges), [dagEdges]);
    const graphNodes = useMemo<Node[]>(
        () => computeNodes(dagEdges, tasks, orientation),
        [dagEdges, tasks, orientation]
    );
    const [nodes, setNodes] = useState(graphNodes);
    const [edges, setEdges] = useState(graphEdges);

    useEffect(() => {
        setNodes(graphNodes);
    }, [graphNodes]);
    useEffect(() => {
        setEdges(graphEdges);
    }, [graphEdges]);

    const onNodesChange = useCallback(
        (changes: NodeChange[]) =>
            setNodes((nodesSnapshot) =>
                applyNodeChanges(changes, nodesSnapshot)
            ),
        []
    );
    const onEdgesChange = useCallback(
        (changes: EdgeChange[]) =>
            setEdges((edgesSnapshot) =>
                applyEdgeChanges(changes, edgesSnapshot)
            ),
        []
    );
    const onConnect = useCallback(
        (params: Connection) =>
            setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
        []
    );

    const derivedEdges = useMemo(() => {
        return computeDerivedEdges(edges, nodes);
    }, [edges, nodes]);

    return {
        nodes,
        edges: derivedEdges,
        onNodesChange,
        onEdgesChange,
        onConnect,
    };
}
