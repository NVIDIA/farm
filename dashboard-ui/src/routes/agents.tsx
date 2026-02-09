// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useEffect, useMemo } from "react";
import { Link } from "react-router";
import type { RowData } from "~/utilities/table-data-utility";
import RandomColorTag from "~/components/random-color-tag";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { Agent, AgentService } from "~/library/agent-service";
import { useRowData } from "~/hooks/row-data";
import { useTableSearchParams } from "~/hooks/table-search-params";
import { useBulkSelect } from "~/hooks/bulk-select";
import { TableDataUtility } from "~/utilities/table-data-utility";
import {
    DataTable,
    DataTableContentLoader,
    DataTableFilterBar,
    DataTablePageHeader,
    DataTableToolbar,
} from "~/components/data-table";

const COLUMNS = TableDataUtility.createColumns([
    { id: "id" },
    { id: "status" },
    {
        id: "labels",
        renderCell: ({ data }: RowData<Agent>) => {
            return (
                <div nve-layout="column gap:xs">
                    {data.labels.map((label) => (
                        <RandomColorTag key={label} label={label} />
                    ))}
                </div>
            );
        },
    },
    {
        id: "taskTypes",
        renderCell: ({ data }: RowData<Agent>) => {
            return (
                <div nve-layout="column gap:xs">
                    {data.taskTypes.map(([job]) => (
                        <Link key={job} to={`/job/${job}`}>
                            {job}
                        </Link>
                    ))}
                </div>
            );
        },
    },
    { id: "elapsedCheckinTime" },
    {
        id: "tasks",
        renderCell: ({ data }: RowData<Agent>) => {
            return (
                <div nve-layout="column gap:xs">
                    {data.tasks.map((task) => (
                        <Link key={task} to={`/task/${task}`}>
                            {task}
                        </Link>
                    ))}
                </div>
            );
        },
    },
]);

const BULK_ACTIONS = [
    {
        label: "Evict",
        value: "evict",
    },
    {
        label: "Enable",
        value: "enable",
    },
    {
        label: "Remove",
        value: "remove",
    },
];

const bulkActionMap = {
    remove: (ids: string[]) =>
        Promise.all(ids.map((id) => AgentService.remove(id))),
    evict: (ids: string[]) =>
        Promise.all(ids.map((id) => AgentService.evict(id))),
    enable: (ids: string[]) =>
        Promise.all(ids.map((id) => AgentService.enable(id))),
};

function postBulkAction(action: string, ids: string[]) {
    return bulkActionMap[action as keyof typeof bulkActionMap](ids);
}

const AgentsTableComponent = DataTable<Agent>;
const AgentsTableToolbar = DataTableToolbar<Agent>;
function Agents() {
    const agentDataFetcher = useDataFetcher(AgentService.getAll);
    const bulkActionFetcher = useDataFetcher(postBulkAction);
    const defaultColumns = useMemo(
        () => COLUMNS.map((column) => column.id),
        []
    );
    const tableSearchParams = useTableSearchParams({
        defaultColumns,
    });
    const rowData = useRowData({
        query: tableSearchParams.query,
        config: COLUMNS,
        rows: agentDataFetcher.data || [],
    });
    const bulkSelect = useBulkSelect(rowData.data.filteredRows);
    const selectedRowData = useMemo(
        () =>
            rowData.data.filteredRows
                .filter((row) => bulkSelect.selectedRows.has(row.id))
                .map((row) => row.data as Agent),
        [rowData.data.filteredRows, bulkSelect.selectedRows]
    );

    const loading = useMemo(
        () => agentDataFetcher.loading || bulkActionFetcher.loading,
        [agentDataFetcher.loading, bulkActionFetcher.loading]
    );

    const clearBulkSelect = bulkSelect.clear;
    const fetchAgentData = agentDataFetcher.fetchData;
    const postBulkActionData = bulkActionFetcher.fetchData;
    const onSubmitBulkAction = useCallback(
        async (action: string) => {
            const ids = selectedRowData.map((agent) => agent.id);
            await postBulkActionData(action, ids);
            await fetchAgentData();
            clearBulkSelect();
        },
        [fetchAgentData, postBulkActionData, selectedRowData, clearBulkSelect]
    );

    useEffect(() => {
        fetchAgentData();
    }, [fetchAgentData]);

    return (
        <DataTableContentLoader loading={loading}>
            <DataTablePageHeader
                title="Agents"
                onClickRefresh={fetchAgentData}
                lastUpdated={agentDataFetcher.lastUpdated}
            />
            <DataTableFilterBar
                filters={tableSearchParams.query.filters}
                onSearch={tableSearchParams.setSearch}
                defaultValue={tableSearchParams.query.search}
                onFilter={tableSearchParams.setFilter}
                onClear={tableSearchParams.clear}
                label="search"
            />
            <AgentsTableToolbar
                config={COLUMNS}
                columns={tableSearchParams.query.columns}
                onColumnChange={tableSearchParams.setColumn}
                bulkActionItems={BULK_ACTIONS}
                selectedRows={bulkSelect.selectedRows}
                onSubmitBulkAction={onSubmitBulkAction}
                onCloseBulkSelect={bulkSelect.clear}
            />
            <AgentsTableComponent
                allSelected={bulkSelect.allSelected}
                config={COLUMNS}
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
        </DataTableContentLoader>
    );
}

export { Agents };
