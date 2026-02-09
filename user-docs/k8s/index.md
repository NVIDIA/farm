## Farm Documentation

1. [Getting Started](getting-started.md)
2. [Create a Job Container](create-a-job-container.md)
3. [Create a Job](create-a-job.md)
4. [Create a Taskflow](create-a-taskflow.md)
5. [Advanced Taskflow Features](advanced-taskflow-features.md)

## Swagger Documentation

Farm services expose REST APIs documented with Swagger/OpenAPI. After deploying Farm locally, access the API documentation at:

- **[Jobs service](http://jobs.127-0-0-1.nip.io:8080/docs)** - Manage job definitions
- **[Tasks service](http://tasks.127-0-0-1.nip.io:8080/docs)** - Submit and query tasks and taskflows
- **[Results service](http://results.127-0-0-1.nip.io:8080/docs)** - Store and retrieve task outputs
- **[Dashboard](http://farm.127-0-0-1.nip.io:8080/queue/management/dashboard)** - Monitor tasks, jobs, and workflows
- **[DAG service](http://dag.127-0-0-1.nip.io:8080/docs)** - Manage directed acyclic graph structures
- **[Agents service](http://agents.127-0-0-1.nip.io:8080/docs)** - Manage worker agents
- **[Logs service](http://logs.127-0-0-1.nip.io:8080/docs)** - Access task logs
- **[Retries service](http://retries.127-0-0-1.nip.io:8080/docs)** - Configure retry policies
- **[Settings service](http://settings.127-0-0-1.nip.io:8080/docs)** - Manage configuration settings
- **[Controller service](http://controller.127-0-0-1.nip.io:8080/docs)** - Core orchestration logic

