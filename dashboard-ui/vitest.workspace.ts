// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { defineWorkspace } from "vitest/config";

export default defineWorkspace([
    {
        extends: "vite.config.ts",
        test: {
            include: ["src/**/*.spec.ts"],
            name: "node",
            environment: "node",
        },
    },
    {
        extends: "vite.config.ts",
        test: {
            name: "browser",
            include: ["src/**/*.spec.tsx"],
            globalSetup: ["./src/test/vitest-global-setup-browser.ts"],
            setupFiles: ["./src/test/vitest-setup-browser.ts"],
            browser: {
                enabled: true,
                name: "chromium",
                provider: "playwright",
                headless: true,
                providerOptions: { playwright: { launch: { devtools: true } } },
                viewport: {
                    height: 834,
                    width: 1112,
                },
            },
            css: true,
        },
    },
]);
