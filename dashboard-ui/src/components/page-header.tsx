// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Using native custom elements
import type { IconName } from "@nve/elements";

export interface PageHeaderAction {
    label: string;
    primary?: boolean;
    icon?: IconName;
    onAction: () => void;
}

function PageHeader({
    title,
    tabs,
    metadata,
    actions,
}: {
    title: string;
    tabs?: {
        items: { label: string; value: string }[];
        selected: string;
        onClick: (value: string) => void;
    };
    metadata?: React.ReactNode;
    actions?: React.ReactNode;
}) {
    return (
        <nve-card container="full" style={{ width: "100%", flexShrink: 0 }}>
            <nve-card-content>
                <div nve-layout="column gap:md align:stretch">
                    <div nve-layout="row align:space-between align:vertical-center">
                        <section nve-layout="row gap:sm align:vertical-center">
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
            </nve-card-content>
        </nve-card>
    );
}

export { PageHeader };
