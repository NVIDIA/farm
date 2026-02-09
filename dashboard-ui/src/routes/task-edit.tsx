// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router";

// Local library
import {
    type Task,
    type PartialTask,
    TaskService,
} from "../library/task-service";

// Local
import { JsonInput } from "~/components/json-input";
import { KeyValueField } from "~/components/key-value-field";
import { KeyValueInput } from "~/components/key-value-input";
import { useUserContext } from "~/contexts/user-context/utils";
import { GridField } from "../components/grid-field";
import { TaskStatusBadge } from "~/components/task-status-badge";
import { PageHeader } from "~/components/page-header";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { ContentLoader } from "~/components/content-loader";
import { TaskProgressBar } from "~/components/task-progress-bar";

// Mapping of arbitrary field name to Task property key.
interface FieldNameToField {
    [key: string]: keyof Task;
}

// Mappinig of displayed field name of an editable field to
// the actual name of the field on the Task object.
const FIELD_MAP: FieldNameToField = {
    Priority: "priority",
    Comment: "comment",
    "Task Args": "args",
    "Function Args": "functionArgs",
    Metadata: "metadata",
} as const;

async function onSubmit(
    userId: string,
    {
        editableTask,
        editedFields,
    }: { editableTask?: PartialTask; editedFields?: Partial<Task> }
) {
    if (!editableTask) {
        return;
    }

    const { id, type, functionName, status } = editableTask;

    // Copy specific fields over from the task copy (required fields for the update)
    // and copy all edited fields into the partial task.
    const updateTask: PartialTask = {
        id,
        userId: userId || editableTask.userId,
        type,
        functionName,
        status,
        ...editedFields,
    };

    await TaskService.update(updateTask);
}

function TaskEdit(): JSX.Element {
    const { userId } = useUserContext();

    if (!userId) {
        throw new Error("Must be logged in");
    }

    const params = useParams();
    const id = params.id || "";

    const [selected, setSelected] = useState<string>("details");

    const { loading: submitTaskLoading, fetchData: fetchSubmitTaskData } =
        useDataFetcher(onSubmit);

    const {
        data: task,
        loading: taskLoading,
        fetchData: fetchTaskData,
    } = useDataFetcher(TaskService.get);

    const editableTask = useRef<PartialTask | null>(null);
    const editedFields = useRef<Partial<Task> | null>(null);
    const tabs = useMemo(
        () => ({
            items: [
                { label: "Details", value: "details" },
                { label: "Task Args", value: "taskArgs" },
                { label: "Function Args", value: "functionArgs" },
                { label: "Metadata", value: "metadata" },
            ],
            selected,
            onClick: (value: string) => setSelected(value),
        }),
        [selected]
    );

    if (editableTask.current === null && task !== null) {
        editableTask.current = task;
        editedFields.current = {};
    }

    useEffect(() => {
        console.log("Get Task at ", Date.now());
        fetchTaskData(id);
    }, [id, fetchTaskData]);

    function onInputFieldChanged(field: string, value: string | number) {
        const taskField = FIELD_MAP[field];

        if (
            !editableTask.current ||
            !editedFields.current ||
            taskField in editableTask.current === false
        ) {
            return;
        }

        // Update the set of edited fields.
        editedFields.current = {
            ...editedFields.current,
            [taskField]: value,
        };

        // Update the task copy to keep form state in-sync.
        editableTask.current = {
            ...editableTask.current,
            [taskField]: value,
        };
    }

    function onJsonInputFieldChanged(
        field: string,
        value: string,
        isValid: boolean
    ) {
        if (isValid === false) {
            return;
        }

        const taskField = FIELD_MAP[field];

        if (
            !editableTask.current ||
            taskField in editableTask.current === false
        ) {
            return;
        }

        const parsedValue = JSON.parse(value);

        // Update the set of edited fields.
        editedFields.current = {
            ...editedFields.current,
            [taskField]: parsedValue,
        };

        // Update the task copy to keep form state in-sync.
        editableTask.current = {
            ...editableTask.current,
            [taskField]: parsedValue,
        };
    }

    return (
        <div nve-layout="column gap:lg align:stretch">
            <PageHeader title={`Task ${id}`} tabs={tabs} />
            <ContentLoader
                nve-layout="column gap:md"
                loading={taskLoading || submitTaskLoading}
            >
                {task && editableTask.current && selected === "details" && (
                    <>
                        <KeyValueField
                            name="Id"
                            value={task.id}
                            link={`/task/${task?.id}`}
                        />
                        <KeyValueField name="User Id" value={task.userId} />
                        <KeyValueField
                            name="Taskflow Id"
                            value={task.metadata.dag?.id}
                            link={`/taskflow/${task?.metadata.dag?.id}`}
                        />
                        <KeyValueField name="Type" value={task.type} />
                        <KeyValueField
                            name="Function Name"
                            value={task.functionName}
                        />
                        <GridField name="Status">
                            <TaskStatusBadge status={task.status} />
                        </GridField>
                        <KeyValueField name="Details" value={task.details} />
                        <GridField name="Progress">
                            <TaskProgressBar
                                progress={task.progress?.progress}
                                status={task.status}
                            />
                        </GridField>
                        <KeyValueInput
                            name="Priority"
                            value={editableTask.current.priority}
                            onEdit={onInputFieldChanged}
                            isNumeric
                        />
                        <KeyValueInput
                            name="Comment"
                            value={editableTask.current.comment}
                            isMultiLine
                            onEdit={onInputFieldChanged}
                        />
                    </>
                )}

                {task && editableTask.current && selected === "taskArgs" && (
                    <JsonInput
                        name="Task Args"
                        defaultValue={editableTask.current.args}
                        onEdit={onJsonInputFieldChanged}
                    />
                )}

                {task &&
                    editableTask.current &&
                    selected === "functionArgs" && (
                        <JsonInput
                            name="Function Args"
                            defaultValue={editableTask.current.functionArgs}
                            onEdit={onJsonInputFieldChanged}
                        />
                    )}

                {task && editableTask.current && selected === "metadata" && (
                    <JsonInput
                        name="Metadata"
                        defaultValue={editableTask.current.metadata}
                        onEdit={onJsonInputFieldChanged}
                    />
                )}

                <nve-button
                    interaction="emphasis"
                    size="lg"
                    onClick={() => {
                        fetchSubmitTaskData(userId, {
                            editableTask: editableTask.current ?? undefined,
                            editedFields: editedFields.current ?? undefined,
                        });
                    }}
                >
                    Submit
                </nve-button>
            </ContentLoader>
        </div>
    );
}

export { TaskEdit };
