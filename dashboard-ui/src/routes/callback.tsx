// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import { Navigate } from "react-router";

// NVIDIA custom elements (loader defined globally)

// Local
import { useUserContext } from "../contexts/user-context/utils";

function Callback(): JSX.Element {
    const { isSignedIn } = useUserContext();

    if (isSignedIn) {
        return <Navigate to="/tasks" />;
    }

    return <nve-page-loader></nve-page-loader>;
}

export { Callback };
