// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useRef } from "react";

export function MultiSelect({
    items,
    defaultValue,
    label = null,
    onChange,
}: {
    items: { label: string; value: string }[];
    defaultValue?: string[];
    label?: string | null;
    onChange?: (selectedOptions: string[]) => void;
}) {
    const ref = useRef<HTMLSelectElement>(null);

    useEffect(() => {
        if (ref.current && defaultValue) {
            for (const option of ref.current.options) {
                option.selected = defaultValue.includes(option.value);
            }
        }
    }, [defaultValue]);

    return (
        <nve-select>
            {label && <label>{label}</label>}
            <select
                ref={ref}
                multiple
                defaultValue={defaultValue}
                onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions).map(
                        (n) => n.value
                    );
                    onChange?.(selected);
                }}
            >
                {items.map(({ label, value }) => (
                    <option key={value} value={value}>
                        {label}
                    </option>
                ))}
            </select>
        </nve-select>
    );
}
