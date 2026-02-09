import eslint from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import prettier from "eslint-plugin-prettier";
import react from "eslint-plugin-react";
import prettierConfig from "./.prettierrc.js";

export default defineConfig(
    // Ignore patterns
    { ignores: ["dist", "public", "@nve"] },
    // Base JS and TS recommended flat configs
    eslint.configs.recommended,
    tseslint.configs.recommended,
    // Project-specific overrides
    {
        files: ["**/*.{ts,tsx}"],
        languageOptions: {
            ecmaVersion: 2020,
            globals: globals.browser,
            parserOptions: {
                project: ["./tsconfig.node.json", "./tsconfig.app.json"],
                tsconfigRootDir: import.meta.dirname,
            },
        },
        settings: { react: { version: "18.3" } },
        plugins: {
            react,
            prettier: prettier,
            "react-hooks": reactHooks,
            "react-refresh": reactRefresh,
        },
        rules: {
            ...react.configs.recommended.rules,
            ...react.configs["jsx-runtime"].rules,
            ...reactHooks.configs.recommended.rules,
            "prettier/prettier": ["error", prettierConfig],
            "react-refresh/only-export-components": [
                "warn",
                { allowConstantExport: true },
            ],
            "react/no-unknown-property": [
                "error",
                {
                    ignore: ["nve-layout", "nve-text"],
                },
            ],
        },
    },
);
