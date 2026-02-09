// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export interface GraphEdge {
    source: string;
    target: string;
}

export interface GraphNode {
    id: string;
    position: {
        x: number;
        y: number;
    };
}

const GraphUtility = {
    // given a set of edges, return a graph of the edges
    getGraphFromEdges(edges: GraphEdge[]): Record<string, string[]> {
        return edges.reduce<Record<string, string[]>>((acc, edge) => {
            const target = acc[edge.source] || [];
            target.push(edge.target);
            acc[edge.source] = target;
            return acc;
        }, {});
    },
    // given a graph and edges, return the entrypoints of the graph
    getGraphEntrypoints(
        graph: Record<string, string[]>,
        edges: GraphEdge[]
    ): string[] {
        const targets = edges.reduce<Set<string>>((acc, edge) => {
            acc.add(edge.target);
            return acc;
        }, new Set());

        return Object.keys(graph).filter((node) => !targets.has(node));
    },
    // given a graph and entrypoints, return a list of layers of nodes
    getBFSGraphLayers(
        graph: Record<string, string[]>,
        entrypoints: string[]
    ): string[][] {
        if (entrypoints.length === 0) {
            return [];
        }

        // Initialize the layers with the entrypoints
        const layers: string[][] = [entrypoints];

        // Do a breadth first traversal of the graph and build the layers
        for (const layer of layers) {
            // use a set to avoid duplicates
            const nextLayer = new Set<string>();
            for (const node of layer) {
                // if the node is a source node, add its targets to the next layer
                if (node in graph) {
                    const nodes = graph[node];
                    nodes.forEach((target) => {
                        nextLayer.add(target);
                    });
                }
            }

            if (nextLayer.size) {
                layers.push([...nextLayer]);
            }
        }

        return layers;
    },
    // Given a set of edges, return a list of layers of nodes
    getGraphLayers(edges: GraphEdge[]) {
        // Build a graph of the edges
        const graph = this.getGraphFromEdges(edges);

        // Get the entrypoints of the graph by finding source nodes that are not targets
        const entrypoints = this.getGraphEntrypoints(graph, edges);

        // Build the layers of the graph
        return this.getBFSGraphLayers(graph, entrypoints);
    },
    getHorizontalGraphUiNode(
        layers: string[][],
        layerIndex: number,
        nodeIndex: number,
        longestRow: number,
        xOffset: number,
        yOffset: number
    ): GraphNode {
        const layer = layers[layerIndex];
        const node = layer[nodeIndex];
        // use the height of the longest row to center the column
        const longestColumnHeight = longestRow * yOffset;
        // get the starting position of the first node in the column using the longest column height to center the column
        const currentColumnHeight = layer.length * yOffset;
        const columnOffset = (longestColumnHeight - currentColumnHeight) / 2;

        return {
            id: node,
            position: {
                // every column has the same x position
                x: layerIndex * xOffset,
                // plot the node in the column along the y axis
                y: nodeIndex * yOffset + columnOffset,
            },
        };
    },
    getVerticalGraphUiNode(
        layers: string[][],
        layerIndex: number,
        nodeIndex: number,
        longestRow: number,
        xOffset: number,
        yOffset: number
    ): GraphNode {
        const layer = layers[layerIndex];
        const node = layer[nodeIndex];
        // use the width of the longest column to center the row
        const longestRowWidth = longestRow * xOffset;
        // get the starting position of the first node in the row using the longest row width to center the row
        const currentRowWidth = layer.length * xOffset;
        const rowOffset = (longestRowWidth - currentRowWidth) / 2;

        return {
            id: node,
            position: {
                // plot the node in the row along the x axis
                x: nodeIndex * xOffset + rowOffset,
                // every row has the same y position
                y: layerIndex * yOffset,
            },
        };
    },
    getGraphUiNode(
        layers: string[][],
        layerIndex: number,
        nodeIndex: number,
        longestRow: number,
        xOffset: number,
        yOffset: number,
        orientation: "vertical" | "horizontal"
    ): GraphNode {
        if (orientation === "horizontal") {
            return this.getHorizontalGraphUiNode(
                layers,
                layerIndex,
                nodeIndex,
                longestRow,
                xOffset,
                yOffset
            );
        }
        return this.getVerticalGraphUiNode(
            layers,
            layerIndex,
            nodeIndex,
            longestRow,
            xOffset,
            yOffset
        );
    },
    // Given a list of layers of nodes, return a list of nodes with their positions
    getGraphUiNodes(
        layers: string[][],
        xOffset: number = 0,
        yOffset: number = 0,
        orientation: "vertical" | "horizontal"
    ): GraphNode[] {
        const longestRow = layers.reduce(
            (max, row) => Math.max(max, row.length),
            0
        );

        // return an array of ui nodes for each node in each layer of the graph
        return layers
            .map((layer, layerIndex) =>
                layer.map((_, nodeIndex) =>
                    this.getGraphUiNode(
                        layers,
                        layerIndex,
                        nodeIndex,
                        longestRow,
                        xOffset,
                        yOffset,
                        orientation
                    )
                )
            )
            .flat();
    },
    // Given a set of edges, return a list of nodes with their positions
    getGraphUiNodesFromEdges(
        edges: GraphEdge[],
        xOffset: number = 0,
        yOffset: number = 0,
        orientation: "vertical" | "horizontal"
    ): GraphNode[] {
        const layers = this.getGraphLayers(edges);
        return this.getGraphUiNodes(layers, xOffset, yOffset, orientation);
    },
};

export { GraphUtility };
