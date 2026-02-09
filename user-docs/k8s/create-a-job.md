## Create A Job

**In this guide:**
- [Overview](#overview)
- [Write a Job Definition](#write-a-job-definition)
- [Upload the Job Definition](#upload-the-job-definition)
- [Run the Job via Tasks](#run-the-job-via-tasks)
- [Configure container environment (Farm API mode)](#configure-container-environment-farm-api-mode)
- [Next steps](#next-steps)

### Overview

In this guide, you define a Farm job that uses the container from [Create a Job Container](create-a-job-container.md). You'll:
1. Create a Job Definition for the `wordctl` container
2. Upload the Job Definition to the [Jobs service](index.md#swagger-documentation)
3. Submit a Task that runs the Job via the [Tasks service](index.md#swagger-documentation)


### Write a Job Definition

Below is a minimal Job Definition for `wordctl`. It runs the `wordctl` container and lets you pass subcommands and flags at submit time via `task_args`.

Save as `./user-docs/wordctl.json`:
```json
{
    "name": "wordctl",
    "job_type": "base",
    "command": "wordctl",
    "args": [],
    "allowed_args": {
        "subcommand": { "arg": "0" },
        "text": { "arg": "1" },
        "input_node": { "arg": "--input-node", "separator": " " },
        "output_node": { "arg": "--output-node", "separator": " " },
        "input_node_list": { "arg": "--input-node-list", "separator": " " },
        "error": { "arg": "--error" },
        "random_error": { "arg": "--random-error" },
        "error_message": { "arg": "--error-message", "separator": " " }
    },
    "success_return_codes": [0],
    "container": "wordctl:dev"
}
```

> **Note:**
> - "subcommand" goes to position 0, so you can run `store`, `piglatinize`, `haikuize`, etc.
> - Flags like `--input-node` and `--output-node` are provided at submit time. For multiple report inputs, you can also use `--input-node-list` with a comma-separated list.
> - Failure injection flags `--error`, `--random-error`, and optional `--error-message` are passed through from `task_args` to the container and handled by the subcommands.


### Upload the Job Definition

The Jobs service requires an API key header. For local development, retrieve it from the `farm-jobs` Kubernetes Secret created by DevSpace/Helm.

Upload in one command (no env exports needed):
```bash
curl -X POST \
  "http://farm.127-0-0-1.nip.io:8080/queue/management/jobs/save" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $(kubectl get secret -n farm farm-jobs -o jsonpath='{.data.api_key}' | base64 -d)" \
  --data-binary @./user-docs/wordctl.json
```

Verify it’s loaded by viewing the job in the [dashboard](http://farm.127-0-0-1.nip.io:8080/queue/management/dashboard/job/wordctl)


### Run the Job via Tasks

Submit a Task that references the Job by name using `task_type`. Start by seeding data with the `store` subcommand.

Create `./user-docs/task.json`:
```json
{
    "user": "local-user",
    "task_type": "wordctl",
    "task_comment": "store-data-node",
    "task_args": {
        "subcommand": "store",
        "output_node": "store-data-node",
        "text": "A Quick Brown Fox Jumped Over The Lazy Dog"
    },
    "metadata": {
        "_retry": {
            "is_retryable": false
        }
    }
}
```

Submit the Task:
```bash
curl -X POST \
  "http://farm.127-0-0-1.nip.io:8080/queue/management/tasks/submit" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/task.json
```

You can view your running task in the [dashboard](http://farm.127-0-0-1.nip.io:8080/queue/management/dashboard). When it finishes, you’ll likely see an error. Open the task page and check the Logs tab; you should see:

```bash
  File "/app/store/farm_apis.py", line 18, in <module>
    raise ValueError("OV_FARM_RESULTS_ENDPOINT, OV_FARM_TASKS_ENDPOINT, and OV_FARM_TASK_ID must be set")
ValueError: OV_FARM_RESULTS_ENDPOINT, OV_FARM_TASKS_ENDPOINT, and OV_FARM_TASK_ID must be set
Process exited with return code: -1
```

### Configure container environment (Farm API mode)

Our task failed because the CLI expects certain environment variables to be set. You can solve this in two ways: set the variables in the task definition or in the Job Definition. Farm injects `OV_FARM_TASK_ID` automatically, but you must provide the service endpoints the CLI expects: `OV_FARM_RESULTS_ENDPOINT` ([Results service](index.md#swagger-documentation)) and `OV_FARM_TASKS_ENDPOINT` ([Tasks service](index.md#swagger-documentation)).

Let's first fix this by updating the task definition under `task_requirements.env`.

Update `./user-docs/task.json`
```json
{
    "user": "local-user",
    "task_type": "wordctl",
    "task_comment": "store-data-node",
    "task_args": {
        "subcommand": "store",
        "output_node": "store-data-node",
        "text": "A Quick Brown Fox Jumped Over The Lazy Dog"
    },
    "metadata": {
        "_retry": {
            "is_retryable": false
        }
    },
    "task_requirements": {
        "env": [
            {
                "name": "OV_FARM_TASKS_ENDPOINT",
                "value": "http://farm-tasks.farm.svc.cluster.local/queue/management/tasks"
            },
            {
                "name": "OV_FARM_RESULTS_ENDPOINT",
                "value": "http://farm-results.farm.svc.cluster.local/queue/management/results"
            }
        ]
    }
}
```

Resubmit the task:

```bash
curl -X POST \
  "http://farm.127-0-0-1.nip.io:8080/queue/management/tasks/submit" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/task.json
```

Verify success in the Logs tab; you should see:

```bash
#### Agent ID: farm-controller-599fc5f87d-wtq8g-1
Process exited with return code: 0
```

We can also verify that the data was stored in the [Results service](index.md#swagger-documentation):

```bash
# Input your task id <task-id>
curl "http://farm.127-0-0-1.nip.io:8080/queue/management/results/task/<task-id>"
```

Since these environment variables are shared across tasks, prefer setting them in the Job Definition under `capacity_requirements.env`. This lets you remove `task_requirements` from individual tasks.

Resubmit the Job Definition with `capacity_requirements.env`:
```json
{
    "name": "wordctl",
    "job_type": "base",
    "command": "wordctl",
    "args": [],
    "allowed_args": {
        "subcommand": { "arg": "0" },
        "text": { "arg": "1" },
        "input_node": { "arg": "--input-node", "separator": " " },
        "output_node": { "arg": "--output-node", "separator": " " },
        "input_node_list": { "arg": "--input-node-list", "separator": " " },
        "error": { "arg": "--error" },
        "random_error": { "arg": "--random-error" },
        "error_message": { "arg": "--error-message", "separator": " " }
    },
    "success_return_codes": [0],
    "container": "wordctl:dev",
    "capacity_requirements": {
        "env": [
            {
                "name": "OV_FARM_TASKS_ENDPOINT",
                "value": "http://farm-tasks.farm.svc.cluster.local/queue/management/tasks"
            },
            {
                "name": "OV_FARM_RESULTS_ENDPOINT",
                "value": "http://farm-results.farm.svc.cluster.local/queue/management/results"
            }
        ]
    }
}
```

```bash
curl -X POST \
  "http://farm.127-0-0-1.nip.io:8080/queue/management/jobs/save" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $(kubectl get secret -n farm farm-jobs -o jsonpath='{.data.api_key}' | base64 -d)" \
  --data-binary @./user-docs/wordctl.json
```

Resubmit the task without `task_requirements`:

```json
{
    "user": "local-user",
    "task_type": "wordctl",
    "task_comment": "store-data-node",
    "task_args": {
        "subcommand": "store",
        "output_node": "store-data-node",
        "text": "A Quick Brown Fox Jumped Over The Lazy Dog"
    },
    "metadata": {
        "_retry": {
            "is_retryable": false
        }
    }
}
```

```bash
curl -X POST \
  "http://farm.127-0-0-1.nip.io:8080/queue/management/tasks/submit" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/task.json
```

### Next steps

Now that you've created a job and run your first task, continue to [Create a Taskflow](create-a-taskflow.md) to learn about:

- **DAG Orchestration**: Compose multiple tasks into complex workflows with dependencies
- **Fan-out and Fan-in Patterns**: Build parallel processing pipelines
- **Result Coordination**: Pass outputs between tasks across multi-step workflows
