// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

const UrlUtility = {
    getSearchParams(): URLSearchParams {
        const params = new URLSearchParams(window.location.search);
        return params;
    },
    getSearchParamsFromRecord(
        params: Record<string, string | string[] | undefined>,
        dropUnknownKeys = false
    ): URLSearchParams {
        const searchParams = new URLSearchParams();
        const currentParams = this.getSearchParams();

        // Append each key into the URL search result.
        Object.keys(params).forEach((key) => {
            const value = params[key];

            if (value === undefined || value === null) {
                return;
            }

            if (Array.isArray(value)) {
                value.forEach((v) => searchParams.append(key, v));
                return;
            }

            searchParams.append(key, value);
        });

        if (dropUnknownKeys === false) {
            currentParams.forEach((value, key) => {
                if (key in params === false) {
                    searchParams.append(key, value);
                }
            });
        }

        return searchParams;
    },
    updateSearchHistory(params: URLSearchParams): void {
        // Set the history.
        window.history.replaceState(
            {},
            "",
            `${window.location.pathname}?${params.toString()}`
        );
    },
    willUrlChange(params: URLSearchParams): boolean {
        return params.toString() !== this.getSearchParams().toString();
    },
    getServiceBaseUrl(useFullPath = false): string {
        const index = window.location.pathname.indexOf("/dashboard");

        if (index === -1) {
            return "";
        }

        const subpath = window.location.pathname.substring(0, index);

        if (useFullPath === false) {
            return subpath;
        }

        return `${window.location.origin}${subpath}`;
    },
    getDashboardBaseUrl(useFullPath = false): string {
        const index = window.location.pathname.indexOf("/dashboard");

        if (index === -1) {
            if (useFullPath) {
                return window.location.origin;
            }
            return "";
        }

        const subpath = `${window.location.pathname.substring(0, index)}/dashboard`;

        if (useFullPath === false) {
            return subpath;
        }

        return `${window.location.origin}${subpath}`;
    },
} as const;

export { UrlUtility };
