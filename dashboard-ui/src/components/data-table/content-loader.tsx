// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ContentLoader } from "~/components/content-loader";

interface DataTableContentLoaderProps {
    loading?: boolean;
    stretch?: boolean;
    children: React.ReactNode;
}

function DataTableContentLoader({
    loading = false,
    children,
    stretch = false,
}: DataTableContentLoaderProps) {
    return (
        <ContentLoader loading={loading} stretch={stretch}>
            {children}
        </ContentLoader>
    );
}

export { DataTableContentLoader };
