// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { TimeUtility } from "./time-utility";

describe("TimeUtility", () => {
    describe("getLocalDateFromISODate", () => {
        it("should convert an ISO date string to a Date object (start of day)", () => {
            const result = TimeUtility.getLocalDateFromISODate("2025-03-03");
            expect(result).toBeInstanceOf(Date);
            expect(result.getFullYear()).toBe(2025);
            expect(result.getMonth()).toBe(2); // March (zero-based index)
            expect(result.getDate()).toBe(3);
            expect(result.getHours()).toBe(0);
            expect(result.getMinutes()).toBe(0);
            expect(result.getSeconds()).toBe(0);
            expect(result.getMilliseconds()).toBe(0);
        });

        it("should convert an ISO date string to a Date object (end of day)", () => {
            const result = TimeUtility.getLocalDateFromISODate(
                "2025-03-04",
                true
            );
            expect(result).toBeInstanceOf(Date);
            expect(result.getFullYear()).toBe(2025);
            expect(result.getMonth()).toBe(2); // March
            expect(result.getDate()).toBe(4);
            expect(result.getHours()).toBe(23);
            expect(result.getMinutes()).toBe(59);
            expect(result.getSeconds()).toBe(59);
            expect(result.getMilliseconds()).toBe(0);
        });

        it("should handle single-digit month and day correctly", () => {
            const result = TimeUtility.getLocalDateFromISODate("2025-01-09");
            expect(result.getFullYear()).toBe(2025);
            expect(result.getMonth()).toBe(0); // January
            expect(result.getDate()).toBe(9);
        });

        it("should handle leap year dates", () => {
            const result = TimeUtility.getLocalDateFromISODate("2024-02-29");
            expect(result.getFullYear()).toBe(2024);
            expect(result.getMonth()).toBe(1); // February
            expect(result.getDate()).toBe(29);
        });

        it("should return an invalid date for incorrect input format", () => {
            const result = TimeUtility.getLocalDateFromISODate("invalid-date");
            expect(isNaN(result.getTime())).toBe(true);
        });

        it("should return an invalid date for non-numeric input", () => {
            const result = TimeUtility.getLocalDateFromISODate("YYYY-MM-DD");
            expect(isNaN(result.getTime())).toBe(true);
        });

        it("should return an invalid date for out-of-range dates", () => {
            const result = TimeUtility.getLocalDateFromISODate("2025-13-32");
            expect(isNaN(result.getTime())).toBe(true);
        });

        it("should handle empty string input", () => {
            const result = TimeUtility.getLocalDateFromISODate("");
            expect(isNaN(result.getTime())).toBe(true);
        });
    });
});
