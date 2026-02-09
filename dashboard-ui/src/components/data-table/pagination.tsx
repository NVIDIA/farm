// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export default function Pagination({
    totalResults,
    page,
    step,
    onPage,
    onStep,
}: {
    totalResults: number;
    page: number;
    step: number;
    onPage: (page: number) => void;
    onStep: (step: number) => void;
}) {
    return (
        <nve-pagination
            onchange={(e: unknown) => {
                const event = e as {
                    target: { value: number };
                };
                onPage(Math.ceil(event.target.value));
            }}
            onstep-change={(e: unknown) => {
                const event = e as {
                    target: { step: number };
                };
                onStep(event.target.step);
            }}
            container="flat"
            value={page}
            items={totalResults}
            step={step}
            skippable
        ></nve-pagination>
    );
}
