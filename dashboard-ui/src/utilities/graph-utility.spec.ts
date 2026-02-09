// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { GraphUtility } from "./graph-utility";

describe("GraphUtility.getGraphLayers", () => {
    function sortLayers(layers: string[][]): string[][] {
        return layers.map((layer) => [...layer].sort());
    }

    it("lays out a simple chain A -> B -> C into separate layers", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "B", target: "C" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([["A"], ["B"], ["C"]]);
    });

    it("groups branching nodes A -> B and A -> C on the same layer", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "A", target: "C" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([["A"], ["B", "C"]]);
    });

    it("handles multiple roots: A -> B and C -> D", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "C", target: "D" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([
            ["A", "C"],
            ["B", "D"],
        ]);
    });

    it("deduplicates nodes in deeper layers (diamond shape)", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "A", target: "C" },
            { source: "B", target: "D" },
            { source: "C", target: "D" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([["A"], ["B", "C"], ["D"]]);
    });

    it("returns an empty set of layers for empty input", () => {
        const layers = GraphUtility.getGraphLayers([]);
        expect(layers).toEqual([]);
    });

    it("handles deep merges and wide branches", () => {
        // A branches to B,C; B->D,E; C->E,F; E and F merge to G
        const edges = [
            { source: "A", target: "B" },
            { source: "A", target: "C" },
            { source: "B", target: "D" },
            { source: "B", target: "E" },
            { source: "C", target: "E" },
            { source: "C", target: "F" },
            { source: "E", target: "G" },
            { source: "F", target: "G" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([
            ["A"],
            ["B", "C"],
            ["D", "E", "F"],
            ["G"],
        ]);
    });

    it("supports multiple roots with independent chains and a merge", () => {
        // Roots A and X; A branches then merges to G; X->Y->Z chain
        const edges = [
            { source: "A", target: "B" },
            { source: "A", target: "C" },
            { source: "B", target: "D" },
            { source: "C", target: "D" },
            { source: "D", target: "G" },
            { source: "X", target: "Y" },
            { source: "Y", target: "Z" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([
            ["A", "X"],
            ["B", "C", "Y"],
            ["D", "Z"],
            ["G"],
        ]);
    });

    it("deduplicates when multiple parents point to the same child in the same step", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "C", target: "B" },
        ];

        const layers = GraphUtility.getGraphLayers(edges);

        expect(sortLayers(layers)).toEqual([["A", "C"], ["B"]]);
    });
});

describe("GraphUtility.getGraphUiNodes", () => {
    it("returns empty array for empty layers", () => {
        const nodes = GraphUtility.getGraphUiNodes([], 0, 0, "horizontal");
        expect(nodes).toEqual([]);
    });

    it("uses default offsets (0,0) when none provided", () => {
        const layers = [["A", "B"], ["C"]];
        const nodes = GraphUtility.getGraphUiNodes(layers, 0, 0, "horizontal");
        expect(nodes).toEqual([
            { id: "A", position: { x: 0, y: 0 } },
            { id: "B", position: { x: 0, y: 0 } },
            { id: "C", position: { x: 0, y: 0 } },
        ]);
    });

    it("positions columns by xOffset and rows by yOffset, centering shorter rows to longest", () => {
        const layers = [
            ["A", "B", "C"],
            ["D", "E"],
        ];
        const nodes = GraphUtility.getGraphUiNodes(layers, 100, 50, "vertical");
        expect(nodes).toEqual([
            { id: "A", position: { x: 0, y: 0 } },
            { id: "B", position: { x: 100, y: 0 } },
            { id: "C", position: { x: 200, y: 0 } },
            { id: "D", position: { x: 50, y: 50 } },
            { id: "E", position: { x: 150, y: 50 } },
        ]);
    });

    it("positions rows by yOffset and columns by xOffset, centering shorter columns to longest (horizontal)", () => {
        const layers = [
            ["A", "B", "C"],
            ["D", "E"],
        ];
        const nodes = GraphUtility.getGraphUiNodes(
            layers,
            100,
            50,
            "horizontal"
        );
        expect(nodes).toEqual([
            { id: "A", position: { x: 0, y: 0 } },
            { id: "B", position: { x: 0, y: 50 } },
            { id: "C", position: { x: 0, y: 100 } },
            { id: "D", position: { x: 100, y: 25 } },
            { id: "E", position: { x: 100, y: 75 } },
        ]);
    });

    it("handles irregular layer lengths with centering to longest row", () => {
        const layers = [["A"], ["B", "C", "D"], ["E"]];
        const nodes = GraphUtility.getGraphUiNodes(layers, 10, 20, "vertical");
        expect(nodes).toEqual([
            { id: "A", position: { x: 10, y: 0 } },
            { id: "B", position: { x: 0, y: 20 } },
            { id: "C", position: { x: 10, y: 20 } },
            { id: "D", position: { x: 20, y: 20 } },
            { id: "E", position: { x: 10, y: 40 } },
        ]);
    });

    it("integration: uses getGraphLayers output to compute node positions", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "B", target: "C" },
        ];
        const layers = GraphUtility.getGraphLayers(edges);
        const nodes = GraphUtility.getGraphUiNodes(layers, 100, 10, "vertical");
        expect(nodes).toEqual([
            { id: "A", position: { x: 0, y: 0 } },
            { id: "B", position: { x: 0, y: 10 } },
            { id: "C", position: { x: 0, y: 20 } },
        ]);
    });

    it("integration (horizontal): uses getGraphLayers with horizontal layout", () => {
        const edges = [
            { source: "A", target: "B" },
            { source: "B", target: "C" },
        ];
        const layers = GraphUtility.getGraphLayers(edges);
        const nodes = GraphUtility.getGraphUiNodes(
            layers,
            100,
            10,
            "horizontal"
        );
        expect(nodes).toEqual([
            { id: "A", position: { x: 0, y: 0 } },
            { id: "B", position: { x: 100, y: 0 } },
            { id: "C", position: { x: 200, y: 0 } },
        ]);
    });
    // Vertical/horizontal centering is now derived from longest-row centering within getGraphUiNodes
});
