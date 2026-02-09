// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useSearchParams } from "react-router";
import { useCallback, useMemo } from "react";
import type { Filters, Sort } from "~/utilities/table-data-utility";

function computeFilters(searchParams: URLSearchParams) {
    const filters = searchParams.getAll("filter");
    return filters.reduce<Filters>((acc, value) => {
        const [filterId = "", filterValue = ""] = value.split(":");

        if (filterId && filterValue) {
            acc[filterId] = filterValue;
        }

        return acc;
    }, {});
}

function computeSort(searchParams: URLSearchParams) {
    const sort = searchParams.get("sort") || ":";
    const [sortBy = "", sortDirection = ""] = sort.split(":");
    return {
        sortBy,
        sortDirection,
    };
}

function computeColumns(
    searchParams: URLSearchParams,
    defaultColumns: string[]
) {
    const urlColumns = searchParams.getAll("column");
    return urlColumns.length ? urlColumns : defaultColumns;
}

export interface Query {
    filters: Filters;
    sort: Sort;
    search: string;
    page: number;
    step: number;
    columns: string[];
}

interface TableSearchParams {
    query: Query;
    setPage: (page: number) => void;
    setStep: (step: number) => void;
    setSearch: (search: string) => void;
    setFilter: (key: string, value: string) => void;
    setSort: (sort: Sort) => void;
    setColumn: (id: string, active: boolean) => void;
    clear: () => void;
}

interface TableSearchParamsArgs {
    defaultColumns?: string[];
    defaultPage?: number;
    defaultStep?: number;
}

function useTableSearchParams({
    defaultColumns = [],
    defaultPage = 1,
    defaultStep = 20,
}: TableSearchParamsArgs = {}): TableSearchParams {
    // state
    const [searchParams, setSearchParams] = useSearchParams();

    //derived state
    const query = useMemo(
        () => ({
            filters: computeFilters(searchParams),
            sort: computeSort(searchParams),
            search: searchParams.get("search") || "",
            page: parseInt(searchParams.get("page") || defaultPage.toString()),
            step: parseInt(searchParams.get("step") || defaultStep.toString()),
            columns: computeColumns(searchParams, defaultColumns),
        }),
        [searchParams, defaultColumns, defaultPage, defaultStep]
    );

    const { columns, filters } = query;

    // callbacks
    const setField = useCallback(
        (field: string, value: string) => {
            const nextSearchParams = new URLSearchParams(searchParams);
            nextSearchParams.delete(field);
            if (value) {
                nextSearchParams.set(field, value);
            }

            setSearchParams(nextSearchParams);
        },
        [searchParams, setSearchParams]
    );

    const setFilter = useCallback(
        (field: string, value: string) => {
            const nextSearchParams = new URLSearchParams(searchParams);
            nextSearchParams.delete("filter");
            nextSearchParams.delete("page");

            const nextFilters = {
                ...filters,
                [field]: value,
            };

            Object.keys(nextFilters).forEach((filterId) => {
                const filterValue = nextFilters[filterId];

                if (filterValue) {
                    nextSearchParams.append(
                        "filter",
                        `${filterId}:${filterValue}`
                    );
                }
            });

            setSearchParams(nextSearchParams);
        },
        [searchParams, setSearchParams, filters]
    );

    const setSort = useCallback(
        (sort: Sort) => {
            const nextSearchParams = new URLSearchParams(searchParams);
            nextSearchParams.delete("sort");
            nextSearchParams.delete("page");

            if (sort.sortDirection && sort.sortDirection !== "none") {
                nextSearchParams.set(
                    "sort",
                    `${sort.sortBy}:${sort.sortDirection}`
                );
            }

            setSearchParams(nextSearchParams);
        },
        [searchParams, setSearchParams]
    );

    const setColumn = useCallback(
        (id: string, active: boolean) => {
            const nextSearchParams = new URLSearchParams(searchParams);
            nextSearchParams.delete("column");

            columns.forEach((colId) => {
                if (colId !== id) {
                    nextSearchParams.append("column", colId);
                }
            });

            if (active) {
                nextSearchParams.append("column", id);
            }

            setSearchParams(nextSearchParams);
        },
        [searchParams, setSearchParams, columns]
    );

    const setPage = useCallback(
        (value: number) => {
            setField("page", value.toString());
        },
        [setField]
    );

    const setStep = useCallback(
        (value: number) => {
            setField("step", value.toString());
        },
        [setField]
    );

    const setSearch = useCallback(
        (value: string) => {
            setField("search", value);
        },
        [setField]
    );

    const clear = useCallback(() => {
        setSearchParams(new URLSearchParams());
    }, [setSearchParams]);

    return {
        query,
        setPage,
        setStep,
        setSearch,
        setFilter,
        setSort,
        setColumn,
        clear,
    };
}

export { useTableSearchParams };
