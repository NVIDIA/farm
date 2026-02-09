// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PropsWithChildren } from "react";
import { ContainerLoader } from "./container-loader";
import {
    ContentLoaderStyles,
    ContentLoaderStretch,
} from "./content-loader.css";

type ContentLoaderProps = PropsWithChildren<{
    loading: boolean;
    stretch?: boolean;
}>;

function ContentLoader({
    loading,
    children,
    stretch = false,
    ...props
}: ContentLoaderProps) {
    const className = stretch
        ? `${ContentLoaderStyles} ${ContentLoaderStretch}`
        : ContentLoaderStyles;
    return (
        <div className={className} {...props}>
            <ContainerLoader loading={loading} />
            {children}
        </div>
    );
}

export { ContentLoader };
