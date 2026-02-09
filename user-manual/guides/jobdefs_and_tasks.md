# Job Definitions, Task Types, and Tasks

## Overview

Farm is a scheduling system for executing configurable *tasks* on Windows or Linux systems. Farm organizes and processes workloads using three key components:

- A *task* represents a unit of work submitted to Farm for execution.

- Each task specifies a *task type*, which determines how it should be executed.

- The task type corresponds to a *job definition*, which provides execution details such as the command to run, required arguments, and environment settings.

The mapping between a task's *task type* and a job definition's *name* allows Farm to execute tasks correctly. When a task is submitted, a Farm agent looks up the job definition by its *name*, merges the task-specific information with the predefined job execution details, and then runs the task accordingly.

This guide will explore *job definitions*, differentiate between *base* and *kit-service* job definitions, and explain how tasks are structured in relation to job definitions.

## Job Definitions

A *job definition* serves as a blueprint for executing tasks. It defines how Farm should process a task by specifying the execution details, including:

- The *command* to run

- The *arguments* required for execution

- The *environment settings*

- The *name*, which serves as the identifier that tasks reference via their *task type*

Each job definition contains a *name*, which uniquely identifies it within a Farm instance. When submitting a task, the user specifies the *task type*, which must match the *name* of an existing job definition or the task will stay pending in `submitted` until a matching job definition is found.

### Job Definition Schema

A job definition consists of the following properties:

  Property                  Type                    Description
  ------------------------- ----------------------- ------------------------------------------------------------------------------------------------------------------------------------
  `name`                    `string`                A unique identifier for the job definition. Tasks use this as their `task type`.
  `job_type`                `string`                The type of job, either `base` or `kit-service`.
  `command`                 `string`                The application or script to run.
  `task_function`           `string`                Module to execute when specifying a `kit-service`.
  `working_directory`       `string`                The directory in which the command should be executed.
  `success_return_codes`    `Array<int>`            List of return codes that indicate a successful execution.
  `args`                    `Array<string>`         Static arguments that apply to all tasks using this job definition.
  `allowed_args`            `Dict<string,Dict>`     Arguments that may change per task, defined with default values.
  `env`                     `Dict<string,string>`   Environment variables required for execution.
  `extension_paths`         `Array<string>`         Paths to any additional Kit extensions required.
  `log_to_stdout`           `boolean`               Whether to capture `stdout` and `stderr` logs.
  `headless`                `boolean`               Indicates if the job should run without a GUI.
  `active`                  `boolean`               Specifies if the job definition is enabled.
  `container`               `string`                The Docker image location for containerized execution. The `command` should specify the container entrypoint. **Kubernetes only.**
  `capacity_requirements`   `Dict<string,any>`      Defines resource requirements such as CPU and memory. **Kubernetes only.**

### Sample Job Definition

`/resources/hello-world.kit`

**The `command` needs to be valid for the Farm Agents that will be running this type of job.**

## `base` vs `kit-service` Job Definitions

Farm supports two primary types of job definitions:

### `base` Job Definitions

A *base* job definition is a standalone execution of `command`. It follows a typical batch processing model where Farm executes the command separately for each submitted task.

``` toml
[job.file_conversion]
job_type = "base"
name = "file_conversion"
command = '/usr/bin/converter
success_return_codes = [0]
args = ["--verbose"]
log_to_stdout = true
headless = true
active = true

[job.file_conversion.allowed_args]
source = { arg = "--source", default = "/data/input.file" }
destination = { arg = "--destination", default = "/data/output.file" }

[job.file_conversion.env]
LOG_LEVEL = "info"
```

It is important to differentiate between executable commands versus shell builtins on both Windows and Linux:

- Executables exist as discrete pieces of executable software.

- Shell builtins are implemented within the shell and do not exist independently.

Farm uses `asyncio.create_subprocess_exec` to launch `command`, which will not work with shell commands. To do so, specify the shell as the `command` and the builtin as an argument.

When a task is submitted, the task's `task_args` dictionary is validated against and then merged with the job definition's `allowed_args`, which are then passed onto the `command`.

### `kit-service` Job Definitions

A *kit-service* job definition allows you to launch the Kit application specified in `command` and then call the service endpoint specified in `task_function`, typically implemented in a Kit extension.

This allows you to use the same code for persistent services as well as on-demand execution. It also provides flexibility in regards to how information is passed.

This is how the `create-render` job definition works, in conjunction with the `omni.services.render` Kit extension.

Similar to how the task's `task_args` dictionary is passed to `command`, a task's `task_function_args` is used to pass arguments to the `task_function` during execution. Because this happens outside of the initial command invocation, there is no equivalent to the job definition's `allowed_args`.

## Specifying a Task

A *task* is a unit of work submitted to a Farm instance for execution. Each task must include a *task type*, which is used to locate the corresponding *job definition*, by matching the *task type* to the *name* of a job definition.

### Task Schema

A task consists of the following properties:

  Property               Type                 Description
  ---------------------- -------------------- ---------------------------------------------------------------------------------------------------------------
  `user`                 `string`             The user who submitted the task **(metadata only)**.
  `task_type`            `string`             The `name` of the job definition to use to execute the task.
  `task_args`            `Dict<string,any>`   A dictionary of arguments to pass to the command. This should match the `allowed_args` in the job definition.
  `task_function`        `string`             The task function to call for `kit-service` job definitions.
  `task_function_args`   `Dict<string,any>`   A dictionary of arguments to pass to the `task_function`.
  `task_requirements`    `Dict<string,any>`   A dictionary of capacity requirements for the task **(Kubernetes only)**.
  `task_comment`         `string`             A comment to associate with the task to provide context.
  `priority`             `integer`            A integer to set the relative priority of submitted tasks. Lower numbers have higher priority.
  `metadata`             `Dict<string,any>`   Extensible metadata for defining the task, such as retry values.
  `status`               `string`             The task's status. This should be set to `submitted`.
  `labels`               `Array<string>`      Labels to associate with the task which can be used for filtering which Farm Agents can process the task.

### Sample Task Definitions

Tasks are submitted to a Farm Queue's `/queue/management/tasks/submit` endpoint with the task definition passed as a JSON dictionary.

**hello-world** task

``` json
{
   "user": "Username",
   "task_type": "hello-world",
   "task_args": {},
   "status": "submitted"
}
```

**create-render** task snippet

/resources/task_create-render.json

**The `render_settings` in `task_function_args` was shortened for simplicity. You can use your own `create-render` submission for a full list of arguments.**

### Submitting Tasks

Submitting the hello-world task using `curl` from a Linux shell, as an example.

``` shell
curl -X 'POST' \
   'http://localhost:8222/queue/management/tasks/submit' \
   -H 'accept: application/json' \
   -H 'Content-Type: application/json' \
   -d '{
   "user": "Username",
   "task_type": "hello-world",
   "task_args": {},
   "status": "submitted"
}
```

Typically, Farm task submission is embedded in purpose-built UIs such as Movie Capture.
