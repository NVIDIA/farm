// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { http, HttpResponse } from "msw";
import { faker } from "@faker-js/faker";
// import { ServiceApiTask, TasksResponse } from "~/library/task-service";
import { ServiceApiAgents } from "~/library/agent-service";
import mockBatchesJson from "./mock-batches.json";
import mockLoadJobsJson from "./mock-load-jobs.json";
import mockTaskInfo from "./mock-task-info.json";
import mockTaskRevisionHistory from "./mock-task-revision-history.json";
import { TasksResponse } from "~/library/task-service";

function generateRandomIp() {
    return `ip-${Array.from({ length: 4 }, () =>
        Math.floor(Math.random() * 256)
    ).join(".")}`;
}

function generateRandomUUIDArray() {
    const numUUIDs = Math.floor(Math.random() * 5);
    return Array.from({ length: numUUIDs }, () => faker.string.uuid());
}

const host = "http://www.msw.com";

const sleep = () => new Promise((res) => setTimeout(() => res(null), 1000));

type Methods = typeof http.get | typeof http.post;

const withSleep =
    (method: Methods) =>
    (...parameters: Parameters<typeof method>) => {
        const [route, cb] = parameters;
        return method(`${host}${route}`, async (...args) => {
            await sleep();
            return cb(...args);
        });
    };

const get = withSleep(http.get);
const post = withSleep(http.post);

export const handlers = [
    get("/tasks/list", async (res) => {
        const url = new URL(res.request.url);
        const fields = url.searchParams.getAll("field");

        if (fields.includes("task_function_args")) {
            const response = JSON.parse(
                JSON.stringify(mockBatchesJson)
            ) as TasksResponse;
            Object.values(response).forEach((value) => {
                value.forEach((v) => {
                    v["task_function_args"] = {
                        usd_path: "omniverse://...",
                        collect_dir: "...",
                        s3_bucket: "...",
                        aws_profile: "...",
                    };
                });
            });

            return HttpResponse.json(response);
        }
        return HttpResponse.json(mockBatchesJson);
    }),
    get("/dashboard/config", () => {
        return HttpResponse.json({});
    }),
    get("/jobs/load", async () => {
        await sleep();
        return HttpResponse.json(mockLoadJobsJson);
    }),
    get("/agents/list", () => {
        faker.seed(123);

        const response: ServiceApiAgents = {};
        const now = new Date();
        for (let i = 0; i < 9; i++) {
            response[generateRandomIp()] = {
                active_tasks: generateRandomUUIDArray(),
                task_types: [
                    ["create-render", "render.run"],
                    ["another-create-render", "another.render.run"],
                ],
                checkin_time: faker.date
                    .between({
                        from: new Date(now.getTime() - 2 * 60 * 1000),
                        to: now,
                    })
                    .getTime(),
                status: faker.helpers.arrayElement(["idle", "active"]),
                resources: {},
                errored_task_count: faker.number.int({
                    min: 0,
                    max: 5,
                }),
                labels: faker.helpers.arrayElements(
                    ["label-1", "label-2", "label-3", "label-4", "label-5"],
                    { min: 0, max: 3 }
                ),
            };
        }
        return HttpResponse.json(response);
    }),
    get("/logs/:id", async () => {
        const logs = {
            created_at: 1732076053.246496,
            updated_at: 1732076173.631194,
            logs: "This is some logs\nThis is some more logs",
        };

        const warning = "[warning]";
        const error = "[error]";
        const info = "[info]";
        const logLineTypes = [
            error,
            warning,
            warning,
            info,
            info,
            info,
            info,
            info,
        ];
        const logLines: string[] = [];
        for (let i = 0; i < 300000; i++) {
            logLines.push(
                `${logLineTypes[Math.floor(Math.random() * logLineTypes.length)]} ${faker.lorem.sentences(Math.floor(Math.random() * 3) + 1)}`
            );
        }

        logs.logs = logLines.join("\n");

        return HttpResponse.json(logs);
    }),
    get("/tasks/info/:id", async () => {
        return HttpResponse.json(mockTaskInfo);
    }),
    post("/tasks/update", async (res) => {
        return HttpResponse.json(res.request.body);
    }),
    post("/tasks/cancel", async (res) => {
        return HttpResponse.json(res.request.body);
    }),
    post("/tasks/retry", async (res) => {
        return HttpResponse.json(res.request.body);
    }),
    post("/tasks/archive", async () => {
        return HttpResponse.json({
            archived_task_count: 0,
            error_count: 0,
            error_details: [],
        });
    }),
    get("/tasks/revision-history/:id", () => {
        return HttpResponse.json(mockTaskRevisionHistory);
    }),
    post("/agents/evict", async () => {
        return HttpResponse.json();
    }),
    post("/agents/enable", async () => {
        return HttpResponse.json();
    }),
    post("/agents/remove", async () => {
        return HttpResponse.json();
    }),
];
