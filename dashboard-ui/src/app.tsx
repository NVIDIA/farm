// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import { Navigate, Outlet, useMatch } from "react-router";

// NVIDIA custom elements (loader defined globally)

// Local
import { useUserContext } from "~/contexts/user-context/utils";
import { Login } from "./routes/login";
import { UrlUtility } from "./utilities/url-utility";
import { AppLayout } from "./components/app-layout";
import { TaskUtility } from "./utilities/task-utility";

function SignedInPage(): JSX.Element {
    return (
        <AppLayout>
            <Outlet />
        </AppLayout>
    );
}

function App(): JSX.Element {
    const isRoot = useMatch("/") !== null;
    const { isSignedIn, isConfigLoading } = useUserContext();

    const params = UrlUtility.getSearchParams();
    const hasCode = params.get("code") !== null;

    // If loading remote config, show loading.
    if (isConfigLoading) {
        return <nve-page-loader />;
    }

    // If signed in, load tasks page and show navigation.
    if (isSignedIn) {
        return (
            <>
                <SignedInPage />
                {isRoot && <Navigate to={TaskUtility.defaultTaskTableRoute} />}
            </>
        );
    }

    // If not signed in, but there is a code= in the URL, then
    // the user-context will be parsing the code to request an
    // access token. As such, show the loader.
    if (hasCode) {
        return <nve-page-loader />;
    }

    // If not logged in and not currently processing login, then
    // show the login screen.
    return <Login />;
}

export default App;
