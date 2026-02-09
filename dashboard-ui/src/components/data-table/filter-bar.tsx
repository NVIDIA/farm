// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useDebouncedCallback } from "use-debounce";
import { Input } from "~/components/input";
import { useMemo } from "react";
import type { Filters } from "~/utilities/table-data-utility";

interface DataTableFilterBarProps {
    onSearch: (value: string) => void;
    onFilter: (key: string, value: string) => void;
    onClear: () => void;
    filters: Filters;
    label: string;
    defaultValue?: string;
}

function DataTableFilterBar({
    onSearch,
    onFilter,
    onClear,
    defaultValue = "",
    label,
    filters,
}: DataTableFilterBarProps) {
    const items = useMemo(
        () =>
            Object.keys({ ...filters })
                .map((filterId) => ({
                    label: filterId,
                    value: filters[filterId],
                }))
                .filter(({ value }) => value),
        [filters]
    );

    const debounce = useDebouncedCallback((value) => {
        onSearch(value);
    }, 500);

    return (
        <div nve-layout="row" data-testid="FilterBar">
            <nve-toolbar container="flat">
                <nve-icon-button
                    readonly
                    icon-name="filter"
                    container="flat"
                    slot="prefix"
                ></nve-icon-button>
                {items.map(({ label, value }) => (
                    <nve-tag
                        data-testid="nve-tag"
                        key={label}
                        closable
                        color="brand-green"
                        onClick={() => onFilter(label, "")}
                    >
                        {`${label}: ${value}`}
                    </nve-tag>
                ))}
                {defaultValue && (
                    <nve-tag
                        closable
                        color="brand-green"
                        onClick={() => onSearch("")}
                    >
                        {`${label}: ${defaultValue}`}
                    </nve-tag>
                )}
                <Input
                    placeholder="Add Filter"
                    defaultValue={defaultValue}
                    onChange={(value) => debounce(value)}
                />
                <nve-icon-button
                    slot="suffix"
                    icon-name="cancel"
                    onClick={() => onClear()}
                />
            </nve-toolbar>
        </div>
    );
}

export { DataTableFilterBar };
