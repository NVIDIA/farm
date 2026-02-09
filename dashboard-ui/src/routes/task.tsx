// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";
// native custom elements
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { GridField } from "~/components/grid-field";
import { KeyValueField } from "~/components/key-value-field";
import { LogViewer } from "~/components/log-viewer";
import RandomColorTag from "~/components/random-color-tag";
import { RevisionTable } from "~/components/revision-table";
import { TabularField } from "~/components/tabular-field";
import { type Task as ApiTask, TaskService } from "~/library/task-service";
import { PageHeader } from "~/components/page-header";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { ContentLoader } from "~/components/content-loader";
import { TaskProgressBar } from "~/components/task-progress-bar";
// native elements used inline

type Selected = "details" | "metrics" | "logs" | "revisions";

function getDetails(task: ApiTask): JSX.Element {
    return (
        <div nve-layout="grid gap:lg span-items:12">
            <KeyValueField name="Id" value={task.id} />
            <KeyValueField name="User Id" value={task.userId} />
            <GridField name="Status">
                <div>{task.status}</div>
            </GridField>
            <GridField name="Labels">
                <div nve-layout="row gap:sm">
                    {task.labels.map((label, i) => (
                        <RandomColorTag key={i} label={label} />
                    ))}
                </div>
            </GridField>
            <KeyValueField
                name="Taskflow Id"
                value={task.metadata.dag?.id}
                link={`/taskflow/${task.metadata.dag?.id}`}
            />
            <KeyValueField name="Details" value={task.details} />
            <KeyValueField name="Comment" value={task.comment} />
            <KeyValueField name="Type" value={task.type} />
            <KeyValueField name="Function Name" value={task.functionName} />
            <KeyValueField name="Submitted" value={task.submissionDateString} />
            <KeyValueField name="Priority" value={task.priority} />
            <GridField name="Progress">
                <TaskProgressBar
                    progress={task.progress?.progress}
                    status={task.status}
                />
            </GridField>
            <TabularField name="ApiTask Args" value={task.args} />
            <TabularField name="Function Args" value={task.functionArgs} />
            <TabularField
                name="Metadata"
                value={task.metadata as { [key: string]: unknown }}
            />
            <TabularField name="Requirements" value={task.requirements} />
        </div>
    );
}

function getMetrics(task: ApiTask | null): JSX.Element {
    return (
        <div style={{ whiteSpace: "pre-wrap", overflowWrap: "break-word" }}>
            {task?.metrics}
        </div>
    );
}

function getLogs(selected: boolean, logs?: string) {
    // Hide the log tab instead of unmounting to prevent rerenders.
    // The insert method from @lyrasearch/lyra only loads logs synchronously so we only want to do this once.
    const style = selected ? {} : { display: "none" };

    return (
        <div style={style}>
            <LogViewer logs={logs || ""} />
        </div>
    );
}

function EditButton({ onClick }: { onClick: () => void }) {
    return (
        <nve-button onClick={onClick}>
            <nve-icon size="sm" name="edit"></nve-icon>
            Edit
        </nve-button>
    );
}

function Task() {
    const params = useParams();
    const navigate = useNavigate();
    const id = params.id || "";

    const {
        data: task,
        loading: taskLoading,
        error: taskError,
        reset: resetTask,
        fetchData: fetchTask,
    } = useDataFetcher(TaskService.get);

    const {
        data: logs,
        loading: logsLoading,
        error: logsError,
        reset: resetLogs,
        fetchData: fetchTaskLogs,
    } = useDataFetcher(TaskService.getLogs);

    const {
        data: revisions,
        loading: revisionsLoading,
        error: revisionsError,
        reset: resetRevisions,
        fetchData: fetchTaskRevisions,
    } = useDataFetcher(TaskService.getRevisions);

    const [selected, setSelected] = useState<Selected>("details");
    const error = taskError || logsError || revisionsError || "";

    const tabs = useMemo(
        () => ({
            items: [
                { label: "Details", value: "details" },
                { label: "Metrics", value: "metrics" },
                { label: "Logs", value: "logs" },
                { label: "Revisions", value: "revisions" },
            ],
            selected,
            onClick: (value: string) => setSelected(value as Selected),
        }),
        [selected]
    );

    useEffect(() => {
        if (selected === "details" && !task) {
            fetchTask(id);
        }

        if (selected === "logs" && !logs) {
            fetchTaskLogs(id);
        }

        if (selected === "revisions" && !revisions) {
            fetchTaskRevisions(id);
        }
    }, [
        id,
        fetchTask,
        fetchTaskLogs,
        fetchTaskRevisions,
        selected,
        task,
        logs,
        revisions,
    ]);

    return (
        <div nve-layout="column gap:lg align:stretch">
            {error && (
                <nve-alert-group status="danger" title="Error loading task">
                    <nve-alert
                        closable
                        onclose={() => {
                            resetLogs();
                            resetRevisions();
                            resetTask();
                        }}
                    >
                        {error}
                    </nve-alert>
                </nve-alert-group>
            )}
            <PageHeader
                title={`Task ${task?.id ?? ""}`}
                actions={
                    <EditButton onClick={() => navigate(`/task/edit/${id}`)} />
                }
                tabs={tabs}
            />
            <ContentLoader
                loading={taskLoading || revisionsLoading || logsLoading}
            >
                {selected === "details" && task ? getDetails(task) : ""}
                {selected === "metrics" ? getMetrics(task) : ""}
                {getLogs(selected === "logs", logs?.logs)}
                {selected === "revisions" && (
                    <RevisionTable revisions={revisions || []} />
                )}
            </ContentLoader>
        </div>
    );
}

export { Task };
