// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/// <reference types="vite/client" />

declare global {
    interface Window {
        litIssuedWarnings?: Set<string>;
    }
}

export {};
