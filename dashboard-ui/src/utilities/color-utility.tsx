// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// color-utility.ts
// Single instance utility for color operations.

import type { JSX } from "react";

interface rgb {
    red: number;
    green: number;
    blue: number;
}

// Helper function for converting hex string ("#FFFFFF") to red, green, blue components.
function hexToRgb(hex: string): rgb {
    return {
        red: parseInt(hex.charAt(1) + hex.charAt(2), 16),
        green: parseInt(hex.charAt(4) + hex.charAt(4), 16),
        blue: parseInt(hex.charAt(5) + hex.charAt(6), 16),
    };
}

const ColorUtility = {
    // Given a string, hashes the string and returns a stable color.
    getStableColor(id: string): string {
        let hash = 0;
        for (let i = 0; i < id.length; i++) {
            hash = id.charCodeAt(i) + ((hash << 5) - hash);
        }
        let color = "#";

        color += ((hash >> 0) & 0xff).toString(16).padStart(2, "0");
        color += ((hash >> 8) & 0xff).toString(16).padStart(2, "0");
        color += ((hash >> 16) & 0xff).toString(16).padStart(2, "0");

        return color;
    },
    // Given a hex color string for a background, returns either "#FFFFFF" or "#000000" as
    // a contrasting foreground color.
    getForegroundFromBackground(background: string): string {
        const { red, green, blue } = hexToRgb(background);
        if (red * 0.299 + green * 0.587 + blue * 0.114 > 186) {
            return "#000000";
        }

        return "#FFFFFF";
    },
    // Given a string, will generate a span containing a color stable tag. Optionally,
    // can add a key to the tag, either a custom one specified or a random one.
    getColorStableTag(
        tag: string,
        key?: string,
        useRandomKey = false
    ): JSX.Element {
        const backgroundColor = this.getStableColor(tag);
        return (
            <span
                key={useRandomKey ? Math.random() : (key ?? undefined)}
                title={tag}
                style={{
                    alignItems: "center",
                    textAlign: "center",
                    borderRadius: "0.5em",
                    backgroundColor: backgroundColor,
                    border: 0,
                    outline: 0,
                    color: this.getForegroundFromBackground(backgroundColor),
                    padding: "0.25em",
                    margin: "0.25em",
                }}
            >
                {tag}
            </span>
        );
    },
} as const;

export { ColorUtility };
