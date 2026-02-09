// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

// Helper function for performing a getIndex with a regex.
function findWithRegex(str: string, startIndex: number, regex: RegExp): number {
    const substr = str.substring(startIndex);
    const index = substr.search(regex);

    if (index === -1) {
        return -1;
    }

    return startIndex + index;
}

const LinkUtility = {
    getWithLinksParsed(str: string | undefined): JSX.Element {
        if (!str) {
            return <></>;
        }

        let composed = "";
        const elements: JSX.Element[] = [];
        let index = 0;

        // Arbitrary loop conditional. Could be while true.
        while (index !== str.length) {
            const foundIndex = str.indexOf("http", index);

            // Add remainder of string.
            if (foundIndex === -1) {
                composed += str.substring(index);
                elements.push(<span key={elements.length}>{composed}</span>);
                break;
            }

            composed += str.substring(index, foundIndex);

            // Add span.
            elements.push(<span key={elements.length}>{composed}</span>);

            // Reset composed.
            composed = "";

            // Find whitespace after.
            const right = findWithRegex(str, foundIndex, /\s/);

            if (right === -1) {
                // If run over the end, then add link to end.
                const link = str.substring(foundIndex);
                elements.push(
                    <a
                        href={link}
                        rel="noreferrer"
                        target="_blank"
                        key={elements.length}
                    >
                        {link}
                    </a>
                );
                break;
            }

            const link = str.substring(foundIndex, right);
            elements.push(
                <a
                    href={link}
                    rel="noreferrer"
                    target="_blank"
                    key={elements.length}
                >
                    {link}
                </a>
            );

            // Setup next iteration.
            index = right;
        }

        return <div>{elements}</div>;
    },
} as const;

export { LinkUtility };
