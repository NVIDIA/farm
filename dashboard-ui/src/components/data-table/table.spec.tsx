// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { render, RenderResult, cleanup } from "vitest-browser-react";
import { BrowserRouter as Router } from "react-router";
import type { ColumnConfig, RowData } from "~/utilities/table-data-utility";
import { userEvent } from "@vitest/browser/context";
import type { IconName } from "@nvidia-elements/core/icon";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { useRowData } from "~/hooks/row-data";
import { useTableSearchParams } from "~/hooks/table-search-params";
import { useCallback, useEffect, useMemo } from "react";
import { useBulkSelect } from "~/hooks/bulk-select";
import { TableDataUtility } from "~/utilities/table-data-utility";
import { DataTableContentLoader } from "./content-loader";
import { DataTablePageHeader } from "./page-header";
import { DataTableFilterBar } from "./filter-bar";
import { DataTableToolbar } from "./toolbar";
import { DataTable } from "./table";

interface Sortable extends Element {
    sort?: "ascending" | "descending" | "none";
}

interface WithRenderRoot extends Element {
    renderRoot: Element;
}

const statusArray = [
    "started",
    "in_progress",
    "completed",
    "failed",
    "pending",
] as const;
type Status = (typeof statusArray)[number];

interface Data {
    id: string;
    created: Date;
    status: Status;
    name: string;
    description: string;
    metadata?: {
        job: {
            job_progress: number;
            job_status: Status;
        };
    };
}

const data: Data[] = [
    {
        id: "7e3c54b9-0569-4bfa-b956-4c61916471fd",
        created: new Date("2024-11-03T10:00:00Z"),
        status: "failed",
        name: "Erica Campos",
        description: "Anyone score option century why.",
        metadata: {
            job: {
                job_progress: 1,
                job_status: "completed",
            },
        },
    },
    {
        id: "de316e6d-2c5e-4a27-bc16-50d1b3edabcd",
        created: new Date("2024-11-08T10:00:00Z"),
        status: "in_progress",
        name: "Heather Brown",
        description: "Policy evening purpose current health do tell.",
    },
    {
        id: "577b34c9-fd75-40f5-80b2-f0fb6a4c5c33",
        created: new Date("2024-11-01T00:00:00Z"),
        status: "in_progress",
        name: "Jon Chavez",
        description: "Play brother history study class sister.",
    },
    {
        id: "693ed2ac-e2d8-40b7-a5e2-99cb966e965c",
        created: new Date("2024-11-10T10:00:00Z"),
        status: "pending",
        name: "Karen Patterson",
        description: "List then simply why cold.",
    },
    {
        id: "1dcb958b-7d3c-4d8a-92ac-dc7fa4214c1f",
        created: new Date("2024-11-13T00:00:00Z"),
        status: "started",
        name: "Mrs. Cynthia Bennett",
        description: "Employee ok hospital security view necessary natural.",
    },
    {
        id: "f8e5d0be-32e0-4afe-a537-eee414ddd9fe",
        created: new Date("2024-11-04T10:00:00Z"),
        status: "pending",
        name: "Michelle Mendoza",
        description: "Son already local.",
        metadata: {
            job: {
                job_progress: 0,
                job_status: "pending",
            },
        },
    },
    {
        id: "0e038173-5281-4535-9ea1-2e5b4791099e",
        created: new Date("2024-11-03T20:00:00Z"),
        status: "started",
        name: "Dr. Melissa Roberts DDS",
        description: "During family body.",
    },
    {
        id: "650f7071-2abb-491f-a522-a0dd1d71ab79",
        created: new Date("2024-11-08T00:00:00Z"),
        status: "started",
        name: "Rebekah Fox",
        description: "Risk man as rich.",
    },
    {
        id: "b3cdbeb8-6549-40c0-af07-49f36f04420c",
        created: new Date("2024-11-07T00:00:00Z"),
        status: "failed",
        name: "Casey Anderson",
        description: "Fact less goal vote box change.",
        metadata: {
            job: {
                job_progress: 0.5,
                job_status: "failed",
            },
        },
    },
    {
        id: "5c465da9-c832-4eea-ac3f-c314fa1efdfb",
        created: new Date("2024-11-15T00:00:00Z"),
        status: "completed",
        name: "Chloe Flores",
        description: "Response each cut black.",
    },
    {
        id: "b0d33a60-b297-4b79-b9f5-bfb14d1fb9a5",
        created: new Date("2024-11-03T00:00:00Z"),
        status: "pending",
        name: "Warren Flynn",
        description: "Billion study arm degree try.",
    },
    {
        id: "854c7362-804a-447e-ac93-c16a95b70e3c",
        created: new Date("2024-11-06T00:00:00Z"),
        status: "failed",
        name: "Robert Keith",
        description: "Help recognize owner add.",
    },
    {
        id: "28fc3ea0-3db0-4a95-a224-827a2dde42c1",
        created: new Date("2024-11-04T00:00:00Z"),
        status: "failed",
        name: "Sonia Rogers",
        description: "Provide cultural over group world.",
    },
    {
        id: "2c341542-7ef2-4b44-9620-695ac8584baf",
        created: new Date("2024-11-02T00:00:00Z"),
        status: "completed",
        name: "Michael Gray",
        description: "Stop explain history continue pull morning view account.",
    },
    {
        id: "2af5b1e3-a7d7-4f5c-9d45-c6f5448c0ec6",
        created: new Date("2024-11-18T00:00:00Z"),
        status: "in_progress",
        name: "William Miller",
        description: "Similar so cost discussion agent.",
        metadata: {
            job: {
                job_progress: 0.25,
                job_status: "in_progress",
            },
        },
    },
    {
        id: "f030eafd-e2b0-4958-99f4-ae0ae0779d03",
        created: new Date("2024-11-09T10:00:00Z"),
        status: "failed",
        name: "Paul Mitchell",
        description: "Big road factor style face wife prepare.",
    },
    {
        id: "f496dffa-e080-4f88-ad6d-2776e4d6bd4e",
        created: new Date("2024-11-19T00:00:00Z"),
        status: "started",
        name: "Jeffrey Terry",
        description: "Trouble appear face particular save right more customer.",
    },
    {
        id: "013bc4c4-7403-48ea-840b-232c9f34e878",
        created: new Date("2024-11-07T10:00:00Z"),
        status: "pending",
        name: "Mary Cook",
        description: "Detail toward PM money law.",
    },
    {
        id: "8a50c6fd-69a1-4d7a-817c-8540bac7133a",
        created: new Date("2024-11-02T10:00:00Z"),
        status: "failed",
        name: "Amy Bradford",
        description: "Threat within evidence four on American without.",
    },
    {
        id: "1769a527-d40b-4b03-bfda-bff53d6694ff",
        created: new Date("2024-11-06T00:00:00Z"),
        status: "in_progress",
        name: "Vincent Ramirez",
        description: "Here safe company whatever current.",
        metadata: {
            job: {
                job_progress: 0.3,
                job_status: "in_progress",
            },
        },
    },
    {
        id: "74a69903-d6a1-4907-9993-79a5c265dd3f",
        created: new Date("2024-11-09T00:00:00Z"),
        status: "completed",
        name: "Jonathan Taylor",
        description: "Animal price they practice act.",
    },
    {
        id: "c3288447-22af-4359-a9a9-784283df78d1",
        created: new Date("2024-11-10T00:00:00Z"),
        status: "failed",
        name: "Kristin Carney",
        description: "Hard impact sense agree foreign.",
        metadata: {
            job: {
                job_progress: 0.8,
                job_status: "failed",
            },
        },
    },
];

const config: ColumnConfig<Data> = TableDataUtility.createColumns([
    {
        id: "id",
        type: "TEXT",
    },
    {
        id: "created",
        type: "DATE",
    },
    {
        id: "status",
        type: "MULTI_SELECT",
        filterItems: statusArray.map((status) => ({
            label: status,
            value: status,
        })),
    },
    {
        id: "name",
        type: "TEXT",
    },
    {
        id: "description",
        type: "TEXT",
    },
]);

async function waitForClearedTags(screen: RenderResult) {
    await vi.waitUntil(
        () => screen.baseElement.querySelectorAll("nve-tag").length === 0
    );
}

async function waitForLoadingToFinish(screen: RenderResult) {
    globalThis.NVE_ELEMENTS.state.env = "production"; // disable dev time logs
    await vi.waitUntil(
        () => screen.baseElement.querySelector("nve-page-loader") != null
    );
    await vi.waitUntil(
        () => screen.baseElement.querySelector("nve-page-loader") === null
    );
}

const locators = {
    findTag(screen: RenderResult, tagId: string) {
        const tags = Array.from(screen.baseElement.querySelectorAll("nve-tag"));
        return tags.find((element) => element.innerHTML.startsWith(tagId));
    },
    findColumn(screen: RenderResult, headerText: string) {
        const elements = Array.from(
            screen.baseElement.querySelectorAll("nve-grid-column")
        );
        const element = elements.find((element) => {
            return (
                element.firstChild?.textContent?.trim().toLowerCase() ===
                headerText.toLowerCase()
            );
        });

        const [sortButton, filterButton, dropdown] = element?.children || [];

        return {
            element,
            sortButton: sortButton as Sortable,
            filterButton,
            dropdown,
        };
    },
    findRow(screen: RenderResult, rowId: string) {
        const element = screen.getByText(rowId).element();
        return element.parentNode!.parentNode!;
    },
    findCheckbox(screen: RenderResult, rowId: string) {
        const row =
            rowId === "all"
                ? this.findHeader(screen)
                : this.findRow(screen, rowId);
        return row.querySelector("input")!;
    },
    findHeader(screen: RenderResult) {
        return screen.baseElement.querySelector("nve-grid-header")!;
    },
    findLastUpdated(screen: RenderResult) {
        const labelEl = screen.getByText("Last Updated:").element();
        const lastUpdatedEl = labelEl.parentElement?.querySelector(
            '[nve-text="body sm bold"]'
        ) as Element;

        return lastUpdatedEl.textContent?.trim();
    },
    findRefreshButton(screen: RenderResult) {
        return screen.getByText("Refresh").element();
    },
    findPagination(screen: RenderResult) {
        const footer = screen.baseElement.querySelector("nve-grid-footer");
        const pagination = footer?.querySelector(
            "nve-pagination"
        ) as WithRenderRoot;
        const paginationItems = pagination.renderRoot.children[0].children;

        if (paginationItems.length === 3) {
            const [resultsDropdown, prevPage, nextPage] = paginationItems;

            return {
                firstPage: null,
                prevPage,
                resultsDropdown: resultsDropdown.children[0],
                totalResults: null,
                nextPage,
                lastPage: null,
            };
        }

        const [
            firstPage,
            prevPage,
            resultsDropdown,
            totalResults,
            nextPage,
            lastPage,
        ] = paginationItems;

        return {
            firstPage,
            prevPage,
            resultsDropdown: resultsDropdown.children[0],
            totalResults,
            nextPage,
            lastPage,
        };
    },
    findBulkSelectCheckboxes(screen: RenderResult) {
        const checkboxes = data.reduce(
            (acc, row) => {
                const checkbox = this.findCheckbox(screen, row.id);
                if (checkbox) {
                    acc[row.id] = checkbox;
                }
                return acc;
            },
            {} as { [key: string]: Element }
        );

        checkboxes["all"] = locators.findCheckbox(screen, "all");

        return checkboxes;
    },
    findSettingsBtn(screen: RenderResult) {
        const settingsBtn = screen.getByTestId("settings-btn").element();
        return settingsBtn;
    },
    findSettingsCheckboxGroup(screen: RenderResult) {
        const settingsCheckboxGroup = screen
            .getByTestId("settings-checkbox-group")
            .element();
        return settingsCheckboxGroup;
    },
    findRowActionMenuBtn(screen: RenderResult, rowId: string) {
        const row = this.findRow(screen, rowId);
        const actionMenu = row.querySelector("nve-icon-button")!;
        return actionMenu;
    },
    findRowActionMenu(screen: RenderResult, rowId: string) {
        const row = this.findRow(screen, rowId);
        const menu = row.querySelector("nve-menu")!;
        return menu;
    },
    findBulkSelectToolbar(screen: RenderResult) {
        return Array.from(
            screen.baseElement.querySelectorAll("nve-toolbar")
        ).find((toolbar) =>
            toolbar.textContent?.includes("selected")
        ) as HTMLElement;
    },
};

const expectations = {
    expectToMatchRows({
        screen,
        page,
        pageSize,
    }: {
        screen: RenderResult;
        page: number;
        pageSize: number;
    }) {
        const visibleRows = data
            .map(({ id }) => screen.getByText(id).query()?.textContent ?? "")
            .filter(Boolean);
        const rows = new Set(visibleRows);
        const start = page * pageSize - pageSize;
        const end = pageSize + start;
        const rowSlice = data.slice(start, end);
        const foundRows = rowSlice.every(({ id }) => rows.has(id));
        return foundRows && rows.size === rowSlice.length;
    },
    expectTotalResultsToEqual(screen: RenderResult, value: number) {
        const totalResults =
            locators
                .findPagination(screen)
                .totalResults?.textContent?.trim()
                .split(" ")[1] || "0";

        expect(parseInt(totalResults)).toEqual(value);
    },
    expectTagFilterToEqual(
        screen: RenderResult,
        filterId: string,
        filter: string | string[]
    ) {
        const tag = locators.findTag(screen, filterId)!;
        const tagFilter = tag.textContent?.trim().split(": ")[1] || "";

        if (typeof filter === "string") {
            expect(tagFilter).toEqual(filter);
        } else {
            const tagFilterArray = tagFilter.split("|").filter(Boolean);
            expect(tagFilterArray.sort()).toEqual(filter.sort());
        }
    },
    expectCheckboxChecked(screen: RenderResult, id: string) {
        const checkbox =
            id == "all"
                ? locators.findCheckbox(screen, "all")
                : locators.findCheckbox(screen, id);
        expect(checkbox.checked).toBeTruthy();
    },
    expectCheckboxUnchecked(screen: RenderResult, id: string) {
        const checkbox =
            id == "all"
                ? locators.findCheckbox(screen, "all")
                : locators.findCheckbox(screen, id);
        expect(checkbox.checked).toBeFalsy();
    },
    expectBulkActionToBeDisabled(screen: RenderResult) {
        const bulkToolbar = locators.findBulkSelectToolbar(screen);
        expect(bulkToolbar.style.visibility).toBe("hidden");
    },
    expectBulkActionToBeEnabled(screen: RenderResult) {
        const bulkToolbar = locators.findBulkSelectToolbar(screen);
        expect(bulkToolbar.style.visibility).toBe("visible");
    },
    expectColumnToBeFalsy(screen: RenderResult, headerText: string) {
        const column = locators.findColumn(screen, headerText);
        expect(column.element).toBeFalsy();
    },
    expectColumnToBeTruthy(screen: RenderResult, headerText: string) {
        const column = locators.findColumn(screen, headerText);
        expect(column.element).toBeTruthy();
    },
    async expectToEventuallyThrow(fn: () => Promise<void>) {
        let thrown: boolean | null = null;
        try {
            await fn();
            thrown = false;
        } catch {
            thrown = true;
        } finally {
            expect(thrown).toBeTruthy();
        }
    },
};

const actions = {
    async enterSearch(screen: RenderResult, text: string) {
        await screen.getByTestId("FilterBar").getByRole("textbox").fill(text);
        try {
            await vi.waitUntil(() => locators.findTag(screen, "search"));
        } catch {
            return;
        }
    },
    async cancelSearch(screen: RenderResult) {
        const element = screen.baseElement.querySelector(
            "nve-toolbar nve-icon-button[slot='suffix']"
        );

        if (!element) {
            throw new Error("Element not found, cancel button");
        }

        await userEvent.click(element);
        await waitForClearedTags(screen);
    },
    async applyDateFilter({
        screen,
        filterId,
        start = "",
        end = "",
    }: {
        screen: RenderResult;
        filterId: string;
        start?: string;
        end?: string;
    }) {
        const column = locators.findColumn(screen, filterId);

        await userEvent.click(column.filterButton);

        const startDate = screen.baseElement.querySelector(
            `input[name="${filterId}-start-date"]`
        )!;

        const endDate = screen.baseElement.querySelector(
            `input[name="${filterId}-end-date"]`
        )!;
        await userEvent.fill(startDate, start);
        await userEvent.fill(endDate, end);

        await this.reset(screen);
        try {
            await vi.waitUntil(() => locators.findTag(screen, filterId));
        } catch {
            return;
        }
    },
    async applyTextFilter({
        screen,
        filterId,
        value = "",
    }: {
        screen: RenderResult;
        filterId: string;
        value?: string;
    }) {
        const column = locators.findColumn(screen, filterId);

        await userEvent.click(column.filterButton);

        const input = screen.baseElement.querySelector(
            `input[name="${filterId}-text"]`
        )!;
        await userEvent.fill(input, value);

        await this.reset(screen);

        try {
            await vi.waitUntil(() => locators.findTag(screen, filterId));
        } catch {
            return;
        }
    },
    async applyMultiSelectFilter({
        screen,
        filterId,
        value = [],
    }: {
        screen: RenderResult;
        filterId: string;
        value?: string[];
    }) {
        const column = locators.findColumn(screen, filterId);
        await userEvent.click(column.filterButton);
        const select = column.dropdown.firstChild?.firstChild as Element;
        await userEvent.selectOptions(select, value);
        await this.reset(screen);
        try {
            await vi.waitUntil(() => locators.findTag(screen, filterId));
        } catch {
            return;
        }
    },
    async sortColumn(screen: RenderResult, columnId: string) {
        const { sortButton } = locators.findColumn(screen, columnId);
        const sortDirection = sortButton.sort;
        await userEvent.click(sortButton);
        await vi.waitUntil(() => sortButton.sort !== sortDirection);
    },
    async submitBulkAction(screen: RenderResult, action: string) {
        const bulkToolbar = locators.findBulkSelectToolbar(screen);

        // Click the "more-actions" button to open the dropdown
        const moreActionsButton = bulkToolbar.querySelector(
            "nve-icon-button[icon-name='more-actions']"
        )!;
        await userEvent.click(moreActionsButton);

        // Find and click the specific action in the dropdown menu
        const dropdownMenu = screen.baseElement.querySelector(
            "#toolbar-dropdown-menu nve-menu"
        )!;
        const menuItems = Array.from(dropdownMenu.children);
        const actionItem = menuItems.find((item) =>
            item.textContent
                ?.trim()
                .toLowerCase()
                .includes(action.toLowerCase())
        );

        if (!actionItem) {
            throw new Error(`Action "${action}" not found in bulk action menu`);
        }

        await userEvent.click(actionItem);
    },
    async changePageSize(screen: RenderResult, pageSize: string) {
        const gridRows = screen.baseElement.querySelector("nve-grid")?.children;
        const startingGridRowLength = gridRows?.length;

        const { resultsDropdown } = locators.findPagination(screen);
        await userEvent.selectOptions(resultsDropdown, pageSize);
        try {
            await vi.waitUntil(
                () => startingGridRowLength !== gridRows?.length
            );
        } catch {
            return;
        }
    },
    async nextPage(screen: RenderResult) {
        const { nextPage } = locators.findPagination(screen);
        await userEvent.click(nextPage);
    },
    async firstPage(screen: RenderResult) {
        const { firstPage } = locators.findPagination(screen);
        await userEvent.click(firstPage!);
    },
    async lastPage(screen: RenderResult) {
        const { lastPage } = locators.findPagination(screen);
        await userEvent.click(lastPage!);
    },
    async clickCheckbox(screen: RenderResult, id: string) {
        const checkbox = locators.findCheckbox(screen, id);
        await userEvent.click(checkbox);
    },
    async toggleColumns(screen: RenderResult, columnIds: string[]) {
        const settingsBtn = locators.findSettingsBtn(screen);
        await userEvent.click(settingsBtn);

        const settingsCheckboxGroup =
            locators.findSettingsCheckboxGroup(screen);

        for (const child of settingsCheckboxGroup.children) {
            if (
                columnIds.includes(
                    child.textContent?.trim().toLowerCase() ?? ""
                )
            ) {
                await userEvent.click(child);
            }
        }
        await this.reset(screen);
    },
    async triggerRowAction(
        screen: RenderResult,
        rowId: string,
        action: string
    ) {
        const rowActionMenuBtn = locators.findRowActionMenuBtn(screen, rowId);
        await userEvent.click(rowActionMenuBtn);
        const rowActionMenu = locators.findRowActionMenu(screen, rowId);

        for (const child of rowActionMenu.children) {
            if (child.textContent?.trim() === action) {
                await userEvent.click(child);
            }
        }

        await this.reset(screen);
    },
    async reset(screen: RenderResult) {
        await userEvent.keyboard("[Escape]");
        await userEvent.keyboard("[Escape]");
        await screen.getByText("Table Test", { exact: true }).tripleClick();
    },
    async renderTable(props: TableTestProps) {
        const screen = render(
            <Router>
                <TableTest {...props} />
            </Router>
        );
        await waitForLoadingToFinish(screen);
        return screen;
    },
    rerenderTable(screen: RenderResult, props: TableTestProps) {
        screen.rerender(
            <Router>
                <TableTest {...props} />
            </Router>
        );
    },
    async clickRefresh(screen: RenderResult) {
        await userEvent.click(locators.findRefreshButton(screen));
        await waitForLoadingToFinish(screen);
    },
};

async function fetchTableData() {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return [...data];
}

interface TableTestProps {
    config: ColumnConfig<Data>;
    bulkActionItems?: { label: string; value: string }[];
    rowActionItems?: { label: string; value: string; iconName: IconName }[];
    testOnSubmitBulkAction?: (action: string, rows: Data[]) => void;
    testOnSubmitRowAction?: (action: string, row: Data) => void;
}

const TableTest = (props: TableTestProps) => {
    const { lastUpdated, fetchData, data, loading } =
        useDataFetcher(fetchTableData);
    const defaultColumns = useMemo(
        () => props.config.map((column) => column.id),
        [props.config]
    );
    const tableSearchParams = useTableSearchParams({
        defaultColumns,
    });
    const rowData = useRowData({
        query: tableSearchParams.query,
        config: props.config,
        rows: data || [],
    });
    const bulkSelect = useBulkSelect(rowData.data.filteredRows);
    const selectedRows = useMemo(
        () =>
            rowData.data.filteredRows
                .filter((row) => bulkSelect.selectedRows.has(row.id))
                .map((row) => row.data) as Data[],
        [rowData.data.filteredRows, bulkSelect.selectedRows]
    );

    const testOnSubmitBulkAction = props.testOnSubmitBulkAction;
    const clearBulkSelect = bulkSelect.clear;
    const onSubmitBulkActionCallback = useCallback(
        (action: string) => {
            testOnSubmitBulkAction?.(action, selectedRows);
            clearBulkSelect();
        },
        [testOnSubmitBulkAction, selectedRows, clearBulkSelect]
    );

    const testOnSubmitRowAction = props.testOnSubmitRowAction;
    const onSubmitRowActionCallback = useCallback(
        (action: string, row: RowData) => {
            testOnSubmitRowAction?.(action, row.data as Data);
        },
        [testOnSubmitRowAction]
    );

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return (
        <DataTableContentLoader loading={loading}>
            <DataTablePageHeader
                title="Table Test"
                onClickRefresh={fetchData}
                lastUpdated={lastUpdated}
            />
            <DataTableFilterBar
                filters={tableSearchParams.query.filters}
                onSearch={tableSearchParams.setSearch}
                defaultValue={tableSearchParams.query.search}
                onFilter={tableSearchParams.setFilter}
                onClear={tableSearchParams.clear}
                label="search"
            />
            <DataTableToolbar
                config={props.config}
                columns={tableSearchParams.query.columns}
                onColumnChange={tableSearchParams.setColumn}
                bulkActionItems={props.bulkActionItems}
                selectedRows={bulkSelect.selectedRows}
                onSubmitBulkAction={onSubmitBulkActionCallback}
                onCloseBulkSelect={clearBulkSelect}
            />
            <DataTable
                allSelected={bulkSelect.allSelected}
                config={props.config}
                data={rowData.data}
                query={tableSearchParams.query}
                onPageChange={tableSearchParams.setPage}
                onStepChange={tableSearchParams.setStep}
                onFilterChange={tableSearchParams.setFilter}
                onSortChange={tableSearchParams.setSort}
                rowActionItems={props.rowActionItems}
                selectedRows={bulkSelect.selectedRows}
                onClickSelectAll={bulkSelect.toggleAll}
                onClickSelectRow={bulkSelect.toggleRow}
                onSubmitRowAction={onSubmitRowActionCallback}
            />
        </DataTableContentLoader>
    );
};

describe("table.tsx", () => {
    let screen: RenderResult;
    beforeEach(async () => {
        screen = await actions.renderTable({ config });
    });

    afterEach(async () => {
        await actions.reset(screen);
        await actions.cancelSearch(screen);
        cleanup();
    });

    describe("date filter", () => {
        it("should include all dates on or after 2024-11-03", async () => {
            const start = "2024-11-03";
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start,
            });
            expectations.expectTotalResultsToEqual(screen, 19);
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                `${start}=>`
            );
        });

        it("should include all dates on or before 2024-11-07", async () => {
            const end = "2024-11-07";

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                end,
            });
            expectations.expectTotalResultsToEqual(screen, 12);
            expectations.expectTagFilterToEqual(screen, "created", `=>${end}`);
        });

        it("should include all dates between 2024-11-03 and 2024-11-10 inclusively", async () => {
            const start = "2024-11-03";
            const end = "2024-11-10";
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start,
                end,
            });
            expectations.expectTotalResultsToEqual(screen, 15);
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                `${start}=>${end}`
            );
        });

        it("should include only dates exactly on 2024-11-03", async () => {
            const start = "2024-11-03";
            const end = "2024-11-03";

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start,
                end,
            });
            expectations.expectTotalResultsToEqual(screen, 3);
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                `${start}=>${end}`
            );
        });

        it("should return no results for a date range with no matches", async () => {
            const start = "2024-11-20";

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start,
            });
            expectations.expectTotalResultsToEqual(screen, 0);
            await expectations.expectTagFilterToEqual(
                screen,
                "created",
                `${start}=>`
            );
        });

        it("should handle empty filter string by including all rows", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "",
                end: "",
            });
            expectations.expectTotalResultsToEqual(screen, 22);
            expect(locators.findTag(screen, "created")).toBeFalsy();
        });

        it("should handle whitespace by including all rows", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "    ",
            });
            expectations.expectTotalResultsToEqual(screen, 22);
            expect(locators.findTag(screen, "created")).toBeFalsy();
        });
    });

    describe("text filter", () => {
        it('should include all rows containing substring "er"', async () => {
            const value = "er";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTagFilterToEqual(screen, "name", value);
            expectations.expectTotalResultsToEqual(screen, 8);
        });

        it('should include all rows containing "Er" due to case sensitivity', async () => {
            const value = "Er";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "name", value);
        });

        it('should return no results for substring "fox"', async () => {
            const value = "fox";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 0);
            expectations.expectTagFilterToEqual(screen, "name", value);
        });

        it('should include rows where "name" is exactly "Heather Brown"', async () => {
            const value = "Heather Brown";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "name", value);
        });

        it('should return no results for non-matching substring "XYZ"', async () => {
            const value = "XYZ";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 0);
            expectations.expectTagFilterToEqual(screen, "name", value);
        });

        it("should handle empty filter string by including all rows", async () => {
            const value = "";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 22);
            expect(locators.findTag(screen, "name")).toBeFalsy();
        });

        it("should handle whitespace by including all rows", async () => {
            const value = "   ";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 22);
            expect(locators.findTag(screen, "name")).toBeFalsy();
        });

        it('should include rows where "name" is exactly "Dr. Melissa Roberts DDS"', async () => {
            const value = "Dr. Melissa Roberts DDS";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "name", value);
        });

        it('should correctly match substrings with special characters (e.g., "Mrs.")', async () => {
            const value = "Mrs.";
            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "name", value);
        });
    });

    describe("multi-select filter", () => {
        it('should include all rows containing status "started"', async () => {
            const value = ["started"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 4);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing status "failed"', async () => {
            const value = ["failed"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 7);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing status "in_progress"', async () => {
            const value = ["in_progress"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 4);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing status "pending"', async () => {
            const value = ["pending"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 4);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing status "completed"', async () => {
            const value = ["completed"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 3);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing status "started" or "completed"', async () => {
            const value = ["started", "completed"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 7);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing status "failed" or "in_progress"', async () => {
            const value = ["failed", "in_progress"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 11);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });

        it('should include all rows containing multiple statuses "failed", "started", or "pending"', async () => {
            const value = ["failed", "started", "pending"];
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value,
            });
            expectations.expectTotalResultsToEqual(screen, 15);
            expectations.expectTagFilterToEqual(screen, "status", value);
        });
    });

    describe("search filter (case-sensitive)", () => {
        it('should include all rows containing substring "er" across columns', async () => {
            const value = "er";
            await actions.enterSearch(screen, value);
            expectations.expectTagFilterToEqual(screen, "search", value);
            expectations.expectTotalResultsToEqual(screen, 11);
        });

        it('should include all rows containing substring "fa" across columns', async () => {
            const value = "fa";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 11);
            expectations.expectTagFilterToEqual(screen, "search", value);
        });

        it('should include all rows containing substring "Melissa" in the name field', async () => {
            const value = "Melissa";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "search", value);
        });

        it('should include all rows containing substring "view" in the description field', async () => {
            const value = "view";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 2);
            expectations.expectTagFilterToEqual(screen, "search", value);
        });

        it('should include all rows containing substring "Anderson" in the name field', async () => {
            const value = "Anderson";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "search", value);
        });

        it('should return no rows for substring "nonexistent"', async () => {
            const value = "nonexistent";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 0);
            expectations.expectTagFilterToEqual(screen, "search", value);
        });

        it("should handle empty search filter by including all rows", async () => {
            const value = "";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 22);
            expect(locators.findTag(screen, "search")).toBeFalsy();
        });

        it('should include all rows containing substring "prepare" in the description field', async () => {
            const value = "prepare";
            await actions.enterSearch(screen, value);
            expectations.expectTotalResultsToEqual(screen, 1);
            expectations.expectTagFilterToEqual(screen, "search", value);
        });
    });

    describe("comprehensive filtering", () => {
        it("should include all rows created on or after 2024-11-03 and with status 'started'", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-03",
            });

            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["started"],
            });

            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-03=>"
            );
            expectations.expectTagFilterToEqual(screen, "status", ["started"]);
            expectations.expectTotalResultsToEqual(screen, 4);
        });

        it("should include all rows created on or before 2024-11-07 and containing 'er' in the name", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                end: "2024-11-07",
            });

            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value: "er",
            });

            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "=>2024-11-07"
            );
            expectations.expectTagFilterToEqual(screen, "name", "er");
            expectations.expectTotalResultsToEqual(screen, 4);
        });

        it("should include rows created between 2024-11-03 and 2024-11-10 and status 'failed' or 'in_progress'", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-03",
                end: "2024-11-10",
            });

            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["failed", "in_progress"],
            });

            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-03=>2024-11-10"
            );
            expectations.expectTagFilterToEqual(screen, "status", [
                "failed",
                "in_progress",
            ]);
            expectations.expectTotalResultsToEqual(screen, 8);
        });

        it("should include rows containing 'view' in the description and created strictly before 2024-11-07", async () => {
            await actions.enterSearch(screen, "view");
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                end: "2024-11-06",
            });

            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "=>2024-11-06"
            );
            expectations.expectTagFilterToEqual(screen, "search", "view");
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows with status 'pending' and name exactly 'Karen Patterson'", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["pending"],
            });

            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value: "Karen Patterson",
            });

            expectations.expectTagFilterToEqual(screen, "status", ["pending"]);
            expectations.expectTagFilterToEqual(
                screen,
                "name",
                "Karen Patterson"
            );
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows created on 2024-11-09 and containing substring 'prepare' in the description", async () => {
            await actions.enterSearch(screen, "prepare");
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-09",
                end: "2024-11-09",
            });

            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-09=>2024-11-09"
            );
            expectations.expectTagFilterToEqual(screen, "search", "prepare");
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows containing 'Melissa' in the name and with status 'started' or 'completed'", async () => {
            await actions.enterSearch(screen, "Melissa");
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["started", "completed"],
            });

            expectations.expectTagFilterToEqual(screen, "status", [
                "started",
                "completed",
            ]);
            expectations.expectTagFilterToEqual(screen, "search", "Melissa");
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows created on or after 2024-11-03, with status 'failed', and containing 'Anderson' in the name", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["failed"],
            });

            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value: "Anderson",
            });

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-03",
            });

            expectations.expectTagFilterToEqual(screen, "status", ["failed"]);
            expectations.expectTagFilterToEqual(screen, "name", "Anderson");
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-03=>"
            );
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows created strictly before 2024-11-07, with status 'in_progress', and containing 'Ramirez' in the name", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["in_progress"],
            });

            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value: "Ramirez",
            });

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                end: "2024-11-06",
            });

            expectations.expectTagFilterToEqual(screen, "status", [
                "in_progress",
            ]);
            expectations.expectTagFilterToEqual(screen, "name", "Ramirez");
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "=>2024-11-06"
            );
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows created between 2024-11-03 and 2024-11-10, with status 'pending', and containing 'cold' in the description", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["pending"],
            });

            await actions.enterSearch(screen, "cold");

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-03",
                end: "2024-11-10",
            });

            expectations.expectTagFilterToEqual(screen, "status", ["pending"]);
            expectations.expectTagFilterToEqual(screen, "search", "cold");
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-03=>2024-11-10"
            );
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows created strictly after 2024-11-04, with status 'started', and containing 'Fox' in the name", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["started"],
            });

            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value: "Fox",
            });

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-05",
            });

            expectations.expectTagFilterToEqual(screen, "status", ["started"]);
            expectations.expectTagFilterToEqual(screen, "name", "Fox");
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-05=>"
            );
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should include rows created before 2024-11-10, with status 'completed', and containing 'view' in the description", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["completed"],
            });

            await actions.enterSearch(screen, "view");

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                end: "2024-11-09",
            });

            expectations.expectTagFilterToEqual(screen, "status", [
                "completed",
            ]);
            expectations.expectTagFilterToEqual(screen, "search", "view");
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "=>2024-11-09"
            );
            expectations.expectTotalResultsToEqual(screen, 1);
        });

        it("should return no rows for a combination of mismatched filters", async () => {
            await actions.applyMultiSelectFilter({
                screen,
                filterId: "status",
                value: ["failed"],
            });

            await actions.applyTextFilter({
                screen,
                filterId: "name",
                value: "XYZ",
            });

            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-20",
            });

            expectations.expectTagFilterToEqual(screen, "status", ["failed"]);
            expectations.expectTagFilterToEqual(screen, "name", "XYZ");
            expectations.expectTagFilterToEqual(
                screen,
                "created",
                "2024-11-20=>"
            );
            expectations.expectTotalResultsToEqual(screen, 0);
        });
    });

    describe("pagination", () => {
        ["10", "20", "50"].forEach((pageSize) => {
            it(`should paginate page size ${pageSize}`, async () => {
                await actions.changePageSize(screen, pageSize);
                expectations.expectToMatchRows({
                    screen,
                    page: 1,
                    pageSize: parseInt(pageSize),
                });
            });
        });

        it("should page", async () => {
            await actions.changePageSize(screen, "10");
            for (let i = 1; i <= 3; i++) {
                expectations.expectToMatchRows({
                    screen,
                    page: i,
                    pageSize: 10,
                });
                await actions.nextPage(screen);
            }
        });

        it("should page to last page and first page", async () => {
            await actions.changePageSize(screen, "10");
            expectations.expectToMatchRows({
                screen,
                page: 1,
                pageSize: 10,
            });
            await actions.lastPage(screen);
            expectations.expectToMatchRows({
                screen,
                page: 3,
                pageSize: 10,
            });
            await actions.firstPage(screen);
            expectations.expectToMatchRows({
                screen,
                page: 1,
                pageSize: 10,
            });
        });
    });

    describe("sorting", () => {
        let pagination: Awaited<ReturnType<typeof locators.findPagination>>;
        let grid: Element;
        const generateSnapshot = () => {
            const columns: string[] = [];
            let sortColumnId = "";
            let sortDirection = "";
            const columnIds = Array.from(
                grid.querySelectorAll("nve-grid-column")
            ).map((column) => {
                return Array.from(column.childNodes)
                    .filter((n) => n.nodeType === Node.TEXT_NODE)
                    .map((n) => n.textContent?.trim() || "")
                    .join("");
            });

            grid.querySelectorAll("nve-grid-column").forEach((column) => {
                if (column.getAttribute("aria-sort")) {
                    const columnIndex =
                        parseInt(column.getAttribute("aria-colindex") || "") -
                        1;
                    sortColumnId = columnIds[columnIndex];
                    sortDirection = column.getAttribute("aria-sort") || "";
                }
            });

            grid.querySelectorAll("nve-grid-row").forEach((row) => {
                const cells = row.querySelectorAll("nve-grid-cell");
                cells.forEach((cell, i) => {
                    if (sortColumnId === columnIds[i]) {
                        columns.push(cell.textContent?.trim() || "");
                    }
                });
            });

            return JSON.stringify(
                {
                    sortDirection,
                    sortColumnId,
                    columns,
                },
                null,
                2
            );
        };

        beforeEach(async () => {
            pagination = locators.findPagination(screen);
            await userEvent.selectOptions(pagination.resultsDropdown, "50");
            await expectations.expectToMatchRows({
                screen,
                page: 1,
                pageSize: 50,
            });
            grid = document.querySelector("nve-grid")!;
        });
        config.forEach(({ id }) => {
            it(`should sort ${id} in ascending order`, async () => {
                await actions.sortColumn(screen, id);
                expect(generateSnapshot()).toMatchSnapshot();
            });
            it(`should sort ${id} in descending order`, async () => {
                await actions.sortColumn(screen, id);
                await actions.sortColumn(screen, id);
                expect(generateSnapshot()).toMatchSnapshot();
            });
        });
    });

    describe("refresh", () => {
        it("should update last updated after clicking refresh", async () => {
            const valueBefore = locators.findLastUpdated(screen);
            await new Promise((resolve) => setTimeout(resolve, 1000));
            await actions.clickRefresh(screen);
            const valueAfter = locators.findLastUpdated(screen);

            expect(valueBefore).toBeTruthy();
            expect(valueAfter).toBeTruthy();
            expect(valueAfter).not.toEqual(valueBefore);
        });
    });

    describe("bulk select", () => {
        const bulkActionItems = [
            { label: "Cancel", value: "cancel" },
            { label: "Archive", value: "archive" },
            { label: "Remove", value: "remove" },
        ];
        let onSubmitBulkAction: ReturnType<typeof vi.fn>;

        beforeEach(async () => {
            onSubmitBulkAction = vi.fn();

            actions.rerenderTable(screen, {
                config,
                bulkActionItems,
                testOnSubmitBulkAction: onSubmitBulkAction,
            });

            await actions.changePageSize(screen, "10");
        });

        it("should select and unselect an individual checkbox", async () => {
            const checkboxId = data[0].id;
            await actions.clickCheckbox(screen, checkboxId);
            expectations.expectCheckboxChecked(screen, checkboxId);
            await actions.clickCheckbox(screen, checkboxId);
            expectations.expectCheckboxUnchecked(screen, checkboxId);
        });

        it("should select and unselect all", async () => {
            await actions.clickCheckbox(screen, "all");
            const allCheckboxes = [
                "all",
                ...data.slice(0, 10).map(({ id }) => id),
            ];

            allCheckboxes.forEach((id) =>
                expectations.expectCheckboxChecked(screen, id)
            );
            await actions.clickCheckbox(screen, "all");
            allCheckboxes.forEach((id) =>
                expectations.expectCheckboxUnchecked(screen, id)
            );
        });

        it("should keep visible checkboxes selected with unchecked checkbox in check all state", async () => {
            await actions.clickCheckbox(screen, "all");
            const checkboxes = data.slice(0, 10).map(({ id }) => id);
            await actions.clickCheckbox(screen, checkboxes[0]);
            checkboxes
                .slice(1)
                .forEach((id) =>
                    expectations.expectCheckboxChecked(screen, id)
                );
            expectations.expectCheckboxUnchecked(screen, checkboxes[0]);
            expectations.expectCheckboxUnchecked(screen, "all");
        });

        it("should display inactive form when no checkboxes checked", () => {
            expectations.expectBulkActionToBeDisabled(screen);
        });

        it("should display active form with selected items", async () => {
            await actions.clickCheckbox(screen, data[0].id);
            expectations.expectBulkActionToBeEnabled(screen);
        });

        it("should reset form", async () => {
            await actions.clickCheckbox(screen, data[0].id);
            expectations.expectBulkActionToBeEnabled(screen);
            await actions.clickCheckbox(screen, data[0].id);
            expectations.expectBulkActionToBeDisabled(screen);
        });

        it("should submit bulk action from dropdown", async () => {
            await actions.clickCheckbox(screen, data[0].id);
            await actions.submitBulkAction(screen, "cancel");
            const [action, rows] = onSubmitBulkAction.mock.calls[0];
            expect(action).toEqual("cancel");
            const rowIds = rows.map((row: Data) => row.id);
            expect(rowIds).toEqual([data[0].id]);
        });

        it("should submit all items", async () => {
            await actions.clickCheckbox(screen, "all");
            await actions.submitBulkAction(screen, "cancel");
            const [action, rows] = onSubmitBulkAction.mock.calls[0];
            expect(action).toEqual("cancel");
            const rowIds = rows.map((row: Data) => row.id);
            expect(rowIds).toEqual(data.map(({ id }) => id));
        });

        it("should submit filtered rows when all is checked", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-01",
                end: "2024-11-09",
            });
            await actions.clickCheckbox(screen, "all");
            await actions.submitBulkAction(screen, "cancel");
            const [action, rows] = onSubmitBulkAction.mock.calls[0];
            const filteredIds = data
                .filter(
                    ({ created }) =>
                        new Date("2024-11-01T00:00:00Z") <= created &&
                        created <= new Date("2024-11-09T23:59:59Z")
                )
                .map(({ id }) => id);
            expect(action).toEqual("cancel");
            const rowIds = rows.map((row: Data) => row.id);
            expect(rowIds).toEqual(filteredIds);
        });

        it("should submit all other rows when a row is unchecked", async () => {
            await actions.applyDateFilter({
                screen,
                filterId: "created",
                start: "2024-11-01",
                end: "2024-11-09",
            });
            await actions.clickCheckbox(screen, "all");
            await actions.nextPage(screen);
            await actions.clickCheckbox(
                screen,
                "2c341542-7ef2-4b44-9620-695ac8584baf"
            );
            await actions.submitBulkAction(screen, "cancel");
            const [action, rows] = onSubmitBulkAction.mock.calls[0];
            const filteredIds = data
                .filter(
                    ({ created, id }) =>
                        new Date("2024-11-01T00:00:00Z") <= created &&
                        created <= new Date("2024-11-09T23:59:59Z") &&
                        id !== "2c341542-7ef2-4b44-9620-695ac8584baf"
                )
                .map(({ id }) => id);
            expect(action).toEqual("cancel");
            const rowIds = rows.map((row: Data) => row.id);
            expect(rowIds).toEqual(filteredIds);
        });
    });

    describe("settings", () => {
        it("should toggle columns", async () => {
            const columns = config.slice(1).map(({ id }) => id);

            await actions.toggleColumns(screen, columns);

            columns.forEach((column) =>
                expectations.expectColumnToBeFalsy(screen, column)
            );

            await actions.toggleColumns(screen, columns);

            columns.forEach((column) =>
                expectations.expectColumnToBeTruthy(screen, column)
            );
        });

        it("should not remove all columns", async () => {
            const columns = config.map(({ id }) => id);
            await actions.toggleColumns(screen, columns);
            columns
                .slice(0, -1)
                .forEach((c) => expectations.expectColumnToBeFalsy(screen, c));
            expectations.expectColumnToBeTruthy(screen, "description");
        });
    });

    describe("row actions", () => {
        let onSubmitRowAction: ReturnType<typeof vi.fn>;
        const rowId = data[0].id;
        beforeEach(() => {
            const rowActionItems: {
                label: string;
                value: string;
                iconName: IconName;
            }[] = [
                {
                    label: "Evict",
                    iconName: "stop-sign",
                    value: "evict",
                },
                {
                    label: "Remove",
                    iconName: "delete",
                    value: "remove",
                },
            ];

            onSubmitRowAction = vi.fn();

            actions.rerenderTable(screen, {
                config,
                rowActionItems,
                testOnSubmitRowAction: onSubmitRowAction,
            });
        });

        it("should trigger evict action", async () => {
            await actions.triggerRowAction(screen, rowId, "Evict");
            const [action, row] = onSubmitRowAction.mock.calls[0];
            expect(action).toEqual("evict");
            expect(row).toBeTruthy();
            expect(row).toEqual(data.find((r) => r === row));
        });

        it("should trigger remove action", async () => {
            await actions.triggerRowAction(screen, rowId, "Remove");
            const [action, row] = onSubmitRowAction.mock.calls[0];
            expect(action).toEqual("remove");
            expect(row).toBeTruthy();
            expect(row).toEqual(data.find((r) => r === row));
        });
    });

    describe("dynamic columns", () => {
        beforeEach(() => {
            actions.rerenderTable(screen, {
                config: [
                    ...config,
                    ...TableDataUtility.createColumns([
                        {
                            id: "metadata.job.job_status",
                            accessor: "metadata.job.job_status",
                            type: "TEXT",
                            headerText: "JOB STATUS",
                        },
                        {
                            id: "metadata.job.job_progress",
                            accessor: "metadata.job.job_progress",
                            type: "TEXT",
                            headerText: "JOB PROGRESS",
                        },
                    ]),
                ],
            });
        });
        it("should load dynamic field job status", () => {
            expectations.expectColumnToBeTruthy(screen, "JOB STATUS");
        });

        it("should load dynamic field job progress", () => {
            expectations.expectColumnToBeTruthy(screen, "JOB PROGRESS");
        });
    });
});
