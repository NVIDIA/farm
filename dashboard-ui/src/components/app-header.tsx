// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useCallback, useId } from "react";
import { useNavigate } from "react-router";
import { useUserContext } from "~/contexts/user-context/utils";

export function AppHeader() {
    const user = useUserContext();
    const navigate = useNavigate();
    const dropdownId = useId();
    const loginBtnText = user.userId ? "logout" : "login";

    const onClickLogin = useCallback(() => {
        if (loginBtnText === "logout") {
            user.signOut();
        }

        navigate("/login");
    }, [navigate, user, loginBtnText]);

    return (
        <nve-page-header slot="header">
            <nve-logo slot="prefix" size="sm">
                <img style={{ width: "32px" }} src="logo.png" />
            </nve-logo>
            <h2 slot="prefix" nve-text="heading sm">
                FARM
            </h2>
            <nve-button
                slot="suffix"
                container="flat"
                popovertarget={`app-header-dropdown-${dropdownId}`}
            >
                {user.userId} <nve-icon name="person"></nve-icon>
            </nve-button>
            <nve-dropdown
                id={`app-header-dropdown-${dropdownId}`}
                position="bottom"
                alignment="end"
            >
                <nve-menu>
                    <nve-menu-item onClick={onClickLogin}>
                        <nve-icon name={loginBtnText}></nve-icon> {loginBtnText}
                    </nve-menu-item>
                </nve-menu>
            </nve-dropdown>
        </nve-page-header>
    );
}
