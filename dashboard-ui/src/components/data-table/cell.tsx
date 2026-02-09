// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";
import type {
    Column,
    ColumnType,
    RowData,
} from "~/utilities/table-data-utility";
import { TableDataUtility } from "~/utilities/table-data-utility";
import { TimeUtility } from "~/utilities/time-utility";

function RowCell({ value }: { value: string }) {
    return (
        <div
            style={{
                whiteSpace: "pre-wrap",
                wordBreak: "break-all",
            }}
        >
            {value}
        </div>
    );
}

function renderTextCell<T>(column: Column<T>, row: RowData<T>) {
    const value = TableDataUtility.getRowValue(column, row);
    return <RowCell value={String(value)} />;
}

function renderDateCell<T>(column: Column<T>, row: RowData<T>) {
    const value = TableDataUtility.getRowDateValue(column, row);
    const valueToRender =
        value == null ? "N/A" : TimeUtility.getLocaleString(value);
    return <RowCell value={valueToRender} />;
}

const cellComponentMap: {
    [key in ColumnType]: <T>(column: Column<T>, row: RowData<T>) => JSX.Element;
} = {
    DATE: renderDateCell,
    TEXT: renderTextCell,
    MULTI_SELECT: renderTextCell,
};

function renderCell<T>(column: Column<T>, row: RowData<T>) {
    return column.renderCell
        ? column.renderCell(row)
        : cellComponentMap[column.type](column, row);
}

export default function Cell<T>({
    row,
    column,
}: {
    column: Column<T>;
    row: RowData<T>;
}) {
    return <nve-grid-cell>{renderCell<T>(column, row)}</nve-grid-cell>;
}
