// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useRef } from "react";

export function Input({
    label = "",
    defaultValue = "",
    onChange,
    placeholder,
    name,
}: {
    label?: string;
    defaultValue?: string;
    onChange?: (value: string) => void;
    placeholder?: string;
    name?: string;
}) {
    const ref = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (ref.current) {
            ref.current.value = defaultValue;
        }
    }, [defaultValue]);

    return (
        <nve-input container="flat">
            {label && <label>{label}</label>}
            <input
                ref={ref}
                type="text"
                defaultValue={defaultValue}
                onChange={(e) => onChange?.(e.target.value)}
                onClick={(e) => {
                    e.preventDefault();
                    ref.current?.focus();
                }}
                placeholder={placeholder}
                name={name}
            />
        </nve-input>
    );
}
