// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useMemo } from "react";
import type { Color } from "@nvidia-elements/core";

const colors = [
    "red-cardinal",
    "gray-slate",
    "gray-denim",
    "blue-indigo",
    "blue-cobalt",
    "blue-sky",
    "teal-cyan",
    "green-mint",
    "teal-seafoam",
    "green-grass",
    "yellow-amber",
    "orange-pumpkin",
    "red-tomato",
    "pink-magenta",
    "purple-plum",
    "purple-violet",
    "purple-lavender",
    "pink-rose",
    "green-jade",
    "lime-pear",
    "yellow-nova",
    "brand-green",
] satisfies readonly Color[];

function hashColor(value: string): Color {
    let hash = 0;

    for (let i = 0; i < value.length; i++) {
        hash += value.charCodeAt(i);
    }

    return colors[hash % colors.length];
}

export default function RandomColorTag({ label }: { label: string }) {
    const color = useMemo(() => hashColor(label), [label]);
    return <nve-tag color={color}>{label}</nve-tag>;
}
