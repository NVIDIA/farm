// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import { createContext, useContext } from "react";

interface UserContextDefinition {
    userId: string | null;
    isSignedIn: boolean;
    signIn: (id?: string) => Promise<void>;
    signOut: () => void;
    clientToken: string;
    isConfigLoading: boolean;
}

const UserContext = createContext<UserContextDefinition>({
    userId: null,
    isSignedIn: false,
    signIn: async () => {},
    signOut: () => {},
    clientToken: "",
    isConfigLoading: true,
});

const useUserContext = (): UserContextDefinition => useContext(UserContext);

export { UserContext, useUserContext };
