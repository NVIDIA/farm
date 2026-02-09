// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { render, cleanup } from "vitest-browser-react";
import { userEvent } from "@vitest/browser/context";
import BulkSelectToolbar from "./bulk-select-toolbar";

describe("toolbar.tsx", () => {
    const mockActions = [
        {
            label: "Delete",
            iconName: "delete" as const,
            value: "delete",
        },
        {
            label: "Archive",
            iconName: "archive" as const,
            value: "archive",
        },
    ];

    let onClose = vi.fn();
    let onClickAction = vi.fn();
    const toolbarComponent = () => (
        <BulkSelectToolbar
            selectedCount={1}
            actions={mockActions}
            visible={true}
            onClickAction={onClickAction}
            onClose={onClose}
        />
    );

    beforeEach(() => {
        onClose = vi.fn();
        onClickAction = vi.fn();
    });

    afterEach(() => {
        cleanup();
    });

    it("should render toolbar with selected count", () => {
        const screen = render(
            <BulkSelectToolbar
                selectedCount={5}
                actions={mockActions}
                visible={true}
            />
        );

        // Check if selected count is rendered
        expect(screen.getByText("5 selected")).toBeDefined();
    });

    it("should render toolbar with zero selected items", () => {
        const screen = render(toolbarComponent());

        // Check if selected count is rendered
        expect(screen.getByText("0 selected")).toBeDefined();
    });

    it("should render with close button when onClose is provided", () => {
        const screen = render(
            <BulkSelectToolbar
                selectedCount={3}
                actions={mockActions}
                visible={true}
                onClose={onClose}
            />
        );

        // Check if close button is present (by icon-name attribute)
        const closeButton = screen.container.querySelector(
            '[icon-name="cancel"]'
        );
        expect(closeButton).toBeDefined();
    });

    it("should not render close button when onClose is not provided", () => {
        const screen = render(
            <BulkSelectToolbar
                selectedCount={3}
                actions={mockActions}
                visible={true}
            />
        );

        // Check if close button is not present
        const closeButton = screen.container.querySelector(
            '[icon-name="cancel"]'
        );
        expect(closeButton).toBeNull();
    });

    it("should call onClose when close button is clicked", async () => {
        const screen = render(toolbarComponent());

        // Find and click the close button
        const closeButton = screen.container.querySelector(
            '[icon-name="cancel"]'
        );
        expect(closeButton).toBeDefined();

        await userEvent.click(closeButton as Element);

        // Verify onClose was called
        expect(onClose).toHaveBeenCalledOnce();
    });

    it("should be hidden when visible is false", () => {
        const screen = render(
            <BulkSelectToolbar
                selectedCount={2}
                actions={mockActions}
                visible={false}
            />
        );

        // Check that the toolbar has visibility: hidden style
        const toolbar = screen.container.querySelector("nve-toolbar");
        expect(toolbar).toBeDefined();
        expect(toolbar?.getAttribute("style")).toContain("visibility: hidden");
    });

    it("should render actions in dropdown menu", () => {
        const screen = render(toolbarComponent());

        // Check if more actions button is present
        const moreActionsButton = screen.container.querySelector(
            '[icon-name="more-actions"]'
        );
        expect(moreActionsButton).toBeDefined();

        // Check if dropdown menu exists
        const dropdown = screen.container.querySelector(
            "#toolbar-dropdown-menu"
        );
        expect(dropdown).toBeDefined();

        // Check if action items are rendered in the menu
        expect(screen.getByText("Delete")).toBeDefined();
        expect(screen.getByText("Archive")).toBeDefined();
    });

    it("should display the dropdown menu when more actions button is clicked", async () => {
        const screen = render(toolbarComponent());

        // Check if more actions button is present
        const moreActionsButton = screen.container.querySelector(
            '[icon-name="more-actions"]'
        );
        expect(moreActionsButton).toBeDefined();

        // Click the more actions button
        await userEvent.click(moreActionsButton as Element);

        // Check if dropdown menu exists
        const dropdown = screen.container.querySelector(
            "#toolbar-dropdown-menu"
        );
        expect(dropdown).toBeDefined();

        // Check if action items are rendered in the menu
        expect(screen.getByText("Delete")).toBeDefined();
        expect(screen.getByText("Archive")).toBeDefined();

        const dropdownItems =
            screen.container.querySelectorAll("nve-menu-item");
        expect(dropdownItems).toHaveLength(mockActions.length);

        // Check if action items are rendered in the menu
        expect(dropdownItems[0].textContent).toContain("Delete");
        expect(dropdownItems[1].textContent).toContain("Archive");
    });
});
