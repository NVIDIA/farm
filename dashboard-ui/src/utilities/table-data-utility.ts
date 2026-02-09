// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";
import { StringUtility } from "~/utilities/string-utility";
import { TimeUtility } from "~/utilities/time-utility";

export interface RowData<T = unknown> {
    id: string;
    data: T;
}

// Every column has a type so the utility knows how to filter,
// parse its row value, sort it, and stringify it for display.
// If these types are insufficient, add a new type and its
// associated functions.
export type ColumnType = "TEXT" | "MULTI_SELECT" | "DATE";

// A column is the configuration for a table field. It defines how to
// render the column and how to filter, parse, sort, and stringify
// its row value based on its type.
export interface Column<T = unknown> {
    id: string;
    accessor: string;
    type: ColumnType;
    headerText: string;
    sortable: boolean;
    filterable: boolean;
    filterItems?: { label: string; value: string }[];
    renderCell?: (row: RowData<T>) => JSX.Element;
}

export type ColumnConfig<T = unknown> = readonly Column<T>[];

// Filters are string values, typically sourced from search params.
// Keys must match column ids; values are the column's filter input.
export interface Filters {
    [key: string]: string;
}

type FilterFn<T> = (
    column: Column<T>,
    filterValue: string
) => (row: RowData<T>) => boolean;

export interface Sort {
    sortBy: string;
    sortDirection: string;
}

export type RowFilterFn<T> = (row: RowData<T>) => boolean;

// Helper to safely perform object operations while retaining generic typing.
function isNonNullishObject(
    value: unknown
): value is { [key: string]: unknown } {
    return !!(value && typeof value === "object");
}

// Helper to get the last path segment, used for dynamic column headers.
function lastSegment(path: string): string {
    const parts = path.split(".").filter(Boolean);
    return parts[parts.length - 1] || path;
}

// Each column type has a value-level filter.
// Column filters parse the string filter input and pass the correct
// operands to these value filters.
const TableDataValueFilter = {
    filterTextValue(value: string, filterValue: string) {
        return String(value).includes(filterValue);
    },
    filterDateValue(value: Date, start: Date, end: Date) {
        return value >= start && value <= end;
    },
    filterMultiSelectValue(value: string, filterValueSet: Set<string>) {
        return filterValueSet.has(value);
    },
};

// Extract the value for a column from a row using the column's accessor.
const TableDataRowParser = {
    parseRowDateValue<T>(column: Column<T>, row: RowData<T>) {
        const value = this.parseRowValue(column, row);

        if (value instanceof Date) {
            return value;
        }

        return null;
    },
    parseRowStringValue<T>(column: Column<T>, row: RowData<T>) {
        const value = this.parseRowValue(column, row);

        if (typeof value === "string") {
            return value;
        }

        return null;
    },
    parseRowValue<T>(column: Column<T>, row: RowData<T>): unknown {
        const keys = column.accessor.split(".").filter(Boolean);

        if (keys.length === 0) {
            return null;
        }

        let value: unknown = row.data;

        keys.forEach((key) => {
            if (isNonNullishObject(value) && key in value) {
                value = value[key];
            } else {
                value = null;
            }
        });

        return value;
    },
};

// Column-aware filters. Each function defines the inputs needed to
// evaluate whether a row matches a column's filter.
const TableDataColumnFilter = {
    filterTextColumn<T>(
        column: Column<T>,
        row: RowData<T>,
        filterValue: string
    ): boolean {
        if (!filterValue) {
            return true;
        }

        const rowValue = TableDataRowParser.parseRowStringValue(column, row);

        if (rowValue == null) {
            return false;
        }

        return TableDataValueFilter.filterTextValue(rowValue, filterValue);
    },
    filterDateColumn<T>(
        column: Column<T>,
        row: RowData<T>,
        start: Date,
        end: Date,
        filterValue = "=>"
    ): boolean {
        if (filterValue === "=>" || !filterValue) {
            return true;
        }

        const rowValue = TableDataRowParser.parseRowDateValue(column, row);

        if (rowValue == null) {
            return false;
        }

        return TableDataValueFilter.filterDateValue(rowValue, start, end);
    },
    filterMultiSelectColumn<T>(
        column: Column<T>,
        row: RowData<T>,
        filterValueSet: Set<string>,
        filterValue = ""
    ): boolean {
        if (!filterValue) {
            return true;
        }

        const rowValue = TableDataRowParser.parseRowStringValue(column, row);

        if (rowValue == null) {
            return false;
        }

        return TableDataValueFilter.filterMultiSelectValue(
            rowValue,
            filterValueSet
        );
    },
};

// Function factories that close over the column config and filter input,
// producing row filter functions. This enables composing multiple
// filters into a single row filter.
const TableDataFilterFnCreator = {
    createTextFilterFn<T>(
        column: Column<T>,
        filterValue = ""
    ): (row: RowData<T>) => boolean {
        return (row: RowData<T>) =>
            TableDataColumnFilter.filterTextColumn(column, row, filterValue);
    },
    createDateFilterFn<T>(column: Column<T>, filterValue = "=>") {
        const [startDate, endDate] = filterValue.split("=>");
        let start = TimeUtility.getLocalDateFromISODate(startDate);
        let end = TimeUtility.getLocalDateFromISODate(endDate, true);

        if (!TimeUtility.isValidDate(start)) {
            start = TimeUtility.getNegativeInfinityDate();
        }

        if (!TimeUtility.isValidDate(end)) {
            end = TimeUtility.getInfinityDate();
        }

        return (row: RowData<T>) =>
            TableDataColumnFilter.filterDateColumn(
                column,
                row,
                start,
                end,
                filterValue
            );
    },
    createMultiSelectFilterFn<T>(column: Column<T>, filterValue = "") {
        const filterValues = filterValue.split("|").filter(Boolean);
        const filterValueSet = new Set(filterValues);

        return (row: RowData<T>) =>
            TableDataColumnFilter.filterMultiSelectColumn(
                column,
                row,
                filterValueSet,
                filterValue
            );
    },
    createSearchFilterFn<T>(column: Column<T>, searchFilterValue: string) {
        if (column.type === "TEXT" || column.type === "MULTI_SELECT") {
            return (row: RowData<T>) =>
                TableDataColumnFilter.filterTextColumn(
                    column,
                    row,
                    searchFilterValue
                );
        }

        return null;
    },
};

// Dispatch map from column type to the appropriate filter factory.
const filterFunctionMap = {
    TEXT: <T>(column: Column<T>, filterValue: string) =>
        TableDataFilterFnCreator.createTextFilterFn(column, filterValue),
    DATE: <T>(column: Column<T>, filterValue: string) =>
        TableDataFilterFnCreator.createDateFilterFn<T>(column, filterValue),
    MULTI_SELECT: <T>(column: Column<T>, filterValue: string) =>
        TableDataFilterFnCreator.createMultiSelectFilterFn<T>(
            column,
            filterValue
        ),
};

// Default sentinel values by column type for missing/invalid sort keys
// (e.g., a DATE column with a string value).
const nullValueMap = {
    TEXT: "",
    DATE: new Date(-8640000000000000),
    MULTI_SELECT: "",
};

// Most fields are optional; sensible defaults are applied so the
// presentation layer doesn't need to handle omissions.
interface CreateColumnParams<T = unknown> {
    id: string;
    accessor?: string;
    headerText?: string;
    type?: ColumnType;
    sortable?: boolean;
    filterable?: boolean;
    filterItems?: { label: string; value: string }[];
    renderCell?: (row: RowData<T>) => JSX.Element;
}

const TableDataUtility = {
    createColumn<T = unknown>({
        id,
        accessor,
        headerText,
        type = "TEXT",
        sortable = true,
        filterable = true,
        filterItems,
        renderCell,
    }: CreateColumnParams<T>): Column<T> {
        return {
            id,
            accessor: accessor ?? id,
            headerText:
                headerText ??
                StringUtility.objectKeyToTitleCase(lastSegment(accessor ?? id)),
            type,
            sortable,
            filterable,
            filterItems,
            renderCell,
        };
    },
    // Helper to build a ColumnConfig from partial column definitions.
    createColumns<T = unknown>(
        columns: CreateColumnParams<T>[]
    ): ColumnConfig<T> {
        return columns.map((column) => this.createColumn<T>(column));
    },
    // Look up the correct filter function factory based on column type.
    getFilterFn<T>(column: Column<T>): FilterFn<T> {
        return filterFunctionMap[column.type];
    },
    // For sorting, return the correct sentinel for the column type when the value
    // is null/undefined or of the wrong type (e.g., DATE column with a string).
    getSortValue<T>(
        column: Column<T>,
        row: RowData<T>
    ): Date | string | number {
        const value = TableDataRowParser.parseRowValue(column, row);
        return (value === null ? nullValueMap[column.type] : value) as
            | Date
            | string
            | number;
    },
    getRowValue<T>(column: Column<T>, row: RowData<T>): unknown {
        return TableDataRowParser.parseRowValue<T>(column, row);
    },
    getRowDateValue<T>(column: Column<T>, row: RowData<T>): Date | null {
        return TableDataRowParser.parseRowDateValue<T>(column, row);
    },
    getRowStringValue<T>(column: Column<T>, row: RowData<T>): string | null {
        return TableDataRowParser.parseRowStringValue<T>(column, row);
    },
    // Table rows require a string id for display and features like bulk select.
    // This helper wraps items in RowData<T>, using row.id if present; otherwise,
    // it falls back to the row index.
    createRowData<T>(rows: T[]): RowData<T>[] {
        return rows.map((row: T, idx) => {
            const id = isNonNullishObject(row) && "id" in row ? row.id : idx;
            return {
                id: String(id),
                data: row,
            };
        });
    },
    // Build row filter functions for active column filters,
    // enabling composition into a single row filter.
    getRowFilters<T>(columns: ColumnConfig<T>, filters: Filters) {
        return columns.reduce<RowFilterFn<T>[]>((acc, column) => {
            if (column.id in filters) {
                const filterFn = this.getFilterFn(column);
                acc.push(filterFn(column, filters[column.id]));
            }

            return acc;
        }, []);
    },
    // Build row filter functions for the global search filter,
    // enabling composition with column filters.
    getRowSearchFilters<T>(
        columns: ColumnConfig<T>,
        searchFilterValue: string
    ) {
        return columns.reduce<RowFilterFn<T>[]>((acc, column) => {
            const searchFn = TableDataFilterFnCreator.createSearchFilterFn(
                column,
                searchFilterValue
            );
            // search function will be null for column types that don't allow text search i.e. DATE
            if (searchFn) {
                acc.push(searchFn);
            }
            return acc;
        }, []);
    },
    // Compose column and search filters into a single row filter.
    getTableDataFilters<T>(
        columns: ColumnConfig<T>,
        filters: Filters,
        searchFilterValue: string
    ) {
        return (row: RowData<T>) =>
            this.getRowFilters(columns, filters).every((fn) => fn(row)) &&
            this.getRowSearchFilters(columns, searchFilterValue).some((fn) =>
                fn(row)
            );
    },
    // Filter rows using the composed row filter.
    filterTableData<T>(
        rows: RowData<T>[],
        columns: ColumnConfig<T>,
        filters: Filters,
        searchFilterValue: string
    ) {
        const tableDataFilters = this.getTableDataFilters(
            columns,
            filters,
            searchFilterValue
        );
        return rows.filter(tableDataFilters);
    },
    sortTableData<T>({
        rows,
        sort,
        columns,
    }: {
        rows: RowData<T>[];
        sort: Sort;
        columns: ColumnConfig<T>;
    }) {
        // Find the column to sort by (id match).
        const sortColumn = columns.find((col) => col.id === sort.sortBy);

        if (!sortColumn) {
            return rows;
        }

        // Validate sort direction.
        const sortDirection =
            sort.sortDirection === "asc" || sort.sortDirection === "desc"
                ? sort.sortDirection
                : "";

        // If the column or direction is invalid, return rows unchanged.
        if (!sortColumn || !sortDirection) {
            return rows;
        }

        // Create a new reference to the array to indicate state update.
        // This allows for isolating the sort update instead of combining it with filtering.
        rows = [...rows];

        rows.sort((a, b) => {
            // Get sort values (with sentinels for null/invalid types).
            const first = TableDataUtility.getSortValue(sortColumn, a);
            const second = TableDataUtility.getSortValue(sortColumn, b);

            // Compare sort values and apply direction.
            if (sortDirection === "asc") {
                return first > second ? 1 : first < second ? -1 : 0;
            } else {
                return first < second ? 1 : first > second ? -1 : 0;
            }
        });

        return rows;
    },
    // Apply pagination to reduce work in the presentation layer.
    paginateTableData<T>(rows: RowData<T>[], page: number, step: number) {
        const start = page * step - step;
        const end = page * step;
        return rows.slice(start, end);
    },
    // Stringify the row value for display.
    stringifyRowValue<T>(column: Column<T>, row: RowData<T>) {
        const value = TableDataUtility.getRowValue(column, row);
        const data = value == null ? "N/A" : value;

        if (typeof data === "string") {
            return data;
        } else if (typeof data === "object") {
            return JSON.stringify(data, null, 4);
        }

        return String(data);
    },
} as const;

export { TableDataUtility };
