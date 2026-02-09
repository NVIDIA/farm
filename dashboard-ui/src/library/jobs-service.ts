// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Local.
import { Http } from "./http";
import { PathUtility } from "./path-utility";

export interface JobDefinition {
    name: string;
    job_type: string;
    command: string;
    args: string[];
    task_function: string;
    env: Record<string, unknown>;
    log_to_stdout: boolean;
    extension_paths: string[];
    allowed_args: Record<string, unknown>;
    job_spec_path: string;
    headless: boolean;
    active: boolean;
    resolved_command_path: string;
    success_return_codes: number[];
    capacity_requirements: Record<string, unknown>;
    working_directory: string;
    container: string;
}

interface JobDefinitionObject {
    [key: string]: JobDefinition;
}

// JobsService
// Single instance object responsible for async communication
// with remote Farm jobs service.

const JobsService = {
    // Given the name of a job, returns a promise of the job definition from the job service.
    async get(name: string): Promise<JobDefinition | undefined> {
        const response = await Http.get<JobDefinitionObject>(
            PathUtility.get("jobsPath", "load")
        );
        return response.body[name];
    },
    // Returns a promise of all job definitions.
    async getAll(): Promise<JobDefinition[]> {
        const response = await Http.get<JobDefinitionObject>(
            PathUtility.get("jobsPath", "load")
        );
        return Object.values(response.body);
    },
} as const;

export { JobsService };
