// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReactNode } from "react";
import { AppHeader } from "./app-header";
import { SidePanel } from "./side-panel";
import { useLocation, useNavigate } from "react-router";
import { TaskUtility } from "~/utilities/task-utility";

const sidePanelNavLinks = [
    {
        to: TaskUtility.defaultTaskTableRoute,
        path: "/tasks",
        label: "Tasks",
    },
    {
        to: "/jobs",
        path: "/jobs",
        label: "Definitions",
    },
    {
        to: "/taskflows",
        path: "/taskflows",
        label: "Taskflows",
    },
    {
        to: "/agents",
        path: "/agents",
        label: "Agents",
    },
] as const;

export function AppLayout({ children }: { children: ReactNode }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <nve-page>
            <AppHeader />
            <SidePanel
                navLinks={sidePanelNavLinks.map((link) => ({
                    ...link,
                    active: location.pathname === link.path,
                    navigate: () => navigate(link.to),
                }))}
            />
            {children}
        </nve-page>
    );
}
