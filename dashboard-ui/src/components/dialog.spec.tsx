// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { render, cleanup } from "vitest-browser-react";
import { userEvent } from "@vitest/browser/context";
import { Dialog } from "./dialog";

describe("dialog.tsx", () => {
    let onClose = vi.fn();
    let onSubmit = vi.fn();
    const DialogComponent = () => (
        <Dialog title="Test Dialog" onClose={onClose} onSubmit={onSubmit}>
            <div>Hello World Content</div>
        </Dialog>
    );

    beforeEach(() => {
        onClose = vi.fn();
        onSubmit = vi.fn();
    });

    afterEach(() => {
        cleanup();
    });

    it("should render dialog with title and content", () => {
        const screen = render(<DialogComponent />);

        // Check if title is rendered
        expect(screen.getByText("Test Dialog")).toBeDefined();

        // Check if content is rendered
        expect(screen.getByText("Hello World Content")).toBeDefined();

        // Check if buttons are present
        expect(screen.getByText("Cancel")).toBeDefined();
        expect(screen.getByText("Confirm")).toBeDefined();
    });

    it("should call onClose when Cancel button is clicked", async () => {
        const screen = render(<DialogComponent />);

        // Click the Cancel button
        const cancelButton = screen.getByText("Cancel");
        await userEvent.click(cancelButton.element());

        // Verify onClose was called
        expect(onClose).toHaveBeenCalledOnce();
    });

    it("should render with empty content", () => {
        const screen = render(<DialogComponent />);

        // Title should still be present
        expect(screen.getByText("Empty Dialog")).toBeDefined();

        // Buttons should still be present
        expect(screen.getByText("Cancel")).toBeDefined();
        expect(screen.getByText("Confirm")).toBeDefined();
    });

    it("should call onSubmit when Action button is clicked", async () => {
        const screen = render(<DialogComponent />);

        // Click the Action button
        const actionButton = screen.getByText("Confirm");
        await userEvent.click(actionButton.element());

        // Verify onSubmit was called
        expect(onSubmit).toHaveBeenCalledOnce();
    });
});
