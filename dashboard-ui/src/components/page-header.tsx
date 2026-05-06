// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Using native custom elements
import type { IconName } from "@nvidia-elements/core/icon";

export interface PageHeaderAction {
    label: string;
    primary?: boolean;
    icon?: IconName;
    onAction: () => void;
}

function PageHeader({
    title,
    leading,
    tabs,
    metadata,
    actions,
}: {
    title: string;
    leading?: React.ReactNode;
    tabs?: {
        items: { label: string; value: string }[];
        selected: string;
        onClick: (value: string) => void;
    };
    metadata?: React.ReactNode;
    actions?: React.ReactNode;
}) {
    return (
        <nve-page-panel slot="subheader">
            <nve-page-panel-content>
                <div nve-layout="column gap:md align:stretch">
                    <div nve-layout="row align:space-between align:vertical-center">
                        <section nve-layout="row gap:sm align:vertical-center">
                            {leading}
                            <h1 nve-text="heading lg semibold">{title}</h1>
                        </section>

                        {actions && (
                            <section nve-layout="row gap:sm align:vertical-center">
                                {actions}
                            </section>
                        )}
                    </div>

                    {metadata && (
                        <section nve-layout="row gap:xl align:vertical-start">
                            {metadata}
                        </section>
                    )}

                    {tabs && (
                        <nve-tabs>
                            {tabs.items.map(({ label, value }) => (
                                <nve-tabs-item
                                    key={value}
                                    selected={tabs.selected === value}
                                    onClick={() => tabs.onClick(value)}
                                >
                                    {label}
                                </nve-tabs-item>
                            ))}
                        </nve-tabs>
                    )}
                </div>
            </nve-page-panel-content>
        </nve-page-panel>
    );
}

export { PageHeader };
