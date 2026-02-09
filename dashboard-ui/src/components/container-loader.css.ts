// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { style } from "@vanilla-extract/css";
import { theme } from "~/styles/theme.gen.css";

export const ContainerLoaderModal = style({
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 99,
    "::after": {
        content: "",
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: theme.layer.containerBackground,
        opacity: theme.opacity.opacity300,
        zIndex: 98,
    },
});
