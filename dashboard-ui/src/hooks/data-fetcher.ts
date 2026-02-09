// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect, useRef, useCallback, useMemo } from "react";

function useDataFetcher<A extends unknown[], V>(
    fetchFunction: (...args: A) => Promise<V>
) {
    // state
    const [data, setData] = useState<V | null>(null);
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(Date.now());

    // derived state
    const lastUpdated = useMemo(
        () => new Date(lastRefresh).toLocaleTimeString(),
        [lastRefresh]
    );

    // refs
    const mountedRef = useRef(true);

    // callbacks
    const fetchData = useCallback(
        async (...args: A) => {
            setLoading(true);
            setError("");
            try {
                const result = await fetchFunction(...args);
                if (mountedRef.current) {
                    setData(result);
                }
                setLastRefresh(Date.now());
            } catch (e) {
                const error = e as Error;
                if (mountedRef.current) {
                    setError(error.message);
                }
            } finally {
                if (mountedRef.current) {
                    setLoading(false);
                }
            }
        },
        [fetchFunction]
    );

    // effects
    useEffect(() => {
        mountedRef.current = true;
        return () => {
            mountedRef.current = false;
        };
    }, [fetchData]);

    return {
        data,
        error,
        loading,
        lastUpdated,
        fetchData,
        reset: () => {
            setError("");
        },
    };
}

export { useDataFetcher };
