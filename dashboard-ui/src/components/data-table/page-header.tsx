// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";
import { PageHeader } from "../page-header";
import { MetadataItem } from "../metadata-item";

function RefreshButton({ onClick }: { onClick?: () => void }) {
    return (
        <nve-button interaction="emphasis" onClick={onClick}>
            <nve-icon size="sm" name="refresh"></nve-icon>
            Refresh
        </nve-button>
    );
}

interface DataTablePageHeaderProps {
    title: string;
    onClickRefresh: () => void;
    lastUpdated: string;
    renderMetadata?: () => JSX.Element | null;
}

function DataTablePageHeader({
    title,
    onClickRefresh,
    lastUpdated,
    renderMetadata,
}: DataTablePageHeaderProps) {
    return (
        <PageHeader
            title={title}
            actions={<RefreshButton onClick={onClickRefresh} />}
            metadata={
                <>
                    <MetadataItem label="Last Updated:" value={lastUpdated} />
                    {renderMetadata?.()}
                </>
            }
        />
    );
}

export { DataTablePageHeader };
