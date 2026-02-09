// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { vanillaExtractPlugin } from "@vanilla-extract/vite-plugin";
import tsconfigPaths from "vite-tsconfig-paths";

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), tsconfigPaths(), vanillaExtractPlugin()],
    server: {
        proxy: {
            "/api": {
                target: "http://localhost:8222/queue/management",
                changeOrigin: true,
                rewrite: (path) => path.split("/api")[1],
            },
        },
    },
    base: "./",
    test: {
        passWithNoTests: true,
        globals: true,
        coverage: {
            all: true,
            reporter: ["text", "html", "cobertura", "json"],
            reportsDirectory: "ci-reports/vitest/coverage/",
            include: ["app"],
        },
        reporters: ["junit", "verbose", "html"],
        outputFile: {
            junit: "ci-reports/vitest/junit.xml",
            html: "ci-reports/vitest/html/index.html",
        },
    },
});
