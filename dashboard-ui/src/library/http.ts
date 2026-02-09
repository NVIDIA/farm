// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

// Http
// An environment agnostic wrapper around http interactions. Under the covers, this uses
// axios; however, the implementation can be changed in the future based on needs
// without causing cascading changes throughout the library.

// Explicitly alias Axios types for easy portability to another library.
export type HttpHeaders = AxiosRequestConfig["headers"];
export type HttpUrlParameters = AxiosRequestConfig["params"];
export interface HttpResponse<Body> {
    status: number;
    statusText?: string;
    body: Body;
}
export type HttpProtocol = "http" | "https" | "";

// Possible function names used on the axios object.
type AxiosFunctions = "get" | "put" | "post" | "delete";

// Error thrown by Axios.
interface AxiosHttpError extends Error {
    response: AxiosResponse;
}

// Custom error thrown when there's an issue with an http interaction.
export interface HttpError extends Error {
    response: {
        status: number;
        statusText: string;
        body: AxiosResponse["data"];
    };
}

// Simple serializer for encoding URL parameters. This is needed as the backend
// does not currently support array parameters with keys that have brackets, e.g.:
// status[]=pending&status[]=cancelled.
function paramsSerializer(incoming: HttpUrlParameters): string {
    const paramString = Object.keys(incoming).reduce((accumulator, key) => {
        const value = incoming[key];
        const encodedKey = encodeURIComponent(key);

        if (accumulator.length > 0) {
            accumulator += "&";
        }

        if (Array.isArray(value)) {
            accumulator += value
                .map((v) => `${encodedKey}=${encodeURIComponent(v)}`)
                .join("&");
        } else {
            accumulator += `${encodedKey}=${encodeURIComponent(value)}`;
        }

        return accumulator;
    }, "");

    return paramString;
}

// Helper function for merging a path array into a string. Will remove any empty paths and
// will also remove any empty path identifiers.
function mergePaths(paths: string[]): string {
    return paths.filter((path) => path && path !== "/").join("/");
}

// Helper function for creating a consistent request/response format for axios.
async function invokeAxios<Response, Body = undefined>(
    paths: string | string[],
    functionName: AxiosFunctions,
    parameters?: HttpUrlParameters,
    headers?: HttpHeaders,
    body?: Body
): Promise<HttpResponse<Response>> {
    const axiosFunction = axios[functionName];

    // Composite URL into a final form ready for the request.
    const finalUrl = typeof paths === "string" ? paths : mergePaths(paths);

    try {
        const config = {
            params: parameters,
            headers,
            paramsSerializer,
        } as const;

        const { status, data } = await (body
            ? axiosFunction(finalUrl, body, config)
            : await axiosFunction(finalUrl, config));

        // Create a consistent success response object with only the fields api users will expect, not the full
        // axios implementation.
        const response = {
            status,
            body: data,
        } as const;
        return response;
    } catch (e) {
        if (e && typeof e === "object" && "response" in e) {
            const axiosResponse = (e as AxiosHttpError)
                .response as AxiosResponse;

            // Create a consistent error response object with only the fields api users will expect, not the full
            // axios implementation.
            const response = {
                status: axiosResponse.status,
                statusText: axiosResponse.statusText,
                body: axiosResponse.data,
            } as const;

            // Overwrite axios response to be a custom one.
            (e as HttpError).response = response;
        }

        // Rethrow.
        throw e;
    }
}

// Single instance named exported component.
const Http = {
    async get<Response>(
        paths: string | string[],
        parameters?: HttpUrlParameters,
        headers?: HttpHeaders
    ): Promise<HttpResponse<Response>> {
        return invokeAxios<Response>(paths, "get", parameters, headers);
    },
    async put<Body, Response>(
        paths: string | string[],
        body: Body,
        headers?: HttpHeaders
    ): Promise<HttpResponse<Response>> {
        return invokeAxios<Response, Body>(
            paths,
            "put",
            undefined,
            headers,
            body
        );
    },
    async post<Body, Response>(
        paths: string | string[],
        body: Body,
        headers?: HttpHeaders
    ): Promise<HttpResponse<Response>> {
        return invokeAxios<Response, Body>(
            paths,
            "post",
            undefined,
            headers,
            body
        );
    },
    async delete<Response>(
        paths: string | string[],
        headers?: HttpHeaders
    ): Promise<HttpResponse<Response>> {
        return invokeAxios<Response>(paths, "delete", undefined, headers);
    },
} as const;

export { Http };
