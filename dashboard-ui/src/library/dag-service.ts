// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// task-service.ts
// Single instance async data access object responsible for
// task-related interactions.

import { Http } from "~/library/http";
import { PathUtility } from "~/library/path-utility";

// Local dependencies

interface DagInfoResponse {
    name: string;
    version: number;
    id: string;
    edges: { source_task_id: string; target_task_id: string }[];
}

interface DagInfo {
    name: string;
    version: number;
    id: string;
    edges: { source: string; target: string }[];
}

// Single instance service object.
const DagService = {
    async getDagInfo(id: string): Promise<DagInfo> {
        const dagInfoResponse = await Http.get<DagInfoResponse>(
            PathUtility.get("dagPath", id)
        );
        const edges = dagInfoResponse.body.edges.map((edge) => ({
            source: edge.source_task_id,
            target: edge.target_task_id,
        }));
        return {
            ...dagInfoResponse.body,
            edges,
        };
    },
} as const;

export { DagService };
