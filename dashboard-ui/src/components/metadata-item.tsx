// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

function MetadataItem({ label, value }: { label: string; value: unknown }) {
    return (
        <div nve-layout="column gap:sm align:start">
            <span nve-text="body sm muted">{label}</span>
            <span nve-text="body sm bold">{String(value)}</span>
        </div>
    );
}

export { MetadataItem };
