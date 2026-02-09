# Testing Your Farm Instance

With your Farm instance up and running, you'll want to confirm that everything is functioning as it should. This includes verifying that the underlying services are operational and that your agents are configured to accept and execute CPU and GPU tasks.

In this guide, you'll use predefined job definitions to test your instance. We'll walk through the steps to add the job definitions to your Farm instance, submit tasks for execution, and review the results to confirm everything is working properly.

Before getting started, ensure you have:

- Access to an active Farm instance.

- Permissions to add and manage job definitions.

For details on creating your own job definitions, refer to the `creating_job_definitions` guide.

## Basic Service Check

This guide will use the default configuration values for accessing the Farm services. You will need to replace these with the proper values for your Farm instance.

hostname: `localhost` port: `8222` api_key: `<change-me>`

The most basic check you can perform is calling the Farm service's `/status` endpoint using `curl`. This works the same on Windows and Linux.

``` shell
curl http://localhost:8222/status
"OK"
```

**Ensure that you use the proper host and port, for the service that you want to check.**

If the service has not been started, has failed or you specified an incorrect host or port, you will see:

``` shell
curl http://localhost:8222/status
curl: (7) Failed to connect to localhost port 8222 after 2033 ms: Could not connect to server
```

To troubleshoot:

1.  Confirm that the address and port are correct, wait a few moments and retry the endpoint.

2.  Use the `curl` error code and the service's log if it continues to fail.

In addition, each component service has its own `../status` endpoint that you can call, if it has been configured to run on that host and port.

``` shell
curl http://localhost:8222/queue/management/tasks/status
"OK"

curl http://localhost:8222/agent/status
"OK"
```

Now that you have confirmed that your Farm's services are available, let's run our first job.

## Background

Farm relies on Job Definitions to process and execute tasks. These templates specify the commands, arguments, and environment required for execution. A task can only be processed if a properly configured Farm Agent with a matching job definition is available. While the Job Definition provides the structure, the submitted tasks contain the specific inputs needed for execution.

## Hello World

We will add a simple `hello-world` job definition that uses Python to print "Hello World".

/resources/hello-world.kit `hello-world.kit</resources/hello-world.kit>`

Depending on your system configuration, you may need to adjust the command to use either `python` or `python3`. This works on both Windows and Linux.

### Uploading to Farm

Farm stores Job Definitions in Job Stores. In its default configuration, Farm uses the jobs service to manage job definitions in a configurable location. Farm Agents then request job definitions by calling the jobs service's `/load` endpoint.

The jobs service also exposes `/save` and `/remove` endpoints for uploading new definitions and removing unneeded ones.

We are going to use the jobs service's `/queue/management/jobs/save` endpoint to upload our `hello-world.kit` file. We will use the `job_definition_upload.py` python script to make it easier.

``` shell
python job_definition_upload.py hello-world.kit --farm-url http://localhost:8222 --api-key change-me
```

`job_definition_upload.py</resources/job_definition_upload.py>`

You should see the following:

``` shell
NOTE: There is no container defined for 'hello-world'.
Found '1' Job definition(s) in 'hello-world.kit

Uploading Job definition: 'hello-world
Response: {'job-name': 'hello-world', 'success': True}
```

You want to verify that the response contains `'success': True`

The note regarding a container is only important if uploading a job definition for use in a Kubernetes environment, where a container is required.

### Querying Job Definitions

We can now call the jobs service's `load` endpoint to retrieve all of its job definitions. This is exactly what a Farm Agent will do in the default configuration.

``` shell
curl http://localhost:8222/queue/management/jobs/load
```

You should see the following:

``` json
{"hello-world":{"name":"hello-world","job_type":"base","command":"python","args":["-c","Hello World!"],"task_function":"","env":{},"log_to_stdout":true,"extension_paths":[],"allowed_args":{},"job_spec_path":"C:\\Users\\hvera\\AppData\\Local\\nvidia\\nv-svc-farm\\job-definitions\\hello-world.kit","headless":true,"active":true,"unresolved_command_path":"python","success_return_codes":[0],"capacity_requirements":{},"working_directory":"","container":""}}
```

This is the `hello-world` job definition returned as a JSON dictionary. If you have additional job definitions already uploaded, you will see those as well.

You can specify a filter to use when querying for the job definitions:

``` shell
curl http://localhost:8222/queue/management/jobs/load?filter="hello"
```

Only letters, numbers, '." and '\*" can be used with the `filter` query parameter.

### Submitting a Task

With the `hello-world` job definition uploaded to your farm instance, its time to submit a task to ensure your Farm instance is working.

For testing, we will use the `curl` command.

Windows & Linux shell

``` shell
curl -X POST http://localhost:8222/queue/management/tasks/submit -H "accept: application/json" -H "Content-Type: application/json" -d "{\"user\": \"Username\",\"task_type\":\"hello-world\",\"task_args\": {}, \"task_function\": \"\", \"task_function_args\": {}, \"task_requirements\": {}, \"task_comment\": \"my first test\", \"status\": \"submitted\"}"
```

Windows Powershell

``` shell
$body = @{
   user               = "Username"
   task_type          = "hello-world"
   task_args          = @{}
   task_function      = ""
   task_function_args = @{}
   task_requirements  = @{}
   task_comment       = "my first test"
   status             = "submitted"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8222/queue/management/tasks/submit" `
   -Method Post `
   -Headers @{ "accept"="application/json"; "Content-Type"="application/json" } `
   -Body $body
```

If the task was submitted successfully, this will return a task ID that can be used for querying information about the submitted task.

``` json
{"task_id":"736c51a7-44e8-402c-ade9-6b2ceb508cd0"}
```

The `task_id` is what you will use in subsequent calls to query the state and logs of the submitted tasks.

If you receive an error, confirm the following:

- hostname and port are correct for your Farm instance

- services are up and running **(see previous steps)**

- `hello-world` job definition has been uploaded and appears in the queried list

### Check Task Status

You can use the endpoint `queue/management/tasks/info/{task_id}` to query information about a task. The information returned will vary depending on its state (i.e., submitted vs finished). Make sure you replace the task_id, below, with the value returned in the previous step.

``` shell
curl -X GET http://localhost:8222/queue/management/tasks/info/736c51a7-44e8-402c-ade9-6b2ceb508cd0 -H "accept: application/json"
```

This should return something similar to:

``` json
{
   "task_id": "736c51a7-44e8-402c-ade9-6b2ceb508cd0",
   "task_type": "hello-world",
   "task_args": {},
   "task_function": "",
   "task_function_args": {},
   "task_requirements": {},
   "status": "finished",
   "userid": "Username",
   "task_comment": "",
   "task_details": "",
   "metrics": "",
   "progress": {
      "current_step_index": 0,
      "total_step_count": 0,
      "progress": 0,
      "status_message": "",
      "time_remaining": 0
   },
   "task_submission_time": 1736343285.882784,
   "priority": 65535,
   "metadata": {
      "original_submitter": "Username"
   },
   "labels": []
}
```

Here you can see that the `status` is `finished`.

### Check Task Logs

The endpoint `queue/management/logs/{task_id}` can be used to query the task's output logs. Since the `hello-world` job type simply outputs the text "Hello_World!", we can use this to ensure it ran properly. Make sure you replace the `task_id` in the query below with the one provided in the API response from your submission.

``` shell
curl -X GET http://localhost:8222/queue/management/logs/736c51a7-44e8-402c-ade9-6b2ceb508cd0?latest_only=true -H "accept: application/json"
```

And the result:

``` json
{
   "created_at": 1736346918.0343459,
   "updated_at": 1736346918.0343459,
   "logs": "\n#### Agent ID: myagent.mycompany.com-20452\nHello_World!\r\nProcess exited with return code: 0"
}
```

As long as your application outputs continuous logging, you can query it repeatedly while it is running.

### Using the Farm Dashboard and OpenAPI portals

This guide has focused on demonstrating how you can use some of the service endpoints to get information about your Farm instance. However, using the Farm Dashboard and the OpenAPI portal allow you to interactively query the state of your Farm instance:

Farm Queue Dashboard - `http://localhost:8222/queue/management/dashboard`

:   Allows you monitor your Farm Queue including running tasks and their logs, job definitions, and agents

OpenAPI portal - `http://localhost:8222/docs`

:   Provides interactive documentation on the available endpoints for the services running at that location. It is also an easy way to verify which services are running at a particular host:port in a distributed services deployment.

## Check GPU

We will now create a job definition that will call the [nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html) command, which returns information about your NVIDIA gpu(s) and driver.

/resources/check-gpu.kit `check-gpu.kit</resources/check-gpu.kit>`

Notice the additional section at the bottom, where we have specified resource requirements. In particular, that this job type requires one NVIDIA gpu.

Now follow the same steps to upload the `check-gpu.kit` job definition.

``` shell
python job_definition_upload.py check-gpu.kit --farm-url http://localhost:8222 --api-key change-me
```

submit a `check-gpu` task.

Windows & Linux shell

``` shell
curl -X POST http://localhost:8222/queue/management/tasks/submit -H "accept: application/json" -H "Content-Type: application/json" -d "{\"user\": \"Username\",\"task_type\":\"check-gpu\",\"task_args\": {}, \"task_function\": \"\", \"task_function_args\": {}, \"task_requirements\": {}, \"task_comment\": \"check nvidia gpu\", \"status\": \"submitted\"}"
```

Windows Powershell

``` shell
$body = @{
   user               = "Username"
   task_type          = "check-gpu"
   task_args          = @{}
   task_function      = ""
   task_function_args = @{}
   task_requirements  = @{}
   task_comment       = "check nvidia gpu"
   status             = "submitted"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8222/queue/management/tasks/submit" `
   -Method Post `
   -Headers @{ "accept"="application/json"; "Content-Type"="application/json" } `
   -Body $body
```

## Summary

This guide has equipped you to:

- Perform a basic service check to ensure your services are operational.

- Add a simple Hello World job Definition for testing basic task execution.

- Query the job definitions available.

- Submit a `hello-world` task from the commandline to verify that your Farm instance is able to execute it.

- Query the status of a task.

- Introspect the log(s) of a task.

- Add a `check-gpu` job definition to call `nvidia-smi` to ensure that you can run GPU workloads.

By leveraging the above, you will have been able to verify that your Farm instance is working properly as well as gaining an understanding of job definitions and how to submit and query them.

## Further Reading

- `creating_job_definitions`

- `job_stores`

## Deleting a Job Definition

You can also use the `/remove` endpoint of the jobs service to delete a job definition from its JobStore. This should be used with caution as any submitted tasks that depend on the job definition will no longer execute.

``` shell
curl -X POST http://localhost:8222/queue/management/jobs/remove -H "accept: application/json" -H "X-API-KEY: change-me" -H "Content-Type: application/json" -d "{\"job_definition_name\": \"hello-world\"}"
```

and the result:

``` json
{"job-name":"hello-world","success":true}
```
