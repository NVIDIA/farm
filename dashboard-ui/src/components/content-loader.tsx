// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PropsWithChildren } from "react";

type ContentLoaderProps = PropsWithChildren<{
    loading: boolean;
    stretch?: boolean;
}>;

function ContentLoader({ loading, children }: ContentLoaderProps) {
    return (
        <>
            {loading && <nve-page-loader></nve-page-loader>}
            {children}
        </>
    );
}

export { ContentLoader };
