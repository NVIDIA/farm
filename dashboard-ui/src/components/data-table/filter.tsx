// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";
// using native custom elements
import { useId } from "react";
import { useDebouncedCallback } from "use-debounce";
import type { Column, ColumnType } from "~/utilities/table-data-utility";
import { Date } from "~/components/date";
import { Input } from "~/components/input";
import { MultiSelect } from "~/components/multi-select";

interface FilterProps<T = unknown> {
    column: Column<T>;
    defaultValue?: string;
    onFilter: (key: string, value: string) => void;
}

function DateFilter<T>({
    defaultValue = "=>",
    onFilter,
    column,
}: FilterProps<T>) {
    const [start, end] = defaultValue.split("=>");

    return (
        <div nve-layout="row align:vertical-center">
            <nve-input-group>
                <Date
                    name={`${column.id}-start-date`}
                    defaultValue={start}
                    max={end}
                    onChange={(event) =>
                        onFilter(column.id, `${event}=>${end}`)
                    }
                    label="start"
                />
                <Date
                    name={`${column.id}-end-date`}
                    defaultValue={end}
                    min={start}
                    onChange={(event) =>
                        onFilter(column.id, `${start}=>${event}`)
                    }
                    label="end"
                />
            </nve-input-group>
        </div>
    );
}

function TextFilter<T>({
    defaultValue = "",
    onFilter,
    column,
}: FilterProps<T>) {
    const debounce = useDebouncedCallback((value) => {
        onFilter(column.id, value.trim());
    }, 500);

    return (
        <nve-toolbar container="flat">
            <nve-icon-button
                readonly
                icon-name="filter"
                container="flat"
                slot="prefix"
            ></nve-icon-button>
            <Input
                name={`${column.id}-text`}
                onChange={(value) => debounce(value)}
                placeholder="Add Filter"
                defaultValue={defaultValue}
            />
        </nve-toolbar>
    );
}

function MultiSelectFilter<T>({
    defaultValue = "",
    onFilter,
    column,
}: FilterProps<T>) {
    const values = defaultValue.split("|").filter(Boolean);
    const items = column.filterItems || [];

    return (
        <MultiSelect
            items={items}
            defaultValue={values}
            onChange={(nextSelected) => {
                onFilter(column.id, nextSelected.join("|"));
            }}
        />
    );
}

type ColumnFilter = <T>(props: FilterProps<T>) => JSX.Element;
type ColumnFilterMap = { [key in ColumnType]: ColumnFilter };

const columnFilterMap: ColumnFilterMap = {
    DATE: DateFilter,
    TEXT: TextFilter,
    MULTI_SELECT: MultiSelectFilter,
};

function getColumnFilter<T>(column: Column<T>) {
    return columnFilterMap[column.type];
}

export default function Filter<T>({
    column,
    defaultValue,
    onFilter,
}: FilterProps<T>) {
    const id = useId();
    const ColumnFilter = getColumnFilter<T>(column);

    return (
        <>
            <nve-icon-button
                type="button"
                slot="actions"
                icon-name="filter"
                size="sm"
                container="flat"
                popovertarget={`${id}-${column.id}`}
            ></nve-icon-button>
            <nve-dropdown id={`${id}-${column.id}`}>
                <ColumnFilter
                    column={column}
                    defaultValue={defaultValue}
                    onFilter={onFilter}
                />
            </nve-dropdown>
        </>
    );
}
