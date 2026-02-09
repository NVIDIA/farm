// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import React, { useCallback, useEffect, useState } from "react";

// Local
import { AuthService } from "../../library/auth-service";
import { Config } from "../../library/config";
import { ConfigService } from "../../library/config-service";
import { AuthUtility } from "../../utilities/auth-utility";
import { UrlUtility } from "../../utilities/url-utility";
import { UserContext } from "./utils";

async function loadConfig() {
    const remoteConfig = await ConfigService.get();

    if (!remoteConfig) {
        console.log("No remote config loaded, skipping");
        return;
    }

    const renamedConfig = {
        authClientId: remoteConfig.auth_client_id,
        authLoginUrl: remoteConfig.auth_login_url,
        isAuthEnabled: remoteConfig.auth_enabled,
    };

    console.log("Remote config loaded", remoteConfig);
    console.log("Merging remote config into main config...");

    Config.merge(renamedConfig);

    console.log("Config merged, result", Config.getConfig());
}

// Async function for handling login state and all appropriate
// login transitions.
async function handleAuth(isSignedIn: boolean, isCallbackRoute: boolean) {
    const authUrl = Config.get("authLoginUrl");
    const authId = Config.get("authClientId");
    const redirect = AuthUtility.getLoginRedirect();

    if (isSignedIn === false && isCallbackRoute === false) {
        console.log("User is not logged in, redirecting to login");

        // Need to log in. Force a redirect.
        const state = await AuthUtility.generateCodeChallenge();

        // Store challenge, as it will be needed on redirect to /callback.
        AuthUtility.storeChallengeState(state);

        console.log(
            "Initiating auth redirect",
            redirect,
            authId,
            authUrl,
            state
        );

        // Use the challenge to invoke a auth login. This will cause a
        // client redirect to login. After login, the browser will be redirected
        // to /callback.
        await AuthService.redirect(state.challenge, authUrl, authId, redirect);

        // Should not actually be reached, as startAuthFlow will change
        // the page URL.
        return;
    }

    if (isSignedIn === false && isCallbackRoute) {
        // Need to process auth and retrieve and store token.
        console.log("Callback route, user is not logged in, handling callback");
        const params = UrlUtility.getSearchParams();
        const authCode = params.get("code");
        const state = AuthUtility.getChallengeState();

        if (!state) {
            console.error("No stored auth state");
            return;
        }

        if (!authCode) {
            console.error("Redirected without auth code");
            return;
        }

        const authToken = await AuthService.getUserToken(
            authUrl,
            redirect,
            authCode,
            state.verifier
        );

        // Store access token.
        AuthUtility.storeTokenState(authToken.access_token);

        // Store username.
        AuthUtility.storeUserId(authToken.decoded_id.preferred_username);

        // Redirect (this will force the context to be rebuilt, as the site will reload, so
        // no need to set state).
        window.location.replace(UrlUtility.getDashboardBaseUrl(true));
    }
}

function UserProvider(
    props: React.PropsWithChildren<Record<string, unknown>>
): JSX.Element {
    const [clientToken, setClientToken] = useState<string>(
        AuthUtility.getTokenState()
    );
    const [userId, setUserId] = useState<string>(AuthUtility.getUserId());
    const [isSignedIn, setIsSignedIn] = useState<boolean>(!!userId);
    const [isConfigLoading, setIsConfigLoading] = useState<boolean>(true);

    console.log("Is signed in", isSignedIn);

    // Handle merging in any required configurations.
    Config.merge({
        basePath: UrlUtility.getServiceBaseUrl(true),
    });

    const isCallbackRoute = window.location.pathname.indexOf("callback") !== -1;

    const handleAsyncState = useCallback(async () => {
        console.log("Loading remote config");
        setIsConfigLoading(true);
        await loadConfig();
        setIsConfigLoading(false);
        if (Config.get("isAuthEnabled")) {
            console.log("Handling auth");
            await handleAuth(isSignedIn, isCallbackRoute);
        }
        console.log("User context all done");
    }, [isSignedIn, isCallbackRoute]);

    // Force auth to occur when the page is mounted.
    useEffect(() => {
        handleAsyncState()
            .then(() => console.log("All async state handled"))
            .catch((error) => console.error("Error with async state", error));
    }, [handleAsyncState]);

    // Helper function for clearing out all auth state.
    function signOut() {
        // Clear stored state in the browser.
        AuthUtility.clearChallenge();
        AuthUtility.clearTokenState();
        AuthUtility.clearUserId();

        // Clear react state.
        setUserId("");
        setClientToken("");
        setIsSignedIn(false);
    }

    // Helper function to initiate sign in.
    const signIn = useCallback(
        async (id?: string) => {
            if (Config.get("isAuthEnabled")) {
                // Auth auth enabled.
                await handleAuth(isSignedIn, isCallbackRoute);
                return;
            }

            if (!id) {
                return;
            }

            // Auth not enabled, use a simple string.
            setUserId(id);
            setIsSignedIn(true);
            AuthUtility.storeUserId(id);
        },
        [isSignedIn, isCallbackRoute]
    );

    return (
        <UserContext.Provider
            value={{
                userId,
                isSignedIn,
                signIn,
                signOut,
                clientToken,
                isConfigLoading,
            }}
        >
            {props.children}
        </UserContext.Provider>
    );
}

export { UserProvider };
