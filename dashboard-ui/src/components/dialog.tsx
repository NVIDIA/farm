// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReactNode } from "react";

export function Dialog({
    children,
    title,
    onClose,
    onSubmit,
    submitLabel = "Confirm",
    modal = true,
}: {
    children: ReactNode;
    title: string;
    onClose: () => void;
    onSubmit: () => void | Promise<void>;
    submitLabel?: string;
    modal?: boolean;
}) {
    return (
        <nve-dialog modal={modal}>
            <nve-dialog-header>
                <h3 nve-text="heading-3 capitalize">{title}</h3>
            </nve-dialog-header>
            {children}
            <nve-dialog-footer>
                <nve-button onClick={onClose}>Cancel</nve-button>
                <nve-button onClick={onSubmit} interaction="emphasis">
                    {submitLabel}
                </nve-button>
            </nve-dialog-footer>
        </nve-dialog>
    );
}
