// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TaskStatus } from "~/library/task-service";
import { TaskStatus as NveTaskStatus } from "@nve/elements";

const taskStatusMap: { [key: string]: NveTaskStatus } = {
    submitted: "scheduled",
    waiting: "queued",
    starting: "starting",
    running: "running",
    finished: "finished",
    pausing: "pending",
    paused: "pending",
    errored: "failed",
    cancelling: "stopping",
    cancelled: "stopping",
    pending: "pending",
    archived: "unknown",
    unscheduled: "pending",
    unschedulable: "ignored",
};

function mapTaskStatus(status: string): NveTaskStatus {
    return taskStatusMap[status] || "unknown";
}

export function TaskStatusBadge({
    status,
    label = "",
}: {
    status?: TaskStatus;
    label?: string;
}) {
    label = label ? label : status || "unknown";
    return <nve-badge status={mapTaskStatus(status || "")}>{label}</nve-badge>;
}
