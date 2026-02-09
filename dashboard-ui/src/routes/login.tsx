// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// routes/login.tsx
import { useNavigate } from "react-router";
import { useUserContext } from "~/contexts/user-context/utils";

function Login() {
    const user = useUserContext();
    const navigate = useNavigate();

    return (
        <div nve-layout="column align:center" style={{ paddingTop: "150px" }}>
            <nve-card container="full" style={{ maxWidth: 750 }}>
                <nve-card-header>
                    <div nve-text="heading lg semibold" nve-layout="pad-y:md">
                        Omniverse Farm Dashboard
                    </div>
                </nve-card-header>
                <nve-card-content>
                    <div nve-layout="grid span-items:6 gap:lg">
                        <div nve-layout="column gap:lg">
                            <div nve-text="semibold">Welcome</div>
                            <div>
                                Welcome to the Omniverse Farm Dashboard. This is
                                an administrative tool for examining current and
                                historical jobs. If you identify a major feature
                                need please reach out to the Microservice team.
                            </div>
                        </div>
                        <div nve-layout="column gap:lg">
                            <div nve-text="semibold">Please Login</div>
                            <form
                                nve-layout="column gap:lg"
                                onSubmit={(e) => {
                                    e.preventDefault();
                                    const formData = new FormData(
                                        e.currentTarget
                                    );
                                    const userId = (formData.get("userId") ||
                                        "") as string;

                                    if (!userId) {
                                        throw new Error("Invalid userId");
                                    }

                                    user.signIn(userId);

                                    navigate("/");
                                }}
                            >
                                <nve-input>
                                    <label htmlFor="userID">
                                        Nvidia User ID
                                    </label>
                                    <input
                                        type="text"
                                        name="userId"
                                        required
                                        placeholder="joe72"
                                    />
                                </nve-input>
                                <nve-button
                                    size="lg"
                                    interaction="emphasis"
                                    type="submit"
                                >
                                    <nve-icon name="person-circle" />
                                    Login
                                </nve-button>
                            </form>
                        </div>
                    </div>
                </nve-card-content>
            </nve-card>
        </div>
    );
}

export { Login };
