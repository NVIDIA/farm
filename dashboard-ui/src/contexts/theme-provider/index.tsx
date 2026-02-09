// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ReactNode } from "react";
import { createContext, useEffect, useState } from "react";
import { themeClass } from "~/styles/theme.gen.css";
import { Theme } from "./types";
import { getTheme, hasStoredTheme } from "./utils";

const prefersDarkMQ = "(prefers-color-scheme: dark)";

const ThemeContext = createContext<Theme | null>(null);

function ThemeProvider({
    children,
    overrideTheme,
}: {
    children: ReactNode;
    overrideTheme?: Theme;
}) {
    const [theme, setTheme] = useState<Theme>(overrideTheme ?? getTheme());

    useEffect(() => {
        if (overrideTheme) {
            setTheme(overrideTheme);
        }
    }, [overrideTheme]);

    useEffect(() => {
        document.documentElement.setAttribute("nve-theme", theme);
        document.documentElement.classList.add(themeClass);
    }, [theme]);

    useEffect(() => {
        const mediaQuery = window.matchMedia(prefersDarkMQ);
        const handleChange = () => {
            if (!hasStoredTheme()) {
                setTheme(mediaQuery.matches ? Theme.DARK : Theme.LIGHT);
            }
        };
        mediaQuery.addEventListener("change", handleChange);
        return () => mediaQuery.removeEventListener("change", handleChange);
    }, []);

    return (
        <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
    );
}

export { ThemeProvider };
