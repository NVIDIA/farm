// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

interface FieldProperties {
    name: string;
    children: React.ReactNode;
}

function InputField(props: FieldProperties): JSX.Element {
    const { name, children } = props;
    return (
        <div nve-layout="grid span:12">
            <div nve-layout="span:12 pad-y:sm">
                <label nve-text="label">{name}</label>
            </div>
            <div nve-layout="span:5" nve-text="body">
                {children}
            </div>
        </div>
    );
}

export { InputField };
