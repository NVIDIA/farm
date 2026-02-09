// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Column, Filters, Sort } from "~/utilities/table-data-utility";
import SortButton from "./sort-button";
import Filter from "./filter";

export function GridColumn<T>({
    column,
    filters,
    sort,
    onFilter,
    onSort,
}: {
    column: Column<T>;
    filters: Filters;
    sort: Sort;
    onFilter: (key: string, value: string) => void;
    onSort: (sort: Sort) => void;
}) {
    const sortable = column.sortable == null ? true : column.sortable;
    const filterable = column.filterable == null ? true : column.filterable;
    const headerText = column.headerText;

    return (
        <nve-grid-column>
            {headerText.toUpperCase()}
            {sortable && (
                <SortButton column={column} sort={sort} onSort={onSort} />
            )}
            {filterable && (
                <Filter
                    column={column}
                    defaultValue={filters[column.id]}
                    onFilter={onFilter}
                />
            )}
        </nve-grid-column>
    );
}
