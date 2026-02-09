// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import React, { useEffect, useMemo } from "react";
import { useRef, useState } from "react";

// Nvidia
import { InputField } from "./input-field";

interface FieldProperties {
    name: string;
    defaultValue: unknown;
    onEdit?: (field: string, value: string, isValid: boolean) => void;
}

function JsonInput(props: FieldProperties): JSX.Element {
    const { name, defaultValue, onEdit } = props;
    const finalDefaultValue =
        typeof defaultValue !== "string"
            ? JSON.stringify(defaultValue, null, 4)
            : defaultValue;
    const [isValid, setIsValid] = useState<boolean | null>(null);

    const rows = useMemo(() => {
        const numRows = finalDefaultValue.split("\n").length;
        return numRows < 25 ? 25 : numRows;
    }, [finalDefaultValue]);
    const ref = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (ref.current) {
            ref.current.value = finalDefaultValue;
        }
    }, [finalDefaultValue]);

    function onKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
        if (event.key === "Tab") {
            // Do not tab scroll through this field, as it may be an attempt to
            // tab in a field.
            event.preventDefault();
        }
    }

    return (
        <InputField name={name}>
            <div nve-layout="column gap:xs">
                <nve-textarea>
                    <textarea
                        ref={ref}
                        rows={rows}
                        onChange={(e) => {
                            const value = e.target.value;
                            let valid = true;
                            try {
                                JSON.parse(value);
                            } catch {
                                valid = false;
                            }

                            onEdit?.(name, value, valid);
                            setIsValid(valid);
                        }}
                        onKeyDown={onKeyDown}
                        defaultValue={finalDefaultValue}
                        placeholder={name}
                    />
                </nve-textarea>
                {isValid !== null && (
                    <nve-alert
                        status={!isValid ? "danger" : "success"}
                    >{`JSON ${!isValid ? "invalid" : "valid"}`}</nve-alert>
                )}
            </div>
        </InputField>
    );
}

export { JsonInput };
