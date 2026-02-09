// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// get words from string
function getWordsFromObjectKey(str: string): string[] {
    return (
        str
            .replace(/_/g, " ") // Convert snake_case to spaces
            // Insert space on lower->UPPER boundaries (camel case)
            .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
            // Insert space between acronym and ProperCase word: URLParser -> URL Parser
            .replace(/([A-Z])([A-Z][a-z])/g, "$1 $2")
            .trim()
            .split(/\s+/)
    );
}

function objectKeyToTitleCase(str: string): string {
    return getWordsFromObjectKey(str)
        .map(
            (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ) // Convert to title case
        .join(" ");
}

function objectKeyToUpperCase(str: string): string {
    return getWordsFromObjectKey(str).join(" ").toUpperCase();
}

const StringUtility = {
    objectKeyToTitleCase,
    objectKeyToUpperCase,
};

export { StringUtility };
