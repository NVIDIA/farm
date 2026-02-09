// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ColumnConfig } from "~/utilities/table-data-utility";
import { Checkbox } from "~/components/checkbox";

export default function Settings<T>({
    columns,
    selectedColumns,
    onColumnChange,
}: {
    columns: ColumnConfig<T>;
    selectedColumns: Set<string>;
    onColumnChange: (id: string, checked: boolean) => void;
}) {
    return (
        <>
            <nve-icon-button
                popovertarget="column-settings-dropdown"
                container="flat"
                icon-name="gear"
                data-testid="settings-btn"
            />
            <nve-dropdown
                id="column-settings-dropdown"
                position="left"
                alignment="start"
            >
                <h2 nve-text="heading sm">Columns</h2>
                <nve-checkbox-group data-testid="settings-checkbox-group">
                    {columns.map(({ id, headerText }) => {
                        return (
                            <Checkbox
                                key={id}
                                label={headerText}
                                disabled={
                                    !!(
                                        selectedColumns.size === 1 &&
                                        selectedColumns.has(id)
                                    )
                                }
                                defaultChecked={selectedColumns.has(id)}
                                onChange={(checked) =>
                                    onColumnChange(id, checked)
                                }
                            />
                        );
                    })}
                </nve-checkbox-group>
            </nve-dropdown>
        </>
    );
}
