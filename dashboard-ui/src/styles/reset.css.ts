// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { globalStyle } from "@vanilla-extract/css";

/* TODO - Figure out why on deployed site vanilla-extract version of this file the styles are missing */
globalStyle("h1, h2, h3, h4, h5", {
    margin: 0,
});

globalStyle("fieldset", {
    display: "contents",
});

globalStyle("a, a:visited, a:-webkit-any-link", {
    fontWeight: "var(--nve-ref-font-weight-semibold)",
    color: "var(--nve-sys-text-link-emphasis-color)",
    textDecoration: "none",
});

globalStyle("a:hover", {
    color: "var(--nve-sys-text-link-hover-color)",
});

globalStyle("nve-icon", {
    width: "1em",
    height: "1em",
});

globalStyle("nve-grid:has(nve-toolbar:not([hidden]))::part(_scrollbox)", {
    paddingBottom: "0px !important",
});

globalStyle("nve-page-loader::backdrop", {
    inset: "48px 0 0 250px !important",
    backgroundColor: "rgba(0, 0, 0, 0.1) !important",
});

globalStyle("nve-page-loader::part(progress-ring)", {
    margin: "48px 0 0 250px !important",
});
