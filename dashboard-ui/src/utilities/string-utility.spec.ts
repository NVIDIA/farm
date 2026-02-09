// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { StringUtility } from "./string-utility";

describe("StringUtility.objectKeyToTitleCase", () => {
    it("should convert space-separated words to title case", () => {
        expect(StringUtility.objectKeyToTitleCase("hello world")).toBe(
            "Hello World"
        );
        expect(StringUtility.objectKeyToTitleCase("this is a test")).toBe(
            "This Is A Test"
        );
    });

    it("should convert snake_case to title case", () => {
        expect(StringUtility.objectKeyToTitleCase("hello_world")).toBe(
            "Hello World"
        );
        expect(StringUtility.objectKeyToTitleCase("this_is_a_test")).toBe(
            "This Is A Test"
        );
    });

    it("should convert camelCase to title case", () => {
        expect(StringUtility.objectKeyToTitleCase("helloWorld")).toBe(
            "Hello World"
        );
        expect(StringUtility.objectKeyToTitleCase("thisIsATest")).toBe(
            "This Is A Test"
        );
    });

    it("should handle mixed snake_case and camelCase", () => {
        expect(StringUtility.objectKeyToTitleCase("this_isMyExample")).toBe(
            "This Is My Example"
        );
        expect(StringUtility.objectKeyToTitleCase("my_snakeCaseString")).toBe(
            "My Snake Case String"
        );
    });

    it("should handle single words", () => {
        expect(StringUtility.objectKeyToTitleCase("hello")).toBe("Hello");
        expect(StringUtility.objectKeyToTitleCase("world")).toBe("World");
    });

    it("should handle empty strings", () => {
        expect(StringUtility.objectKeyToTitleCase("")).toBe("");
    });

    it("should handle already formatted title case strings", () => {
        expect(StringUtility.objectKeyToTitleCase("Hello World")).toBe(
            "Hello World"
        );
        expect(StringUtility.objectKeyToTitleCase("This Is A Test")).toBe(
            "This Is A Test"
        );
    });

    it("should handle strings with multiple spaces or underscores", () => {
        expect(StringUtility.objectKeyToTitleCase("  hello   world  ")).toBe(
            "Hello World"
        );
        expect(StringUtility.objectKeyToTitleCase("hello___world")).toBe(
            "Hello World"
        );
    });
});

describe("StringUtility.objectKeyToUpperCase", () => {
    it("should convert camelCase to spaced upper case", () => {
        expect(StringUtility.objectKeyToUpperCase("helloWorld")).toBe(
            "HELLO WORLD"
        );
        expect(StringUtility.objectKeyToUpperCase("thisIsATest")).toBe(
            "THIS IS A TEST"
        );
    });

    it("should handle mixed leading uppercase sequences", () => {
        expect(StringUtility.objectKeyToUpperCase("myURLParser")).toBe(
            "MY URL PARSER"
        );
        expect(StringUtility.objectKeyToUpperCase("HelloWorld")).toBe(
            "HELLO WORLD"
        );
    });

    it("should leave non-camel delimiters untouched", () => {
        expect(StringUtility.objectKeyToUpperCase("hello_world")).toBe(
            "HELLO WORLD"
        );
    });

    it("should handle single and empty strings", () => {
        expect(StringUtility.objectKeyToUpperCase("hello")).toBe("HELLO");
        expect(StringUtility.objectKeyToUpperCase("")).toBe("");
    });
});
