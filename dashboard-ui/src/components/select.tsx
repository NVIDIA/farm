// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { SelectHTMLAttributes, useEffect, useRef } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
    label: string;
    items: { label: string; value: string }[];
    defaultValue?: string;
    layout?:
        | "vertical"
        | "vertical-inline"
        | "horizontal"
        | "horizontal-inline";
    placeholder?: string;
}

export function Select(props: SelectProps) {
    const ref = useRef<HTMLSelectElement>(null);

    useEffect(() => {
        if (ref.current && typeof props.defaultValue === "string") {
            ref.current.value = props.defaultValue;
        }
    }, [props.defaultValue]);

    return (
        <nve-select layout={props.layout}>
            <label htmlFor={props.name}>{props.label}</label>
            <select ref={ref} {...props}>
                {props.placeholder && (
                    <option disabled hidden value="">
                        {props.placeholder}
                    </option>
                )}
                {props.items.map(({ label, value }) => (
                    <option key={value} value={value}>
                        {label}
                    </option>
                ))}
            </select>
        </nve-select>
    );
}
