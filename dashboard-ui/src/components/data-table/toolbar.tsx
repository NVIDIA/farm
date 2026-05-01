// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ColumnConfig } from "~/utilities/table-data-utility";
import Settings from "./settings";
import { useMemo } from "react";
import BulkSelectToolbar from "../bulk-select-toolbar";

interface DataTableToolbarProps<T> {
    config: ColumnConfig<T>;
    columns: string[];
    onColumnChange: (id: string, checked: boolean) => void;
    bulkActionItems?: { label: string; value: string }[];
    selectedRows?: Set<string>;
    onSubmitBulkAction?: (action: string) => void;
    onCloseBulkSelect?: () => void;
}

function DataTableToolbar<T>({
    config,
    columns,
    onColumnChange,
    bulkActionItems = [],
    selectedRows,
    onSubmitBulkAction = () => {},
    onCloseBulkSelect = () => {},
}: DataTableToolbarProps<T>) {
    const selectedColumns = useMemo(() => new Set(columns), [columns]);

    return (
        <div
            nve-layout="row align:space-between align:vertical-center gap:sm pad-x:lg"
            style={{ width: "100%" }}
        >
            <BulkSelectToolbar
                visible={!!selectedRows?.size}
                selectedCount={selectedRows?.size ?? 0}
                actions={bulkActionItems}
                onClickAction={onSubmitBulkAction}
                onClose={onCloseBulkSelect}
            />
            <Settings
                columns={config}
                selectedColumns={selectedColumns}
                onColumnChange={onColumnChange}
            />
        </div>
    );
}

export { DataTableToolbar };
