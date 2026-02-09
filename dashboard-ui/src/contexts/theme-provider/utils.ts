// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { createContext, useContext } from "react";
import { Theme } from "./types";

export const SESSION_STORAGE_THEME_KEY = "__theme";

const themes: Array<Theme> = Object.values(Theme);

const prefersDarkMQ = "(prefers-color-scheme: dark)";

const ThemeContext = createContext<Theme | null>(null);

export function useTheme() {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error("useTheme must be used within a ThemeProvider");
    }
    return context;
}

export function getTheme(): Theme {
    const storedTheme = getStoredTheme();
    return storedTheme ?? getMachineTheme();
}

function getMachineTheme(): Theme {
    if (
        typeof window !== "undefined" &&
        window.matchMedia &&
        window.matchMedia(prefersDarkMQ).matches
    ) {
        // user machine prefers dark mode
        return Theme.DARK;
    }

    // user machine prefers light mode
    return Theme.LIGHT;
}

export function hasStoredTheme(): boolean {
    const storedTheme =
        typeof window === "undefined"
            ? undefined
            : window.sessionStorage.getItem(SESSION_STORAGE_THEME_KEY);

    return Boolean(storedTheme);
}

export function getStoredTheme(): Theme | undefined {
    const storedTheme =
        typeof window !== "undefined" &&
        window.sessionStorage.getItem(SESSION_STORAGE_THEME_KEY);
    return isTheme(storedTheme) ? storedTheme : undefined;
}

export function isTheme(value: unknown): value is Theme {
    return typeof value === "string" && themes.includes(value as Theme);
}
