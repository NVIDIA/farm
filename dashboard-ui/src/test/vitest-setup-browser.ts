// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import "vitest-browser-react";
import "~/elements";
import "~/styles/reset.css";
import "~/styles/fouc.gen.css";

window.litIssuedWarnings ??= new Set<string>();
window.litIssuedWarnings.add(
    "Lit is in dev mode. Not recommended for production! See https://lit.dev/msg/dev-mode for more information."
);
