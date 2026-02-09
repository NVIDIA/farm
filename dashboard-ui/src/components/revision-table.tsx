// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Local library
import { type Revision } from "../library/task-service";
import type { ColumnConfig, RowData } from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";
import { useRowData } from "~/hooks/row-data";
import { useTableSearchParams } from "~/hooks/table-search-params";
import type { JSX } from "react";
import { useMemo } from "react";

// Local
import { TaskProgressBar } from "./task-progress-bar";
import {
    DataTable,
    DataTableContentLoader,
    DataTableFilterBar,
    DataTableToolbar,
} from "./data-table";

interface RevisionProps {
    revisions?: Revision[];
}

const COLUMNS: ColumnConfig<Revision> =
    TableDataUtility.createColumns<Revision>([
        { id: "timeDateString" },
        { id: "status" },
        { id: "agentId" },
        { id: "userId" },
        {
            id: "progress",
            renderCell: ({ data }: RowData<Revision>) => {
                return (
                    <TaskProgressBar
                        progress={data.progress?.progress}
                        status={data.status}
                    />
                );
            },
        },
    ]);

const RevisionTableComponent = DataTable<Revision>;
const RevisionTableToolbar = DataTableToolbar<Revision>;

function RevisionTable(props: RevisionProps): JSX.Element {
    const { revisions } = props;
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
        rows: revisions || [],
    });

    return (
        <DataTableContentLoader>
            <DataTableFilterBar
                filters={tableSearchParams.query.filters}
                onSearch={tableSearchParams.setSearch}
                defaultValue={tableSearchParams.query.search}
                onFilter={tableSearchParams.setFilter}
                onClear={tableSearchParams.clear}
                label="search"
            />
            <RevisionTableToolbar
                config={COLUMNS}
                columns={tableSearchParams.query.columns}
                onColumnChange={tableSearchParams.setColumn}
            />
            <RevisionTableComponent
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

export { RevisionTable };
