// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { style } from "@vanilla-extract/css";
import { theme } from "~/styles/theme.gen.css";

export const appContainer = style({
    display: "grid",
    gridTemplateAreas: `
    "header header"
    "sidebar content"
  `,
    gridTemplateColumns: "auto 1fr", // Sidebar width and content fills remaining space
    gridTemplateRows: "auto 1fr", // Header auto height, content fills remaining height
    height: "100vh", // Full viewport height
    gap: theme.space.lg,
});

export const appHeader = style({
    gridArea: "header",
});

export const appSidebar = style({
    gridArea: "sidebar",
});

export const appContent = style({
    gridArea: "content",
});
