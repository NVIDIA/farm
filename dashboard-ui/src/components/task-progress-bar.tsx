// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TaskStatus } from "~/library/task-service";
import { ProgressBar } from "./progress-bar";

type Status = Parameters<typeof ProgressBar>[0]["status"];

const taskStatusMap: {
    [key in TaskStatus]: Status | null;
} = {
    submitted: "accent",
    waiting: "accent",
    starting: "accent",
    running: "accent",
    finished: "success",
    pausing: "warning",
    paused: "warning",
    errored: "danger",
    cancelling: "warning",
    cancelled: "warning",
    archived: null,
    pending: "accent",
    unscheduled: "accent",
    unschedulable: "warning",
};

function TaskProgressBar({
    status,
    progress = 0,
}: {
    progress?: number;
    status: TaskStatus;
}) {
    progress = status === "finished" ? 1 : progress;
    return <ProgressBar progress={progress} status={taskStatusMap[status]} />;
}

export { TaskProgressBar };
