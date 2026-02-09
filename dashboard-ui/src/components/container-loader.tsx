// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ContainerLoaderModal } from "./container-loader.css";

export function ContainerLoader({ loading }: { loading: boolean }) {
    return (
        <>
            {loading && (
                <>
                    <div
                        nve-layout="row align:horizontal-center full"
                        className={ContainerLoaderModal}
                    >
                        <div style={{ paddingTop: "200px" }}>
                            <nve-progress-ring
                                status="accent"
                                size="xl"
                            ></nve-progress-ring>
                        </div>
                    </div>
                </>
            )}
        </>
    );
}
