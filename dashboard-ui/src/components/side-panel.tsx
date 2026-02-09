// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { sidePanelMenuStyles } from "./side-panel.css";

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
        <nve-panel behavior-expand expanded style={{ height: "100%" }}>
            <nve-panel-header>
                <div slot="title">Dashboards</div>
            </nve-panel-header>
            <nve-panel-content>
                <nve-menu className={sidePanelMenuStyles}>
                    {props.navLinks.map((link) => (
                        <SidePanelNavLink key={link.label} {...link} />
                    ))}
                </nve-menu>
            </nve-panel-content>
        </nve-panel>
    );
}
