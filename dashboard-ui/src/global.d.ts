// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// src/global.d.ts
import type { CustomElements } from "@nve/elements/custom-elements-jsx";

declare module "react/jsx-runtime" {
    namespace JSX {
        // eslint-disable-next-line @typescript-eslint/no-empty-object-type
        interface IntrinsicElements extends CustomElements {}
    }
}
