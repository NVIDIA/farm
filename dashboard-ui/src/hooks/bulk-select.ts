// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useEffect, useMemo, useState } from "react";

interface BulkSelectRow {
    id: string;
}

function useBulkSelect(rows: BulkSelectRow[]) {
    // state
    const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());

    // derived state
    const rowKeys = useMemo(() => rows.map((r) => r.id).join("|"), [rows]);
    const allSelected = useMemo(
        () => !!(selectedRows?.size && selectedRows?.size === rows.length),
        [selectedRows, rows]
    );

    // callbacks
    const toggleRow = useCallback(
        (row: BulkSelectRow) => {
            const nextSelectedRows = new Set(selectedRows);

            if (nextSelectedRows.has(row.id)) {
                nextSelectedRows.delete(row.id);
            } else {
                nextSelectedRows.add(row.id);
            }

            setSelectedRows(nextSelectedRows);
        },
        [selectedRows]
    );

    const toggleAll = useCallback(() => {
        if (allSelected) {
            setSelectedRows(new Set());
            return;
        }

        setSelectedRows(new Set(rows.map((row) => row.id)));
    }, [allSelected, rows]);

    const clear = useCallback(() => {
        setSelectedRows(new Set());
    }, []);

    // effects
    useEffect(() => {
        setSelectedRows(new Set());
    }, [rowKeys]);

    return { selectedRows, allSelected, toggleRow, toggleAll, clear };
}

export { useBulkSelect };
