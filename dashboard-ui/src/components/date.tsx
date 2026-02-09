// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useRef } from "react";

export function Date({
    label = "",
    defaultValue = "",
    onChange,
    min,
    max,
    name,
}: {
    label?: string;
    defaultValue?: string;
    onChange?: (value: string) => void;
    min?: string | number;
    max?: string | number;
    name?: string;
}) {
    const ref = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (ref.current) {
            ref.current.value = defaultValue;
        }
    }, [defaultValue]);

    return (
        <nve-date>
            {label && (
                <nve-button container="flat" readonly>
                    {label}
                </nve-button>
            )}
            <input
                ref={ref}
                type="date"
                defaultValue={defaultValue}
                onChange={(e) => onChange?.(e.target.value)}
                min={min}
                max={max}
                name={name}
            />
        </nve-date>
    );
}
