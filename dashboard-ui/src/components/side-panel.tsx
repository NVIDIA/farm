// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

interface SidePanelNavLinkProps {
    to: string;
    label: string;
    active: boolean;
    navigate: () => void;
}

function SidePanelNavLink(props: SidePanelNavLinkProps) {
    return (
        <nve-menu-item
            current={props.active ? "page" : undefined}
            onClick={() => props.navigate()}
        >
            {props.label}
        </nve-menu-item>
    );
}

interface SidePanelProps {
    navLinks: SidePanelNavLinkProps[];
}

export function SidePanel(props: SidePanelProps) {
    return (
        <nve-page-panel slot="left-aside" style={{ width: "250px" }}>
            <nve-page-panel-content>
                <nve-menu>
                    {props.navLinks.map((link) => (
                        <SidePanelNavLink key={link.label} {...link} />
                    ))}
                </nve-menu>
            </nve-page-panel-content>
        </nve-page-panel>
    );
}
