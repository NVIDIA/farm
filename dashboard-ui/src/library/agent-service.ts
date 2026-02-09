// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// task-service.ts
// Single instance async data access object responsible for
// task-related interactions.

// Local dependencies
import { Http } from "./http";
import { PathUtility } from "./path-utility";
import { TimeUtility } from "../utilities/time-utility";

type UnknownDictionary = {
    [key: string]: string | number | boolean;
};

export interface ServiceApiAgent {
    agent_id?: string;
    active_tasks: string[];
    checkin_time: number;
    task_types: [string, string][];
    status: string;
    resources: UnknownDictionary;
    errored_task_count: number;
    labels: string[];
}

export interface ServiceApiAgents {
    [key: string]: ServiceApiAgent;
}

export interface Agent {
    id: string;
    tasks: string[];
    checkinMs: number;
    checkinDate: Date;
    checkinDateString: string;
    elapsedCheckinTime: string;
    status: string;
    errorCount: number;
    labels: string[];
    taskTypes: [string, string][];
}

function incomingAgentToAgent(id: string, agent: ServiceApiAgent): Agent {
    const {
        active_tasks,
        checkin_time,
        status,
        errored_task_count,
        labels,
        task_types,
    } = agent;

    const checkinS = Math.floor(checkin_time);
    const checkinMs = checkinS * 1000;
    const checkinDate = new Date(checkinMs);
    const checkinDateString = TimeUtility.getCompactString(checkinDate);
    const elapsedCheckinTime = TimeUtility.getMajorTimeSinceString(checkinMs);

    return {
        id,
        tasks: active_tasks,
        checkinMs,
        checkinDate,
        checkinDateString,
        elapsedCheckinTime,
        status,
        errorCount: errored_task_count,
        labels,
        taskTypes: task_types,
    };
}

const AgentService = {
    // Returns a promise that resolves to all agents available to the Farm.
    async getAll(): Promise<Agent[]> {
        const response = await Http.get<ServiceApiAgents>(
            PathUtility.get("agentPath", "list")
        );
        const agents = Object.keys(response.body).map((id) =>
            incomingAgentToAgent(id, response.body[id])
        );
        return agents;
    },
    // Returns a promise of evicting the specified agent by id.
    async evict(id: string): Promise<void> {
        const body = { agent_id: id } as const;
        await Http.post<Partial<ServiceApiAgent>, void>(
            PathUtility.get("agentPath", "evict"),
            body
        );
    },
    // Returns a promise of enabling (after an eviction) the specified agent by id.
    async enable(id: string): Promise<void> {
        const body = { agent_id: id } as const;
        await Http.post<Partial<ServiceApiAgent>, void>(
            PathUtility.get("agentPath", "enable"),
            body
        );
    },
    // Returns a promise of removing the specified agent by id.
    async remove(id: string): Promise<void> {
        const body = { agent_id: id } as const;
        await Http.post<Partial<ServiceApiAgent>, void>(
            PathUtility.get("agentPath", "remove"),
            body
        );
    },
} as const;

export { AgentService };
