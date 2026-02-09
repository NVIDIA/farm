// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useMemo } from "react";
import { Link } from "react-router";
import type { RowData } from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { JobDefinition, JobsService } from "~/library/jobs-service";
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
        id: "name",
        renderCell: ({ data }: RowData<JobDefinition>) => (
            <Link to={`/job/${data.name}`}>{data.name}</Link>
        ),
    },
    { id: "task_function", headerText: "function" },
    { id: "job_type", headerText: "type" },
    { id: "container" },
]);

const JobsTableComponent = DataTable<JobDefinition>;
const JobsTableToolbar = DataTableToolbar<JobDefinition>;
function Jobs() {
    const { data, loading, fetchData, lastUpdated } = useDataFetcher(
        JobsService.getAll
    );
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
                title="Jobs"
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
            <JobsTableToolbar
                config={COLUMNS}
                columns={tableSearchParams.query.columns}
                onColumnChange={tableSearchParams.setColumn}
            />
            <JobsTableComponent
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

export { Jobs };
