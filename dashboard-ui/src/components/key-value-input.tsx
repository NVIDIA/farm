// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import React from "react";
import { InputField } from "./input-field";

// Nvidia
interface FieldProperties {
    name: string;
    value: string | number | undefined;
    isMultiLine?: boolean;
    isNumeric?: boolean;
    isDecimal?: boolean;
    onEdit?: (field: string, value: string | number) => void;
}

type ChangeEvent = React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>;

function ComponentShell({
    isMultiLine,
    children,
}: {
    isMultiLine: boolean;
    children: JSX.Element;
}) {
    if (isMultiLine) {
        return <nve-textarea>{children}</nve-textarea>;
    }
    return <nve-input>{children}</nve-input>;
}

function KeyValueInput(props: FieldProperties): JSX.Element {
    const { name, value, isMultiLine, isNumeric, isDecimal, onEdit } = props;
    const finalValue =
        typeof value !== "string" ? JSON.stringify(value) : value;

    function onChange(event: ChangeEvent) {
        const value = event.target.value;
        const finalValue = isNumeric || isDecimal ? parseFloat(value) : value;

        // Notify parent of edit.
        if (onEdit) {
            onEdit(name, finalValue);
        }
    }

    let type = "text";

    if (isNumeric) {
        type = "numeric";
    } else if (isDecimal) {
        type = "decimal";
    }

    return (
        <InputField name={name}>
            <ComponentShell isMultiLine={isMultiLine ?? false}>
                {isMultiLine ? (
                    <textarea
                        value={finalValue}
                        placeholder={name}
                        onChange={onChange}
                    />
                ) : (
                    <input
                        type={type}
                        value={finalValue}
                        placeholder={name}
                        onChange={onChange}
                    />
                )}
            </ComponentShell>
        </InputField>
    );
}

export { KeyValueInput };
