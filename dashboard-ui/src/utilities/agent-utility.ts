// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

const STATUSES = ["idle", "evicted", "lost", "active"] as const;

const AgentUtility = {
    Statuses: STATUSES,
} as const;

export { AgentUtility };
