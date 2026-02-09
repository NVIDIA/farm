// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useRef } from "react";

export function Checkbox({
    label = "",
    defaultChecked = false,
    onChange,
    disabled = false,
}: {
    label?: string;
    defaultChecked?: boolean;
    onChange?: (value: boolean) => void;
    disabled: boolean;
}) {
    const ref = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (ref.current) {
            ref.current.checked = defaultChecked;
        }
    }, [defaultChecked]);

    return (
        <nve-checkbox>
            {label && <label>{label}</label>}
            <input
                ref={ref}
                type="checkbox"
                defaultChecked={defaultChecked}
                disabled={disabled}
                onChange={(e) => onChange?.(e.target.checked)}
            />
        </nve-checkbox>
    );
}
