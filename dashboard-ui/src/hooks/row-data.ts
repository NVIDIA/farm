// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useMemo } from "react";
import type { Query } from "~/hooks/table-search-params";
import type { ColumnConfig } from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";

function useRowData<T>({
    query,
    config,
    rows,
}: {
    query: Query;
    config: ColumnConfig<T>;
    rows: T[];
}) {
    const rowData = useMemo(
        () => TableDataUtility.createRowData<T>(rows),
        [rows]
    );
    const { filters, search, page, step, sort } = query;
    const filteredRows = useMemo(
        () =>
            TableDataUtility.filterTableData<T>(
                rowData,
                config,
                filters,
                search
            ),
        [rowData, config, filters, search]
    );
    const sortedRows = useMemo(
        () =>
            TableDataUtility.sortTableData<T>({
                rows: filteredRows,
                sort,
                columns: config,
            }),
        [filteredRows, config, sort]
    );
    const paginatedRows = useMemo(
        () => TableDataUtility.paginateTableData<T>(sortedRows, page, step),
        [sortedRows, page, step]
    );
    const data = useMemo(
        () => ({
            rows: paginatedRows,
            filteredRows: filteredRows,
            totalResults: filteredRows.length,
        }),
        [filteredRows, paginatedRows]
    );

    return { data };
}

export { useRowData };
