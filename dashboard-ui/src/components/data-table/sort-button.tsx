// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Column } from "~/utilities/table-data-utility";
import type { Sort } from "~/utilities/table-data-utility";

const sortDirections = ["none", "asc", "desc"];
const sortDirectionMap = {
    asc: "ascending",
    desc: "descending",
    none: "none",
} as const;

export default function SortButton<T>({
    column,
    sort,
    onSort,
}: {
    column: Column<T>;
    sort: Sort;
    onSort: (sort: { sortBy: string; sortDirection: string }) => void;
}) {
    const sortDirection =
        column.id === sort.sortBy ? sort.sortDirection : "none";
    const nextSortDirection =
        sortDirections[sortDirections.indexOf(sortDirection) + 1] || "none";

    return (
        <nve-sort-button
            sort={
                sortDirectionMap[sortDirection as keyof typeof sortDirectionMap]
            }
            slot="actions"
            onClick={() =>
                onSort({ sortBy: column.id, sortDirection: nextSortDirection })
            }
        />
    );
}
