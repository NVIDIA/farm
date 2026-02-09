// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// config.ts
// Single instance configuration object.

export interface AppConfig {
    host: string;
    taskPath: string;
    agentPath: string;
    logPath: string;
    jobsPath: string;
    basePath: string;
    dagPath: string;
    authClientId: string;
    authLoginUrl: string;
    userToken: string;
    isAuthEnabled: boolean;
}

// Default configuration. Used when serving the
// built project. Assumes paths are relative to
// the root.
const DeployedConfig: AppConfig = {
    host: "",
    taskPath: "tasks",
    agentPath: "agents",
    logPath: "logs",
    jobsPath: "jobs",
    basePath: "",
    dagPath: "dag",
    authClientId: "",
    authLoginUrl: "",
    userToken: "",
    isAuthEnabled: false,
} as const;

// Local development configuration. Used when
// running locally from a development server.
// const LocalConfig: AppConfig = {
//     ...DeployedConfig,
//     host: "http://localhost:8011/queue/management",
// } as const;

// Local development configuration. Used when
// running locally using k8s.
// const LocalK8sConfig: AppConfig = {
//     ...DeployedConfig,
//     host: "http://farm.127-0-0-1.nip.io:8080/queue/management",
// } as const;

// const LocalDevConfig: AppConfig = {
//     ...DeployedConfig,
//     host: "http://www.msw.com",
// } as const;

// const ProdAConfig: AppConfig = {
//     ...DeployedConfig,
//     host: "https://api.prod-a.us-west-1.nv-ov.farm",
// };

// const CreativeAConfig: AppConfig = {
//     ...LocalConfig,
//     host: "https://creative-a.us-west-1.nv-ov.farm/queue/management",
// };

// Scoped configuration instance.
let config = DeployedConfig;

const Config = {
    get<C extends AppConfig, T extends keyof C>(property: T): Readonly<C[T]> {
        if (property in config) {
            return (config as C)[property];
        }

        throw new Error(`No property ${property as string} in configuration`);
    },
    getConfig<C extends AppConfig>(): C {
        return config as C;
    },
    merge<C extends AppConfig>(data: Partial<C>): Readonly<C> {
        config = { ...config, ...data } as const;
        return config as C;
    },
} as const;

export { Config, DeployedConfig };
