// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useMemo } from "react";
import { Link } from "react-router";
import type { RowData } from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { Batch, TaskService } from "~/library/task-service";
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
        renderCell: ({ data }: RowData<Batch>) => (
            <Link to={`/batch/${data.id}`}>{data.id}</Link>
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

const getBatches = () => TaskService.getBatches();
const BatchesTableComponent = DataTable<Batch>;
const BatchesTableToolbar = DataTableToolbar<Batch>;
function Batches() {
    const { data, loading, fetchData, lastUpdated } =
        useDataFetcher(getBatches);
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
                title="Batches"
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
            <BatchesTableToolbar
                config={COLUMNS}
                columns={tableSearchParams.query.columns}
                onColumnChange={tableSearchParams.setColumn}
            />
            <BatchesTableComponent
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

export { Batches };
