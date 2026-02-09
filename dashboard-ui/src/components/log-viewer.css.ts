// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { style } from "@vanilla-extract/css";
import { theme } from "~/styles/theme.gen.css";

export const LogViewerWindowStyles = style({
    fontFamily: theme.fontFamily.robotoMono,
    fontSize: theme.fontSize.fontSize200,
    overflow: "scroll",
});
