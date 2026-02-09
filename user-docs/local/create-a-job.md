## Create A Job

**In this guide:**
- [Overview](#overview)
- [Write a Job Definition](#write-a-job-definition)
- [Upload the Job Definition](#upload-the-job-definition)
- [Run the Job via Tasks](#run-the-job-via-tasks)
- [Configure container environment (Farm API mode)](#configure-container-environment-farm-api-mode)
- [Next steps](#next-steps)

### Overview

In this guide, you define a Farm job that builds on the CLI from [Create a Job CLI](create-a-job-cli.md). You'll:
1. Create a Job Definition for the `wordctl` logic
2. Upload the Job Definition to the [Jobs service](index.md#swagger-documentation)
3. Submit a Task that runs the Job via the [Tasks service](index.md#swagger-documentation)


### Write a Job Definition

Below is a minimal Job Definition for `wordctl`. It runs the `wordctl` container and lets you pass subcommands and flags at submit time via `task_args`.

Save as `./user-docs/wordctl.json`:
```json
{
    "name": "wordctl",
    "job_type": "base",
    "command": "python3",
    "args": ["wordctl.py"],
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
    "working_directory": "/<absolute-path-to-repo>/user-docs/wordctl"
}
```

> **Note:**
> - "subcommand" goes to position 0, so you can run `store`, `piglatinize`, `haikuize`, etc.
> - Flags like `--input-node` and `--output-node` are provided at submit time. For multiple report inputs, you can also use `--input-node-list` with a comma-separated list.
> - Failure injection flags `--error`, `--random-error`, and optional `--error-message` are passed through from `task_args` to the container and handled by the subcommands.
> - `working_directory` sets the process current working directory before execution. Any relative paths in `command` or `args` are resolved against this directory. In the example, `args: ["wordctl.py"]` runs the script located in `/.../user-docs/wordctl/wordctl.py`.
> - `args` defines the base argv for the process and is combined with the processed `allowed_args` derived from `task_args` at submit time. The final command line is: `[command, *args, *processed_allowed_args_from_task_args]`.
> - Prefer using an absolute path for `working_directory` (e.g., `/home/alice/repos/nv.svc.farm/user-docs/wordctl`) to avoid path resolution issues. If you do not use an absolute `working_directory`, use an absolute script path in `args` instead (e.g., `"/home/alice/repos/nv.svc.farm/user-docs/wordctl/wordctl.py"`).


### Upload the Job Definition

The Jobs service requires an API key header. For local development, retrieve it from the `farm-jobs` Kubernetes Secret created by DevSpace/Helm.

Upload in one command (no env exports needed):
```bash
curl -X POST \
  "http://localhost:8222/queue/management/jobs/save" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: change-me" \
  --data-binary @./user-docs/wordctl.json
```

Verify it’s loaded by viewing the job in the [dashboard](http://localhost:8222/queue/management/dashboard/job/wordctl)


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
  "http://localhost:8222/queue/management/tasks/submit" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/task.json
```

You can view your running task in the [dashboard](http://localhost:8222/queue/management/dashboard). When it finishes, you’ll likely see an error. Open the task page and check the Logs tab; you should see:

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
                "value": "http://localhost:8222/queue/management/tasks"
            },
            {
                "name": "OV_FARM_RESULTS_ENDPOINT",
                "value": "http://localhost:8222/queue/management/results"
            }
        ]
    }
}
```

Resubmit the task:

```bash
curl -X POST \
  "http://localhost:8222/queue/management/tasks/submit" \
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
curl "http://localhost:8222/queue/management/results/task/<task-id>"
```

Since these environment variables are shared across tasks, prefer setting them in the Job Definition under `capacity_requirements.env`. This lets you remove `task_requirements` from individual tasks.

Resubmit the Job Definition with `capacity_requirements.env`:
```json
{
    "name": "wordctl",
    "job_type": "base",
    "command": "python3",
    "args": ["/home/rpowers/repos/omniverse/microservices/farm/nv.svc.farm/user-docs/wordctl/wordctl.py"],
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
    "capacity_requirements": {
        "env": [
            {
                "name": "OV_FARM_TASKS_ENDPOINT",
                "value": "http://localhost:8222/queue/management/tasks"
            },
            {
                "name": "OV_FARM_RESULTS_ENDPOINT",
                "value": "http://localhost:8222/queue/management/results"
            }
        ]
    },
    "working_directory": "."
}
```

```bash
curl -X POST \
  "http://localhost:8222/queue/management/jobs/save" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: change-me" \
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
  "http://localhost:8222/queue/management/tasks/submit" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @./user-docs/task.json
```

### Next steps

Now that you've created a job and run your first task, continue to [Create a Taskflow](create-a-taskflow.md) to learn about:

- **DAG Orchestration**: Compose multiple tasks into complex workflows with dependencies
- **Fan-out and Fan-in Patterns**: Build parallel processing pipelines
- **Result Coordination**: Pass outputs between tasks across multi-step workflows
