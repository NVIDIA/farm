// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useId, useState } from "react";
import { useNavigate } from "react-router";
import { useUserContext } from "~/contexts/user-context/utils";

export function AppHeader() {
    const user = useUserContext();
    const [hidden, setHidden] = useState(true);
    const navigate = useNavigate();
    const onUserMenuOpen = () => setHidden(false);
    const onUserMenuClose = () => setHidden(true);
    const dropdownId = useId();
    const loginBtnText = user.userId ? "logout" : "login";

    const onClickLogin = useCallback(() => {
        if (loginBtnText === "logout") {
            user.signOut();
        }

        navigate("/login");
    }, [navigate, user, loginBtnText]);

    return (
        <nve-app-header>
            <nve-logo size="sm">
                <img style={{ width: "40px" }} src="logo.png" />
            </nve-logo>
            <h2 slot="title">FARM</h2>
            <nve-button
                id={`app-header-dropdown-${dropdownId}`}
                slot="nav-actions"
                pressed={!hidden}
            >
                <nve-icon name="person"></nve-icon> {user.userId}
            </nve-button>
            <nve-dropdown
                trigger={`app-header-dropdown-${dropdownId}`}
                behavior-trigger
                onopen={onUserMenuOpen}
                onclose={onUserMenuClose}
                hidden={hidden}
                position="bottom"
                alignment="end"
            >
                <nve-menu>
                    <nve-menu-item onClick={onClickLogin}>
                        <nve-icon name={loginBtnText}></nve-icon> {loginBtnText}
                    </nve-menu-item>
                </nve-menu>
            </nve-dropdown>
        </nve-app-header>
    );
}
