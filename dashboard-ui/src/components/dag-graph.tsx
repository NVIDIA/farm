// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReactFlow, Background, Controls } from "@xyflow/react";
import { DagGraphNode } from "~/components/dag-graph-node";

const nodeTypes = {
    DagGraphNode,
};

function DagGraph(props: Parameters<typeof ReactFlow>[0]) {
    return (
        <ReactFlow {...props} nodeTypes={nodeTypes}>
            <Background />
            <Controls />
        </ReactFlow>
    );
}

export { DagGraph };
