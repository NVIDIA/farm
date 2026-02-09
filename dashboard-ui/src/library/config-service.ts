// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// config-service.ts
// Single instance async data access object responsible for
// loading configuration from the serving OV extension.

// Local dependencies
import { UrlUtility } from "../utilities/url-utility";
import { Http } from "./http";

interface ConfigResponse {
    auth_client_id?: string;
    auth_login_url?: string;
    auth_enabled?: boolean;
}

const ConfigService = {
    async get(): Promise<ConfigResponse | null> {
        const paths = [UrlUtility.getDashboardBaseUrl(false), "config"];
        try {
            const response = await Http.get<ConfigResponse>(paths);
            return response.body;
        } catch {
            console.log("Unable to load extension config data");
        }

        return null;
    },
} as const;

export { ConfigService };
