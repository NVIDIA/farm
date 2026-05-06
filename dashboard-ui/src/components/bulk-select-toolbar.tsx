// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { IconName } from "@nvidia-elements/core/icon";
import { useMemo } from "react";

interface Action {
    label: string;
    value: string;
    iconName?: IconName;
}

function BulkSelectToolbar({
    selectedCount,
    actions,
    visible = true,
    onClose,
    onClickAction,
}: {
    selectedCount: number;
    actions: Action[];
    visible?: boolean;
    onClose?: () => void;
    onClickAction?: (action: string) => void;
}) {
    const status = useMemo(
        () => (selectedCount ? "accent" : undefined),
        [selectedCount]
    );

    return (
        <nve-toolbar
            status={status}
            style={{ visibility: visible ? "visible" : "hidden" }}
        >
            {onClose && (
                <nve-icon-button
                    icon-name="cancel"
                    slot="prefix"
                    onClick={onClose}
                ></nve-icon-button>
            )}
            <p nve-text="body">{selectedCount} selected</p>
            <nve-icon-button
                popovertarget="toolbar-dropdown-menu"
                container="flat"
                icon-name="more-actions"
                slot="suffix"
            ></nve-icon-button>
            <nve-dropdown id="toolbar-dropdown-menu">
                <nve-menu>
                    {actions.map((action) => (
                        <nve-menu-item
                            key={action.label}
                            onClick={() => onClickAction?.(action.value)}
                        >
                            {action.iconName && (
                                <nve-icon name={action.iconName} />
                            )}{" "}
                            {action.label}
                        </nve-menu-item>
                    ))}
                </nve-menu>
            </nve-dropdown>
        </nve-toolbar>
    );
}

export default BulkSelectToolbar;
