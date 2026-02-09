// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External unreferenced import
import "~/elements";
import "~/styles/reset.css";
import "~/styles/fouc.gen.css";
import "~/styles/theme.gen.css";

// External
import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";

// Local
import App from "./app";
import { UserProvider } from "./contexts/user-context";

// Routes
import { Batches } from "./routes/batches";
import { Tasks } from "./routes/tasks";
import { Agents } from "./routes/agents";
import { Task } from "./routes/task";
import { Batch } from "./routes/batch";
import { Taskflows } from "./routes/taskflows";
import { Taskflow } from "./routes/taskflow";
import { TaskEdit } from "./routes/task-edit";
import { UrlUtility } from "./utilities/url-utility";
import { Callback } from "./routes/callback";
import { Job } from "./routes/job";
import { Jobs } from "./routes/jobs";
import { ThemeProvider } from "./contexts/theme-provider";
import { Login } from "./routes/login";

async function enableMocking() {
    if (process.env.NODE_ENV !== "development") {
        return;
    }

    const { worker } = await import("./mocks/browser");

    return worker.start({
        onUnhandledRequest(request, print) {
            if (request.url.startsWith(window.origin)) {
                return;
            }

            // Otherwise, print an unhandled request warning.
            print.warning();
        },
    });
}

enableMocking().then(() => {
    const root = document.getElementById("root") as HTMLElement;

    ReactDOM.createRoot(root).render(
        <StrictMode>
            <ThemeProvider>
                <UserProvider>
                    <BrowserRouter basename={UrlUtility.getDashboardBaseUrl()}>
                        <Routes>
                            <Route path="/" element={<App />}>
                                <Route path="/batches" element={<Batches />} />
                                <Route
                                    path="/batch/:batchId"
                                    element={<Batch />}
                                />
                                <Route
                                    path="/taskflows"
                                    element={<Taskflows />}
                                />
                                <Route
                                    path="/taskflow/:taskflowId"
                                    element={<Taskflow />}
                                />
                                <Route path="/tasks" element={<Tasks />} />
                                <Route path="/task/:id" element={<Task />} />
                                <Route
                                    path="/task/edit/:id"
                                    element={<TaskEdit />}
                                />
                                <Route path="/agents" element={<Agents />} />
                                <Route
                                    path="/callback"
                                    element={<Callback />}
                                />
                                <Route path="/job/:id" element={<Job />} />
                                <Route path="/jobs" element={<Jobs />} />
                                <Route path="/login" element={<Login />} />
                            </Route>
                        </Routes>
                    </BrowserRouter>
                </UserProvider>
            </ThemeProvider>
        </StrictMode>
    );
});
