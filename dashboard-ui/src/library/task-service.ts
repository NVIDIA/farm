// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// task-service.ts
// Single instance async data access object responsible for
// task-related interactions.

// Local dependencies
import { TimeUtility } from "../utilities/time-utility";
import { Http, HttpError } from "./http";
import { PathUtility } from "./path-utility";

export type TaskStatus =
    | "submitted"
    | "waiting"
    | "starting"
    | "running"
    | "finished"
    | "pausing"
    | "paused"
    | "errored"
    | "cancelling"
    | "cancelled"
    | "archived"
    | "pending"
    | "unscheduled"
    | "unschedulable";

export interface TaskFilter {
    type?: string;
    func?: string;
    statuses?: TaskStatus[];
}

export interface TaskProgress {
    current_step_index?: number;
    total_step_count?: number;
    progress?: number;
    status_message?: string;
    time_remaining?: number;
}

export interface TaskMetadata {
    batches?: {
        last_index?: number;
        batch_id?: string;
        index?: number;
    };
    dag?: {
        id?: string;
        name?: string;
    };
    dependants?: Array<{
        source_queue?: string;
        task_ids?: string[];
        task_type?: string;
        task_function?: string;
    }>;
    original_submitter?: string;
}

type UnknownDictionary = {
    [key: string]: string | number | boolean;
};

interface ServiceApiRevision {
    task_id: string;
    status: TaskStatus;
    user_id: string;
    agent_id: string;
    details: string;
    progress: TaskProgress;
    time: number;
}

export interface Revision {
    status: TaskStatus;
    agentId: string;
    userId: string;
    details: string;
    progress: TaskProgress;
    timeS: number;
    timeDate: Date;
    timeDateString: string;
}

interface ServiceApiTask {
    task_id: string;
    task_type: string;
    task_details: string;
    task_args: UnknownDictionary;
    task_function: string;
    task_function_args: UnknownDictionary;
    task_requirements: UnknownDictionary;
    status: TaskStatus;
    userid: string;
    task_comment: string;
    metrics: string;
    progress: TaskProgress;
    task_submission_time: number;
    priority: number;
    metadata: UnknownDictionary;
    labels: string[];
}

export interface TasksResponse {
    [key: string]: ServiceApiTask[];
}

interface Log {
    logs: string;
}

export interface Task {
    status: TaskStatus;
    id: string;
    userId: string;
    type: string;
    details: string;
    args: UnknownDictionary;
    functionName: string;
    functionArgs: UnknownDictionary;
    requirements: UnknownDictionary;
    comment: string;
    metrics: string | null;
    progress: TaskProgress | null;
    submissionS: number;
    priority: number;
    metadata: TaskMetadata;
    submissionDate: Date;
    submissionDateString: string;
    revisions?: Revision[];
    logs?: Log;
    labels: string[];
}

type RequiredPartialFields =
    | "id"
    | "userId"
    | "type"
    | "functionName"
    | "status";
type OptionalPartialFields =
    | "details"
    | "comment"
    | "args"
    | "functionArgs"
    | "priority"
    | "metadata";
export type PartialTask = Pick<Task, RequiredPartialFields> &
    Partial<Pick<Task, OptionalPartialFields>>;

interface MinimalBatch {
    id: string;
    tasks: Task[];
}

export interface Batch extends MinimalBatch {
    comment: string;
    taskCount: number;
    finishedCount: number;
    errorCount: number;
    startedDate: Date;
    startedDateTimeS: number;
    startedDateTimeStr: string;
}

interface MinimalTaskflow {
    id: string;
    tasks: Task[];
}

export interface Taskflow extends MinimalTaskflow {
    comment: string;
    taskCount: number;
    finishedCount: number;
    errorCount: number;
    startedDate: Date;
    startedDateTimeS: number;
    startedDateTimeStr: string;
}

export interface ArchiveResponse {
    archived_task_count: number;
    error_count: number;
    error_details: string[];
}

// Array of fields used when requesting all tasks.
const TASK_LIST_FIELDS = [
    "task_id",
    "task_type",
    "task_function",
    "task_status",
    "user_id",
    "task_comment",
    "task_progress",
    "task_submission_time",
    "priority",
    "metadata",
    "labels",
] as const;

// Array of statuses used when requesting all tasks.
export const TASK_LIST_STATUSES = [
    "submitted",
    "waiting",
    "starting",
    "running",
    "finished",
    "pausing",
    "paused",
    "errored",
    "cancelling",
    "cancelled",
    "pending",
    "unscheduled",
    "unschedulable",
] as const;

export const BULK_ACTIONS = ["CANCEL", "ARCHIVE", "RETRY"] as const;
export type BulkActions = (typeof BULK_ACTIONS)[number];

// Helper function for converting an API formatted task to one used by
// the local interface. The local interface makes the data members more JavaScript
// in format and adds various helper fields.
function serviceApiTaskToTask(task: ServiceApiTask): Task {
    const {
        task_id,
        task_type,
        task_details,
        task_args,
        task_function,
        task_function_args,
        task_requirements,
        status,
        userid,
        task_comment,
        metrics,
        progress,
        task_submission_time,
        priority,
        metadata,
        labels,
    } = task;

    const submissionS = Math.floor(task_submission_time);
    const submissionMs = submissionS * 1000;
    const submissionDate = new Date(submissionMs);
    const submissionDateString = submissionDate.toLocaleTimeString("en-us", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });

    return {
        id: task_id,
        type: task_type,
        details: task_details,
        args: task_args,
        functionName: task_function,
        functionArgs: task_function_args,
        requirements: task_requirements,
        status,
        comment: task_comment,
        metrics,
        submissionS: Math.floor(task_submission_time),
        priority,
        progress,
        userId: userid,
        metadata,
        submissionDate: new Date(Math.floor(task_submission_time) * 1000),
        submissionDateString,
        labels: labels || [],
    };
}

function partialTaskToServiceApiTask(
    task: PartialTask
): Partial<ServiceApiTask> {
    const {
        id,
        type,
        details,
        args,
        functionName,
        functionArgs,
        status,
        comment,
        priority,
        userId,
        metadata,
    } = task;

    return {
        task_id: id,
        task_type: type,
        task_details: details,
        task_args: args,
        task_function: functionName,
        task_function_args: functionArgs,
        status,
        userid: userId,
        task_comment: comment,
        priority,
        metadata: metadata as UnknownDictionary,
    };
}

// Helper function for converting the microservice formatted revision into
// a local, JavaScript friendly api version.
function serviceApiRevisionToRevision(revision: ServiceApiRevision): Revision {
    const { status, agent_id, user_id, details, progress, time } = revision;

    const timeS = Math.floor(time);
    const timeDate = new Date(Math.floor(time) * 1000);
    const timeDateString = TimeUtility.getCompactString(timeDate);

    return {
        status,
        userId: user_id,
        agentId: agent_id,
        details,
        progress,
        timeS,
        timeDate,
        timeDateString,
    };
}

// Single instance service object.
const TaskService = {
    async get(id: string): Promise<Task> {
        const taskResponse = await Http.get<ServiceApiTask>(
            PathUtility.get("taskPath", "info", id)
        );
        const task = serviceApiTaskToTask(taskResponse.body);

        return task;
    },
    async getAll(additionalFields: string[] = []): Promise<Task[]> {
        const field = [...new Set([...additionalFields, ...TASK_LIST_FIELDS])];
        const parameters = {
            status: TASK_LIST_STATUSES,
            field,
        };
        const response = await Http.get<TasksResponse>(
            PathUtility.get("taskPath", "list"),
            parameters
        );
        const tasks = Object.values(response.body)
            .map((items) => items.map(serviceApiTaskToTask))
            .flat();

        return tasks;
    },
    async getBatches(): Promise<Batch[]> {
        const tasks = await this.getAll();
        const batchesByKey = tasks.reduce(
            (accumulator, task) => {
                const batchId = task.metadata?.batches?.batch_id;
                if (batchId) {
                    if (batchId in accumulator) {
                        accumulator[batchId].tasks?.push(task);
                    } else {
                        accumulator[batchId] = {
                            id: batchId,
                            tasks: [task],
                        };
                    }
                }
                return accumulator;
            },
            {} as { [key: string]: MinimalBatch }
        );

        const batches =
            Object.values(batchesByKey).map((batch) => {
                // Add any additional aggregated data.
                const taskCount = batch.tasks?.length ?? 0;
                const errorCount =
                    batch.tasks?.reduce((accumulator, task) => {
                        if (task.status === "errored") {
                            return accumulator + 1;
                        }

                        return accumulator;
                    }, 0) ?? 0;

                const finishedCount =
                    batch.tasks?.reduce((accumulator, task) => {
                        if (
                            task.status === "finished" ||
                            task.status === "archived"
                        ) {
                            return accumulator + 1;
                        }

                        return accumulator;
                    }, 0) ?? 0;

                const comment =
                    batch.tasks.find((task) => !!task.comment)?.comment ?? "";
                const timestampsS = batch.tasks.map((task) => task.submissionS);
                const earliestTimestampS = Math.min(...timestampsS);

                const hydratedBatch: Batch = {
                    ...batch,
                    taskCount,
                    errorCount,
                    finishedCount,
                    comment,
                    startedDate: new Date(earliestTimestampS * 1000),
                    startedDateTimeS: earliestTimestampS,
                    startedDateTimeStr: TimeUtility.getCompactString(
                        new Date(earliestTimestampS * 1000)
                    ),
                };

                return hydratedBatch;
            }) ?? [];

        return batches;
    },
    async getTaskflows(): Promise<Taskflow[]> {
        const tasks = await this.getAll();
        const taskflowsByKey = tasks.reduce(
            (accumulator, task) => {
                const taskflowId = task.metadata?.dag?.id;
                if (taskflowId) {
                    if (taskflowId in accumulator) {
                        accumulator[taskflowId].tasks?.push(task);
                    } else {
                        accumulator[taskflowId] = {
                            id: taskflowId,
                            tasks: [task],
                        };
                    }
                }
                return accumulator;
            },
            {} as { [key: string]: MinimalTaskflow }
        );

        const taskflows =
            Object.values(taskflowsByKey).map((taskflow) => {
                // Add any additional aggregated data.
                const taskCount = taskflow.tasks?.length ?? 0;
                const errorCount =
                    taskflow.tasks?.reduce((accumulator, task) => {
                        if (task.status === "errored") {
                            return accumulator + 1;
                        }

                        return accumulator;
                    }, 0) ?? 0;

                const finishedCount =
                    taskflow.tasks?.reduce((accumulator, task) => {
                        if (
                            task.status === "finished" ||
                            task.status === "archived"
                        ) {
                            return accumulator + 1;
                        }

                        return accumulator;
                    }, 0) ?? 0;

                const comment =
                    taskflow.tasks.find((task) => !!task.comment)?.comment ??
                    "";
                const timestampsS = taskflow.tasks.map(
                    (task) => task.submissionS
                );
                const earliestTimestampS = Math.min(...timestampsS);

                const hydratedTaskflow: Taskflow = {
                    ...taskflow,
                    taskCount,
                    errorCount,
                    finishedCount,
                    comment,
                    startedDate: new Date(earliestTimestampS * 1000),
                    startedDateTimeS: earliestTimestampS,
                    startedDateTimeStr: TimeUtility.getCompactString(
                        new Date(earliestTimestampS * 1000)
                    ),
                };

                return hydratedTaskflow;
            }) ?? [];

        return taskflows;
    },
    async getTaskflow(id: string): Promise<Taskflow | undefined> {
        const taskflows = await this.getTaskflows();
        const taskflow = taskflows.find((taskflow) => taskflow.id === id);
        return taskflow;
    },
    async getBatch(id: string): Promise<Batch | undefined> {
        const batches = await this.getBatches();
        const batch = batches.find((batch) => batch.id === id);
        return batch;
    },
    async cancel(
        id: string,
        userId: string,
        type: string,
        functionName: string,
        status: TaskStatus
    ): Promise<void> {
        await Http.post<Partial<ServiceApiTask>, null>(
            PathUtility.get("taskPath", "cancel"),
            {
                task_id: id,
                task_type: type,
                task_function: functionName,
                status,
                userid: userId,
            }
        );
    },
    async retry(
        id: string,
        userId: string,
        type: string,
        functionName: string,
        status: TaskStatus
    ): Promise<void> {
        await Http.post<Partial<ServiceApiTask>, null>(
            PathUtility.get("taskPath", "retry"),
            {
                task_id: id,
                task_type: type,
                task_function: functionName,
                status,
                userid: userId,
            }
        );
    },
    async archive(ids: string[]): Promise<ArchiveResponse> {
        const response = await Http.post<
            { task_ids: string[] },
            ArchiveResponse
        >(PathUtility.get("taskPath", "archive"), {
            task_ids: ids,
        });

        return response.body;
    },
    async update(task: PartialTask): Promise<void> {
        const apiTask = partialTaskToServiceApiTask(task);
        await Http.post<Partial<ServiceApiTask>, null>(
            PathUtility.get("taskPath", "update"),
            apiTask
        );
    },
    async getLogs(id: string): Promise<Log> {
        try {
            const response = await Http.get<Log>(
                PathUtility.get("logPath", id)
            );

            return response.body;
        } catch (e) {
            if (e && typeof e === "object" && "response" in e) {
                // Errors with logs may have a body containing information about
                // fetching logs. Create a log object out of the error message.
                return {
                    logs: (e as HttpError).response.body.detail as string,
                };
            }

            return {
                logs: "",
            };
        }
    },
    async getRevisions(id: string): Promise<Revision[]> {
        try {
            const response = await Http.get<ServiceApiRevision[]>(
                PathUtility.get("taskPath", "revision-history", id)
            );

            return response.body.map(serviceApiRevisionToRevision);
        } catch (exception) {
            const error = exception as Error;
            console.error(
                `Exception while getting revision for task id ${id}: ${error.message}`
            );
            return [];
        }
    },
    async bulkStatus({
        ids,
        status,
        userId,
    }: {
        status: TaskStatus;
        ids: string[];
        userId: string;
    }) {
        await Http.post(PathUtility.get("taskPath", "update", "bulk"), {
            userid: userId,
            status,
            task_ids: ids,
        });
    },
} as const;

export { TaskService };
