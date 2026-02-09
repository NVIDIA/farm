// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ColumnConfig, RowData } from "~/utilities/table-data-utility";
import Cell from "./cell";
import Pagination from "./pagination";
import { GridColumn } from "./grid-column";
import { useId, useMemo } from "react";
import type { IconName } from "@nve/elements";
import type { Query } from "~/hooks/table-search-params";

type Sort = Query["sort"];

function Checkbox({
    checked = false,
    onClick,
}: {
    checked?: boolean;
    onClick: () => void;
}) {
    return (
        <nve-checkbox>
            <input
                type="checkbox"
                checked={checked}
                readOnly
                onClick={() => onClick()}
            />
        </nve-checkbox>
    );
}

function ActionMenu({
    items,
    onClick,
}: {
    items: { label: string; value: string; iconName: IconName }[];
    onClick?: (value: string) => void;
}) {
    const id = useId();
    return (
        <>
            <nve-icon-button
                container="flat"
                icon-name="more-actions"
                size="md"
                popovertarget={`action-${id}`}
            />
            <nve-dropdown id={`action-${id}`} alignment="end">
                <nve-menu>
                    {items.map((item) => (
                        <nve-menu-item
                            key={item.label}
                            onClick={() => onClick?.(item.value)}
                        >
                            {item.iconName ? (
                                <nve-icon name={item.iconName} />
                            ) : null}
                            {item.iconName ? " " : ""}
                            {item.label}
                        </nve-menu-item>
                    ))}
                </nve-menu>
            </nve-dropdown>
        </>
    );
}

interface DataTableProps<T> {
    allSelected?: boolean;
    config: ColumnConfig<T>;
    data: {
        rows: RowData<T>[];
        filteredRows: RowData<T>[];
        totalResults: number;
    };
    query: Query;
    onPageChange: (page: number) => void;
    onStepChange: (step: number) => void;
    onFilterChange: (key: string, value: string) => void;
    onSortChange: (sort: Sort) => void;
    rowActionItems?: { label: string; value: string; iconName: IconName }[];
    selectedRows?: Set<string>;
    onClickSelectAll?: () => void;
    onClickSelectRow?: (row: RowData<T>) => void;
    onSubmitRowAction?(action: string, row: RowData<T>): void;
}

function DataTable<T>({
    allSelected,
    config,
    data,
    query,
    onPageChange,
    onStepChange,
    onFilterChange,
    onSortChange,
    rowActionItems = [],
    selectedRows,
    onClickSelectAll = () => {},
    onClickSelectRow = () => {},
    onSubmitRowAction = () => {},
}: DataTableProps<T>) {
    const actionMenu = !!rowActionItems.length;
    const { columns } = query;
    const selectedColumns = useMemo(() => new Set(columns), [columns]);
    const activeColumns = useMemo(
        () => config.filter((column) => selectedColumns.has(column.id)),
        [selectedColumns, config]
    );
    const hasBulkSelect = useMemo(
        () =>
            selectedRows != null &&
            onClickSelectAll != null &&
            onClickSelectRow != null &&
            allSelected != null,
        [selectedRows, onClickSelectAll, onClickSelectRow, allSelected]
    );

    return (
        <div nve-layout="full">
            <div nve-layout="row align:right pad-y:xs pad-x:sm">
                <Pagination
                    page={query.page}
                    step={query.step}
                    totalResults={data.totalResults}
                    onPage={onPageChange}
                    onStep={onStepChange}
                />
            </div>
            <nve-grid stripe>
                <nve-grid-header>
                    {hasBulkSelect && (
                        <nve-grid-column width="max-content" position="fixed">
                            <Checkbox
                                checked={allSelected}
                                onClick={onClickSelectAll}
                            />
                        </nve-grid-column>
                    )}
                    {activeColumns.map((c) => (
                        <GridColumn<T>
                            column={c}
                            key={c.id}
                            filters={query.filters}
                            sort={query.sort}
                            onFilter={onFilterChange}
                            onSort={onSortChange}
                        />
                    ))}
                    {actionMenu && (
                        <nve-grid-column width="max-content" position="fixed" />
                    )}
                </nve-grid-header>
                {data.rows.map((r) => {
                    return (
                        <nve-grid-row key={r.id}>
                            {hasBulkSelect && (
                                <nve-grid-cell>
                                    <Checkbox
                                        checked={selectedRows?.has(r.id)}
                                        onClick={() => onClickSelectRow(r)}
                                    />
                                </nve-grid-cell>
                            )}
                            {activeColumns.map((c) => (
                                <Cell key={c.id} row={r} column={c} />
                            ))}
                            {actionMenu && (
                                <nve-grid-cell>
                                    <ActionMenu
                                        items={rowActionItems}
                                        onClick={(action) =>
                                            onSubmitRowAction(action, r)
                                        }
                                    />
                                </nve-grid-cell>
                            )}
                        </nve-grid-row>
                    );
                })}
                <nve-grid-footer>
                    <Pagination
                        page={query.page}
                        step={query.step}
                        totalResults={data.totalResults}
                        onPage={onPageChange}
                        onStep={onStepChange}
                    />
                </nve-grid-footer>
            </nve-grid>
        </div>
    );
}

export { DataTable };
