// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// auth-utility.ts
// Utility to base64 encode a sequence of octets (URL-safe alphabet, no padding)

import { UrlUtility } from "./url-utility";

const USER_ID_KEY = "userId";
const CLIENT_TOKEN_KEY = "clientToken";
const CLIENT_VERIFIER_KEY = "clientVerifier";
const CLIENT_CHALLENGE_KEY = "clientChallenge";

export interface CodeChallenge {
    verifier: string;
    challenge: string;
}

function b64url(array: Uint8Array): string {
    const b64 = btoa(String.fromCharCode.apply(null, Array.from(array)));
    return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

const AuthUtility = {
    async generateCodeChallenge(): Promise<CodeChallenge> {
        // Generate a 32-octet random sequence
        const rand = window.crypto.getRandomValues(new Uint8Array(32));

        // The PKCE code verifier is the base64url encoding of the random octets
        const verifier = b64url(rand);

        // Calculate the SHA-256 hash of the code verifier
        const data = new TextEncoder().encode(verifier);
        const sha256 = await window.crypto.subtle.digest("SHA-256", data);

        // The PKCE code challenge is the base64url encoding of the hash
        const challenge = b64url(new Uint8Array(sha256));
        return { verifier, challenge } as const;
    },
    // Helper function for retrieving the client token for auth.
    getTokenState(): string {
        const token = localStorage.getItem(CLIENT_TOKEN_KEY);
        return token || "";
    },
    // Helper function for storing the client token.
    storeTokenState(token: string): void {
        localStorage.setItem(CLIENT_TOKEN_KEY, token);
    },
    // Helper function for clearing token.
    clearTokenState() {
        localStorage.removeItem(CLIENT_TOKEN_KEY);
    },
    // Helper function for storing the user identifier.
    storeUserId(id: string) {
        localStorage.setItem(USER_ID_KEY, id);
    },
    // Helper function for retrieving the user identifier.
    getUserId(): string {
        return localStorage.getItem(USER_ID_KEY) || "";
    },
    // Helper function for clearing user id.
    clearUserId() {
        localStorage.removeItem(USER_ID_KEY);
    },
    // Helper function for retrieving the current challenge state.
    getChallengeState(): CodeChallenge | null {
        const verifier = localStorage.getItem(CLIENT_VERIFIER_KEY);
        const challenge = localStorage.getItem(CLIENT_CHALLENGE_KEY);

        if (!verifier || !challenge) {
            return null;
        }

        return {
            verifier,
            challenge,
        } as const;
    },
    // Helper function for storing client challenge state.
    storeChallengeState(state: CodeChallenge) {
        localStorage.setItem(CLIENT_VERIFIER_KEY, state.verifier);
        localStorage.setItem(CLIENT_CHALLENGE_KEY, state.challenge);
    },
    // Remove challenge state.
    clearChallenge() {
        localStorage.removeItem(CLIENT_VERIFIER_KEY);
        localStorage.removeItem(CLIENT_CHALLENGE_KEY);
    },
    // Helper function for returning the redirect path for login.
    getLoginRedirect(): string {
        return `${UrlUtility.getDashboardBaseUrl(true)}/callback`;
    },
} as const;
export { AuthUtility };
