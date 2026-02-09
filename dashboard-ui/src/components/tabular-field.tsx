// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";
import { GridField } from "./grid-field";

// Helper function for determining how to render the value ofa  key/value object.
function getValue(value: unknown): JSX.Element {
    const parsed =
        typeof value !== "string" ? JSON.stringify(value, null, "\t") : value;
    return (
        <div
            style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
            title={parsed}
        >
            {parsed}
        </div>
    );
}

interface FieldProperties {
    name: string;
    value?: {
        [key: string]: unknown;
    };
}

function TabularField(props: FieldProperties): JSX.Element {
    const { name, value } = props;

    if (!value || Object.keys(value).length === 0) {
        return <GridField name={name}>N/A</GridField>;
    }

    const tabularized = Object.keys(value).map((key) => ({
        key,
        value: value[key],
    }));

    return (
        <div nve-layout="grid">
            <div nve-layout="span:2">
                <h2 style={{ margin: 0 }}>{name}</h2>
            </div>
            <div nve-layout="span:8">
                <nve-grid>
                    <nve-grid-header>
                        <nve-grid-column>KEY</nve-grid-column>
                        <nve-grid-column>VALUE</nve-grid-column>
                    </nve-grid-header>
                    {tabularized.map(({ key, value }, i) => (
                        <nve-grid-row key={i}>
                            <nve-grid-cell>{key}</nve-grid-cell>
                            <nve-grid-cell>{getValue(value)}</nve-grid-cell>
                        </nve-grid-row>
                    ))}
                </nve-grid>
            </div>
        </div>
    );
}

export { TabularField };
