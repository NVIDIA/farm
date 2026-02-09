// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { SupportStatus } from "@nve/elements";
// using native custom element

type Status = SupportStatus | null;

export function ProgressBar({
    progress,
    status,
}: {
    progress?: number;
    status?: Status;
}) {
    progress = Math.floor((progress || 0) * 100);
    return (
        <nve-progress-bar
            status={status ?? undefined}
            value={progress}
        ></nve-progress-bar>
    );
}
