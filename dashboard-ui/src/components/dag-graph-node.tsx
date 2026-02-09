// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Fragment, useMemo } from "react";
import { Handle, Position } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { type SupportStatus } from "@nve/elements";
import { theme } from "~/styles/theme.gen.css";
import { TaskStatus } from "~/library/task-service";
import { TaskStatusBadge } from "./task-status-badge";

const taskStatusMap: { [key in TaskStatus]: SupportStatus | "neutral" } = {
    submitted: "neutral",
    waiting: "neutral",
    starting: "neutral",
    running: "accent",
    finished: "success",
    pausing: "warning",
    paused: "warning",
    errored: "danger",
    cancelling: "warning",
    cancelled: "warning",
    archived: "neutral",
    pending: "neutral",
    unscheduled: "neutral",
    unschedulable: "warning",
};

function DagGraphNode({
    data,
    selected,
}: {
    data: {
        orientation: "vertical" | "horizontal";
        progress: number;
        label: string;
        status: TaskStatus;
        fields: { label: string; value: string }[];
    };
    selected?: boolean;
}) {
    const sourcePosition = useMemo(() => {
        return data.orientation === "vertical"
            ? Position.Bottom
            : Position.Right;
    }, [data.orientation]);
    const targetPosition = useMemo(() => {
        return data.orientation === "vertical" ? Position.Top : Position.Left;
    }, [data.orientation]);
    const selectedHandleStyle = selected
        ? {
              background: theme.color.brandGreen1000,
              borderColor: theme.color.brandGreen1000,
          }
        : undefined;
    return (
        <nve-card>
            <nve-card-header>
                <div nve-layout="row align:vertical-center gap:sm">
                    <nve-progress-ring
                        size="md"
                        status={taskStatusMap[data.status] ?? "neutral"}
                        value={data.progress}
                    />
                    <h2 nve-text="heading sm bold">{data.label}</h2>
                </div>
            </nve-card-header>
            <nve-card-content>
                <dl nve-layout="grid gap:sm align:vertical-center">
                    <dt nve-layout="span:4" nve-text="body muted medium">
                        Status
                    </dt>
                    <dd
                        nve-layout="span:8"
                        nve-text="body truncate"
                        style={{
                            width: 200,
                        }}
                        title={data.status}
                    >
                        <TaskStatusBadge status={data.status} />
                    </dd>
                    {data.fields.map((field) => (
                        <Fragment key={field.label}>
                            <dt
                                nve-layout="span:4"
                                nve-text="body muted medium"
                            >
                                {field.label}
                            </dt>
                            <dd
                                nve-layout="span:8"
                                nve-text="body truncate"
                                style={{
                                    width: 200,
                                }}
                                title={field.value}
                            >
                                {field.value}
                            </dd>
                        </Fragment>
                    ))}
                </dl>
                <Handle
                    type="target"
                    position={targetPosition}
                    style={selectedHandleStyle}
                />
                <Handle
                    type="source"
                    position={sourcePosition}
                    style={selectedHandleStyle}
                />
            </nve-card-content>
        </nve-card>
    );
}

export { DagGraphNode };
