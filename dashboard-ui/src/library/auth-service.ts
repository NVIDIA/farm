// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import { type JwtPayload, jwtDecode } from "jwt-decode";

export interface AuthToken {
    access_token: string;
    expires_in: number;
    decoded_id: {
        preferred_username: string;
        exp: number;
    };
}

const AuthService = {
    // Generates an auth redirect. Note: will redirect the page. This function does not preserve
    // state and must be part of a stateful flow that preserves challenge once auth has redirected
    // the browser back.
    async redirect(
        codeChallenge: string,
        authUrl: string,
        clientId: string,
        redirectUrl: string
    ): Promise<void> {
        window.location.replace(
            `${authUrl}/authorize?` +
                new URLSearchParams({
                    response_type: "code",
                    client_id: clientId,
                    redirect_uri: redirectUrl,
                    scope: "openid",
                    code_challenge: codeChallenge,
                    code_challenge_method: "S256",
                })
        );
    },
    // Given a auth redirect code, with make a request to the auth api for a token
    // associated with the user's identity.
    async getUserToken(
        authUrl: string,
        redirectUrl: string,
        code: string,
        verifier: string
    ): Promise<AuthToken> {
        const response = await fetch(`${authUrl}/token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                code,
                code_verifier: verifier,
                redirect_uri: redirectUrl,
                grant_type: "authorization_code",
            }),
        });
        const token = await response.json();

        const id = jwtDecode<JwtPayload>(token.id_token);

        return {
            ...token,
            decoded_id: id,
        } as AuthToken;
    },
} as const;

export { AuthService };
