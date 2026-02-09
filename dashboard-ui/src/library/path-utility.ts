// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { AppConfig } from "./config";
import { Config } from "./config";

type ServiceConfigParts = Pick<
    AppConfig,
    "agentPath" | "logPath" | "taskPath" | "jobsPath" | "dagPath"
>;
type PathType = keyof ServiceConfigParts;

const PathUtility = {
    get(type: PathType, ...subpaths: string[]): string[] {
        const root = Config.get("host")
            ? Config.get("host")
            : Config.get("basePath");
        return [root, Config.get(type), ...subpaths];
    },
} as const;

export { PathUtility };
