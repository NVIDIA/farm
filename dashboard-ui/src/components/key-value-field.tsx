// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import { Link } from "react-router";

// Local
import { GridField } from "~/components/grid-field";

interface FieldProperties {
    name: string;
    value: string | number | boolean | undefined;
    link?: string;
}

function KeyValueField(props: FieldProperties): JSX.Element {
    const { name, value, link } = props;
    return (
        <GridField name={name}>
            {link ? <Link to={link ? link : ""}>{value}</Link> : value}
        </GridField>
    );
}

export { KeyValueField };
