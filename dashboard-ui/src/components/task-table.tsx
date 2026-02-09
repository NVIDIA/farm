// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router";
import type { RowData } from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";
import RandomColorTag from "~/components/random-color-tag";
import { TaskStatusBadge } from "~/components/task-status-badge";
import { useUserContext } from "~/contexts/user-context/utils";
import { useDataFetcher } from "~/hooks/data-fetcher";
import {
    Task,
    TASK_LIST_STATUSES,
    TaskService,
    TaskStatus,
} from "~/library/task-service";
import { TaskProgressBar } from "~/components/task-progress-bar";
import { Dialog } from "~/components/dialog";
import { useRowData } from "~/hooks/row-data";
import { useTableSearchParams } from "~/hooks/table-search-params";
import { useBulkSelect } from "~/hooks/bulk-select";
import {
    DataTable,
    DataTableContentLoader,
    DataTableFilterBar,
    DataTablePageHeader,
    DataTableToolbar,
} from "~/components/data-table";
import { DagGraph } from "./dag-graph";
import { useGraphData } from "~/hooks/graph-data";
import { DagService } from "~/library/dag-service";
// using native elements

const COLUMNS = TableDataUtility.createColumns([
    {
        id: "submissionDate",
        headerText: "SUBMITTED AT",
        type: "DATE",
    },
    {
        id: "id",
        renderCell: ({ data }: RowData<Task>) => {
            return <Link to={`/task/${data.id}`}>{data.id}</Link>;
        },
    },
    {
        id: "status",
        type: "MULTI_SELECT",
        filterItems: TASK_LIST_STATUSES.map((status) => ({
            label: status,
            value: status,
        })),
        renderCell: ({ data }: RowData<Task>) => {
            return <TaskStatusBadge status={data.status} />;
        },
    },
    {
        id: "labels",
        renderCell: ({ data }: RowData<Task>) => {
            return (
                <div>
                    {data.labels.map((v, i) => (
                        <RandomColorTag key={i} label={v} />
                    ))}
                </div>
            );
        },
    },
    { id: "userId" },
    { id: "type" },
    { id: "functionName" },
    { id: "comment" },
    {
        id: "progress",
        filterable: false,
        sortable: false,
        renderCell: ({ data }: RowData<Task>) => {
            return (
                <TaskProgressBar
                    progress={data.progress?.progress}
                    status={data.status}
                />
            );
        },
    },
]);

const defaultColumns = COLUMNS.map((column) => column.id);

const bulkActionItems = [
    { label: "Cancel", value: "cancel" },
    { label: "Retry", value: "retry" },
    { label: "Archive", value: "archive" },
];

type BulkActionMapFn = (args: {
    ids: string[];
    userId: string;
}) => Promise<void>;

type BulkActionMapKeys = "cancel" | "archive" | "retry";
type BulkActionMap = { [key in BulkActionMapKeys]: BulkActionMapFn };

const bulkActionMap: BulkActionMap = {
    cancel: (args) =>
        TaskService.bulkStatus({
            ...args,
            status: "cancelling",
        }),
    archive: (args) =>
        TaskService.bulkStatus({
            ...args,
            status: "archived",
        }),
    retry: (args) =>
        TaskService.bulkStatus({
            ...args,
            status: "submitted",
        }),
};

async function onBulkAction({
    action,
    selected,
    userId,
}: {
    action: string;
    selected: string[];
    userId: string;
}) {
    if (action in bulkActionMap) {
        await bulkActionMap[action as keyof typeof bulkActionMap]({
            ids: selected,
            userId,
        });
    } else {
        throw new Error(`Unhandled bulk action: ${action}`);
    }
}

function computeTaskMetadata(tasks: Task[]) {
    const taskStatusMap = tasks.reduce(
        (acc, value) => {
            const total = acc.total || 0;
            const statusTotal = acc[value.status] || 0;
            acc.total = total + 1;
            acc[value.status] = statusTotal + 1;
            return acc;
        },
        {} as { [key: string]: number }
    );

    return Object.entries(taskStatusMap)
        .map(([label, value]) => ({
            label,
            value,
        }))
        .sort((a, b) => (a.label < b.label ? 1 : a.label > b.label ? -1 : 0));
}

function Metadata({ rows }: { rows: RowData<Task>[] }) {
    const metadata = useMemo(
        () => computeTaskMetadata(rows.map((row) => row.data)),
        [rows]
    );
    return metadata.map(({ label, value }) => (
        <TaskStatusBadge
            key={label}
            status={label as TaskStatus}
            label={`${label}: ${value}`}
        />
    ));
}

async function getAllTasks(
    loadFields: string[] = [],
    batchId = "",
    taskflowId = ""
) {
    const tasks = await TaskService.getAll(loadFields);

    if (batchId) {
        return tasks.filter(
            (task) => task.metadata.batches?.batch_id === batchId
        );
    }

    if (taskflowId) {
        return tasks.filter((task) => task.metadata.dag?.id === taskflowId);
    }

    return tasks;
}

async function getDagEdges(taskflowId: string) {
    if (!taskflowId) {
        return [];
    }

    const dagInfo = await DagService.getDagInfo(taskflowId);
    return dagInfo.edges;
}

// avoid using reference objects (Array, Object) from search params for memoized values
function computeColumnFields(searchParams: URLSearchParams): string {
    const columnFields = searchParams.getAll("columnField");
    return columnFields.toString();
}

// avoid using reference objects (Array, Object) from search params for memoized values
function computeLoadFields(searchParams: URLSearchParams): string {
    const loadFields = searchParams.getAll("loadField");
    return loadFields.toString();
}

function computeColumns(columnFieldString: string) {
    if (!columnFieldString) {
        return COLUMNS;
    }

    const columnFields = TableDataUtility.createColumns<Task>(
        columnFieldString.split(",").map((accessor) => ({
            id: accessor,
        }))
    );

    return [...COLUMNS, ...columnFields];
}

function computeDialogFields(tasks: Task[]): {
    label: string;
    text: string;
}[] {
    const userIds = [...new Set(tasks.map((task) => task.userId))].join(", ");
    return [
        { label: "Tasks", text: tasks.length.toString() },
        {
            label: "Affected Users",
            text: userIds,
        },
    ];
}

function DialogContent({
    action,
    dialogFields,
}: {
    action: string;
    dialogFields: {
        label: string;
        text: string;
    }[];
}) {
    return (
        <div nve-layout="column gap:xxl">
            <div nve-text="heading">
                You are about to <strong nve-text="capitalize">{action}</strong>{" "}
                the following tasks.
            </div>
            <div nve-layout="column gap:sm">
                {dialogFields.map(({ label, text }) => (
                    <div key={label} nve-layout="grid gap:md">
                        <div nve-layout="row span:3 align:right">{`${label}:`}</div>
                        <div
                            title={text}
                            nve-layout="span:9"
                            nve-text="truncate"
                        >
                            {text}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

const TaskTableComponent = DataTable<Task>;
const TaskTableToolbar = DataTableToolbar<Task>;

function TaskTable({
    title,
    batchId,
    taskflowId,
}: {
    title: string;
    batchId?: string;
    taskflowId?: string;
}) {
    // state
    const { userId } = useUserContext();
    const [selectedAction, setSelectedAction] = useState<string>("");
    const [searchParams] = useSearchParams();
    const [showDagGraph, setShowDagGraph] = useState(false);
    const taskDataFetcher = useDataFetcher(getAllTasks);
    const dagEdgesFetcher = useDataFetcher(getDagEdges);
    const tableSearchParams = useTableSearchParams({
        defaultColumns,
    });
    const columnFieldString = useMemo(
        () => computeColumnFields(searchParams),
        [searchParams]
    );
    const columns = useMemo(
        () => computeColumns(columnFieldString),
        [columnFieldString]
    );
    const tasks = useMemo(
        () => taskDataFetcher.data?.map((task) => task) ?? [],
        [taskDataFetcher.data]
    );
    const dagGraphTasks = useMemo(
        () => (taskflowId ? tasks : []),
        [tasks, taskflowId]
    );
    const dagGraphEdges = useMemo(
        () => dagEdgesFetcher.data ?? [],
        [dagEdgesFetcher.data]
    );
    const rowData = useRowData({
        query: tableSearchParams.query,
        config: columns,
        rows: tasks,
    });
    const bulkSelect = useBulkSelect(rowData.data.filteredRows);
    const bulkAction = useDataFetcher(onBulkAction);
    const { nodes, edges, onNodesChange, onEdgesChange, onConnect } =
        useGraphData({
            dagEdges: dagGraphEdges,
            tasks: dagGraphTasks,
            orientation: "horizontal",
        });
    // derived state
    const loadFieldString = useMemo(
        () => computeLoadFields(searchParams),
        [searchParams]
    );
    const loadFields = useMemo(
        () => loadFieldString.split(",").filter(Boolean),
        [loadFieldString]
    );
    const loading = useMemo(
        () => taskDataFetcher.loading || bulkAction.loading,
        [taskDataFetcher.loading, bulkAction.loading]
    );
    const selectedTasks = useMemo(
        () =>
            rowData.data.filteredRows
                .filter((row) => bulkSelect.selectedRows.has(row.id))
                .map((row) => row.data) as Task[],
        [rowData.data.filteredRows, bulkSelect.selectedRows]
    );

    const dialogFields = useMemo(
        () => computeDialogFields(selectedTasks),
        [selectedTasks]
    );

    // callbacks
    const fetchTaskData = taskDataFetcher.fetchData;
    const fetchTasksCallback = useCallback(
        () => fetchTaskData(loadFields, batchId, taskflowId),
        [fetchTaskData, loadFields, batchId, taskflowId]
    );

    const fetchBulkActionData = bulkAction.fetchData;
    const clearBulkSelect = bulkSelect.clear;
    const onSubmitBulkAction = useCallback(async () => {
        await fetchBulkActionData({
            action: selectedAction,
            selected: selectedTasks.map((task) => task.id),
            userId: userId as string,
        });
        await fetchTasksCallback();
        setSelectedAction("");
        clearBulkSelect();
    }, [
        fetchTasksCallback,
        fetchBulkActionData,
        userId,
        selectedTasks,
        selectedAction,
        clearBulkSelect,
    ]);

    const renderMetadata = useCallback(
        () => <Metadata rows={rowData.data.filteredRows} />,
        [rowData.data.filteredRows]
    );

    useEffect(() => {
        fetchTasksCallback();
    }, [fetchTasksCallback]);

    const fetchDagEdges = dagEdgesFetcher.fetchData;
    useEffect(() => {
        if (taskflowId) {
            fetchDagEdges(taskflowId);
        }
    }, [fetchDagEdges, taskflowId]);

    return (
        <DataTableContentLoader loading={loading} stretch={showDagGraph}>
            {selectedAction && (
                <Dialog
                    title={`confirm ${selectedAction} tasks`}
                    onClose={() => setSelectedAction("")}
                    onSubmit={onSubmitBulkAction}
                >
                    <DialogContent
                        action={selectedAction}
                        dialogFields={dialogFields}
                    />
                </Dialog>
            )}
            <DataTablePageHeader
                title={title}
                onClickRefresh={fetchTasksCallback}
                lastUpdated={taskDataFetcher.lastUpdated}
                renderMetadata={renderMetadata}
            />
            <DataTableFilterBar
                filters={tableSearchParams.query.filters}
                onSearch={tableSearchParams.setSearch}
                defaultValue={tableSearchParams.query.search}
                onFilter={tableSearchParams.setFilter}
                onClear={tableSearchParams.clear}
                label="search"
            />
            <div nve-layout="row align:center gap:sm" style={{ width: "100%" }}>
                <TaskTableToolbar
                    config={columns}
                    columns={tableSearchParams.query.columns}
                    onColumnChange={tableSearchParams.setColumn}
                    bulkActionItems={bulkActionItems}
                    selectedRows={bulkSelect.selectedRows}
                    onSubmitBulkAction={setSelectedAction}
                    onCloseBulkSelect={bulkSelect.clear}
                />
                {taskflowId && (
                    <nve-icon-button
                        icon-name="branch"
                        pressed={showDagGraph}
                        onClick={() => setShowDagGraph(!showDagGraph)}
                    ></nve-icon-button>
                )}
            </div>
            {showDagGraph ? (
                <DagGraph
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                />
            ) : (
                <TaskTableComponent
                    allSelected={bulkSelect.allSelected}
                    config={columns}
                    data={rowData.data}
                    query={tableSearchParams.query}
                    onPageChange={tableSearchParams.setPage}
                    onStepChange={tableSearchParams.setStep}
                    onFilterChange={tableSearchParams.setFilter}
                    onSortChange={tableSearchParams.setSort}
                    selectedRows={bulkSelect.selectedRows}
                    onClickSelectAll={bulkSelect.toggleAll}
                    onClickSelectRow={bulkSelect.toggleRow}
                />
            )}
        </DataTableContentLoader>
    );
}

export { TaskTable };
