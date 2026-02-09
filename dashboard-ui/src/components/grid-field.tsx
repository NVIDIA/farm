// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

interface FieldProperties {
    name: string;
    children: React.ReactNode;
}

function GridField(props: FieldProperties): JSX.Element {
    const { name, children } = props;
    return (
        <div nve-layout="grid span:12">
            <div nve-layout="span:2">
                <label nve-text="label">{name}</label>
            </div>
            <div
                nve-layout="span:8"
                nve-text="body"
                style={{ overflowWrap: "break-word" }}
            >
                {children}
            </div>
        </div>
    );
}

export { GridField };
