// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useParams } from "react-router";
import { TaskTable } from "~/components/task-table";

function Batch() {
    const { batchId } = useParams();

    return <TaskTable title={`Batch ${batchId || ""}`} batchId={batchId} />;
}

export { Batch };
