// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useMemo } from "react";
import { Link } from "react-router";
import type { RowData } from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { Taskflow, TaskService } from "~/library/task-service";
import { useRowData } from "~/hooks/row-data";
import { useTableSearchParams } from "~/hooks/table-search-params";
import {
    DataTable,
    DataTableContentLoader,
    DataTableFilterBar,
    DataTablePageHeader,
    DataTableToolbar,
} from "~/components/data-table";

const COLUMNS = TableDataUtility.createColumns([
    {
        id: "id",
        type: "TEXT",
        renderCell: ({ data }: RowData<Taskflow>) => (
            <Link to={`/taskflow/${data.id}`}>{data.id}</Link>
        ),
    },
    {
        id: "comment",
    },
    {
        id: "taskCount",
    },
    {
        id: "finishedCount",
    },
    {
        id: "errorCount",
    },
    {
        id: "startedDate",
        headerText: "Started At",
        type: "DATE",
    },
]);

const getTaskflows = () => TaskService.getTaskflows();
const TaskflowsTableComponent = DataTable<Taskflow>;
const TaskflowsTableToolbar = DataTableToolbar<Taskflow>;
function Taskflows() {
    const { data, loading, fetchData, lastUpdated } =
        useDataFetcher(getTaskflows);
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
        rows: data || [],
    });

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return (
        <DataTableContentLoader loading={loading}>
            <DataTablePageHeader
                title="Taskflows"
                onClickRefresh={fetchData}
                lastUpdated={lastUpdated}
            />
            <DataTableFilterBar
                filters={tableSearchParams.query.filters}
                onSearch={tableSearchParams.setSearch}
                defaultValue={tableSearchParams.query.search}
                onFilter={tableSearchParams.setFilter}
                onClear={tableSearchParams.clear}
                label="search"
            />
            <TaskflowsTableToolbar
                config={COLUMNS}
                columns={tableSearchParams.query.columns}
                onColumnChange={tableSearchParams.setColumn}
            />
            <TaskflowsTableComponent
                config={COLUMNS}
                data={rowData.data}
                query={tableSearchParams.query}
                onPageChange={tableSearchParams.setPage}
                onStepChange={tableSearchParams.setStep}
                onFilterChange={tableSearchParams.setFilter}
                onSortChange={tableSearchParams.setSort}
            />
        </DataTableContentLoader>
    );
}

export { Taskflows };
