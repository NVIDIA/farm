// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

const DEFAULT_TASK_TABLE_ROUTE = "/tasks?sort=submissionDate:desc";

const TaskUtility = {
    defaultTaskTableRoute: DEFAULT_TASK_TABLE_ROUTE,
} as const;

export { TaskUtility };
