// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// External
import type { JSX } from "react";
import { useEffect } from "react";
import { useParams } from "react-router";
// Local
import { JobsService } from "../library/jobs-service";
import { ContentLoader } from "~/components/content-loader";
import { KeyValueField } from "~/components/key-value-field";
import { useDataFetcher } from "~/hooks/data-fetcher";
import { GridField } from "~/components/grid-field";
import { PageHeader } from "~/components/page-header";

interface ObjectFieldProperties {
    name: string;
    value: Record<string, unknown> | string[] | number[] | undefined;
}

function ObjectField({ name, value }: ObjectFieldProperties): JSX.Element {
    let finalValue = value == null ? "" : value;

    try {
        finalValue = JSON.stringify(value, null, 4);
    } catch {
        finalValue = "";
    }

    return (
        <GridField name={name}>
            <div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {finalValue}
            </div>
        </GridField>
    );
}

function Job(): JSX.Element {
    const params = useParams();
    const id = params.id || "";
    const {
        data: definition,
        loading,
        fetchData,
    } = useDataFetcher(JobsService.get);

    useEffect(() => {
        console.log("Get definition at ", Date.now());
        fetchData(id);
    }, [id, fetchData]);

    return (
        <ContentLoader
            loading={loading}
            nve-layout="column align:stretch gap:xl"
        >
            <PageHeader title="Definition" />
            <div nve-layout="grid gap:md span-items:12">
                <KeyValueField name="name" value={definition?.name} />
                <KeyValueField name="job_type" value={definition?.job_type} />
                <KeyValueField name="command" value={definition?.command} />
                <KeyValueField
                    name="task_function"
                    value={definition?.task_function}
                />
                <KeyValueField
                    name="log_to_stdout"
                    value={definition?.log_to_stdout}
                />
                <KeyValueField
                    name="job_spec_path"
                    value={definition?.job_spec_path}
                />
                <KeyValueField name="headless" value={definition?.headless} />
                <KeyValueField name="active" value={definition?.active} />
                <KeyValueField
                    name="resolved_command_path"
                    value={definition?.resolved_command_path}
                />
                <KeyValueField
                    name="working_directory"
                    value={definition?.working_directory}
                />
                <KeyValueField name="container" value={definition?.container} />

                <ObjectField name="args" value={definition?.args} />
                <ObjectField name="env" value={definition?.env} />
                <ObjectField
                    name="extension_paths"
                    value={definition?.extension_paths}
                />
                <ObjectField
                    name="allowed_args"
                    value={definition?.allowed_args}
                />
                <ObjectField
                    name="success_return_codes"
                    value={definition?.success_return_codes}
                />
                <ObjectField
                    name="capacity_requirements"
                    value={definition?.capacity_requirements}
                />
            </div>
        </ContentLoader>
    );
}

export { Job };
