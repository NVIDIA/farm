# Job Stores

This guide presumes you already have basic understanding of how to create configuration TOML files and how to specify them when launching Farm services. The sample TOML configurations below are only the snippets required to specify and configure a Job Store and are meant to be included as part of a service's overall configuration file.

Job Definitions are what define the types of workloads (job types) that a Farm instance is able to execute. They provide the meta-data used by Farm Agents to initiate a task on the local system. A Farm Agent can only accept tasks for job types it has a job definition for. Farm Agents can be configured to write job definitions in a locally accessible folder or from a remote service. In addition, the Farm Queue Job service can be configured to write job definitions locally or on a [Redis](https://github.com/redis/redis) server.

The locations where Job Definitions are stored are conveniently called Job Stores. There are several types of Job Stores provided with Farm allowing you to choose the best method for managing Job Definitions based upon the types of workloads and heterogeneity of your Farm Agents. The two most commonly used are the `DirectoryJobStore` and `RemoteJobStore`. In addition, there is a `RedisJobStore` where scalability and resilience are critical.

## Why Have Job Stores

In order for a Farm Agent to be able to accept a task, it must have the job definition that matches the task's job type in order to initiate its execution.

Job Definitions contain metadata such as the command to execute, the working directory it should execute in, environment variables, etc. If all Farm Agents have exactly the same system configuration and execution environment, it is possible that the same definition will suffice for all agents, which is certainly true in some cases. However, when running in mixed environments, or where there is a desire to allocate only certain Farm Agents to certain job types, having flexibility in how job definitions are stored is required.

While the ability to deploy unique job definitions to every Farm Agent provides the ultimate in customization, it quickly becomes tedious to impractical in large Farm instances. Enabling Farm Agents to access remote job stores via services lowers the cost of deployment and helps with consistency. Farm was designed to enable batch processing of arbitrary workloads from a single desktop system running Windows or Linux, to thousands of high-performance servers in data center compute clusters.

Job Stores allow you to balance:

- Customization

- Ease of maintenance

## Job Stores, Agents, and Queues

Job Stores are implemented as Python classes that provide simple methods for managing job definitions, namely:

- Return all the job definitions managed by the job store.

- Save a job definition, if the Job Store allows it.

- Delete a job definition, if the Job Store allows it.

The three types of Job Stores provided with Farm are:

`DirectoryJobStore`

:   Manages job definitions stored in a locally accessible directory.

`RemoteJobStore`

:   Access job definitions from a remote jobs service.

`RedisJobStore`

:   Uses a Redis server to manage job definitions.

Accessing job definitions occurs in two distinct areas within a Farm deployment:

- Farm Agent's `controller` service

- Farm Queue's `jobs` service

The `controller` service uses its configured job store to manage the job definitions that the Farm Agent can execute. It can be configured to access job definitions directly via the `DirectoryJobStore`, or request job definitions from a jobs service **(using `RemoteJobStore`)** or a Redis server **(using `RedisJobStore`)**.

The `jobs` service is used to support remote job store access via the `RemoteJobStore` and can be configured to manage job definitions via the `DirectoryJobStore` or the `RedisJobStore`. The jobs service supports its own endpoints allowing for remote administration of the job definitions, namely save and remote. These endpoints call into the corresponding methods of the job store it has been configured for.

Each Job Store implementation varies in how job definitions are managed. Only the `jobs` service exposes endpoints for doing so, namely jobs/save and jobs/remove, which call into the job store's `save_job` and `delete_job` methods.

DirectoryJobStore

:   Uses a configurable locally accessible directory to manage job definitions. Watchers are used to monitor the directory for job definition .kit files that are added or deleted.

    When used with the `controller` service, job definitions are manually copied into the directory or deleted from it.

    When used by the `jobs` service, job definitions can be manually added or deleted from the directory or its jobs/save and jobs/remove endpoints can be used to remotely do so.

RemoteJobStore

:   Communicates with a configurable `jobs` service to retrieve job definitions. Adding or deleting job definitions is accomplished by calling the associated `jobs` service endpoints, jobs/save and jobs/remove. This is only used by the `controller` service.

RedisJobStore

:   Uses a [Redis](https://github.com/redis/redis) server to store job definitions in large Farm deployments where performance, scalability, and resiliency are critical. This is intended for use by the jobs service, as the controller service does not provide an external mechanism to load, save, or remove job definitions.

Effectively this means that the controller service will use a DirectoryJobStore to locally manage job definitions, or more commonly, a RemoteJobStore to connect to a jobs service. The jobs service will typically use a DirectoryJobStore for standalone deployments and a RedisJobStore in large Kubernetes deployments.

## Job Store Configuration

You configure the job store for the controller and jobs services by specifying the Python class to use, as a str, and the appropriate settings in a configuration file. Each service has their own settings that must be configured properly.

DirectoryJobStore

:   

    param new_job_definition_save_location

    :   Local path to the directory to store new job definitions **(properly encode or use single-quotes)**.

    type new_job_definition_save_location

    :   str

    param job_directories

    :   Directories that should be scanned and watched for job definitions.

    type job_directories

    :   Tuple(\[str\],)

> The OS specific defaults are:
>
> Windows
>
> :   `%LOCALAPPDATA%/nvidia/nv-svc-farm/job-definitions`
>
> Linux
>
> :   `$HOME/.local/share/nv-svc-farm/job-definitions`

RemoteJobStore

:   

    param jobs_load_endpoint

    :   The full URL of the jobs service's load endpoint **(properly encode or use single-quotes)**.

    type jobs_load_endpoint

    :   str

    param fetch_interval

    :   The interval, in seconds, to sync with the jobs service.

    type fetch_interval

    :   int = 30

RedisJobStore

:   

    param connection_string

    :   A full connection URL to a Redis server **(properly encode or use single-quotes)**.

    type connection_string

    :   str

### Configuring the Controller Service

The controller service's job store is configured using the `job_store_class` and `job_store_args` settings.

Defaults to: RemoteJobStore

RemoteJobStore

``` toml
[settings.nv.svc.farm.controller]

# Configures a RemoteJobStore, which is the default

# This usually isn't required as it is already the default, but shown for completeness
job_store_class = "nv.svc.farm.services.jobs.facilities.store.directory.RemoteJobStore"

# You pass arguments to the Job Store, by setting its arguments
# in the job_store_args parameter, similar to a dict. You only need to
# specify what you want to change.

# This requires the full URL to the Farm Queue's 'jobs/load' endpoint.
job_store_args.jobs_load_endpoint = 'http://10.2.1.40:8222/queue/management/jobs/load

# This usually isn't required.
job_store_args.fetch_interval = 10
```

A more typical example snippet:

``` toml
[settings.nv.svc.farm.controller]

job_store_args.jobs_load_endpoint = 'http://10.2.1.40:8222/queue/management/jobs/load
```

DirectoryJobStore

``` toml
[settings.nv.svc.farm.controller]

# Set the controller to use a DirectoryJobStore
job_store_class = "nv.svc.farm.services.jobs.facilities.store.directory.DirectoryJobStore"

# Set the DirectoryJobStore arguments
# First clear the arguments so they don't inherit from the default RemoteJobStore
job_store_args = {dynaconf_merge=false}

# Set the directory where new job definitions will be saved
job_store_args.new_job_definition_save_location = 'c:\farm\job-definitions

# Specify additional directories to search and monitor for job definitions
job_store_args.job_directories = ['c:\tmp\job-definitions','d:\other\job-defs']
```

A simple example that uses the default locations:

``` toml
[settings.nv.svc.farm.controller]

# Set the controller to use a DirectoryJobStore
job_store_class = "nv.svc.farm.services.jobs.facilities.store.directory.DirectoryJobStore"

# Clear job_store_args to not inherit from the default RemoteJobStore
# and use the DirectoryJobStore defaults
job_store_args = {dynaconf_merge=false}
```

RedisJobStore

``` toml
[settings.nv.svc.farm.controller]

# Configures a RedisJobStore

# Set the controller to use a RedisJobStore
job_store_class = "nv.svc.farm.services.jobs.facilities.store.directory.RedisJobStore"

# You pass arguments to the Job Store, by setting its arguments
# in the job_store_args parameter, similar to a dict. You only need to
# specify what you want to change.

# This requires a fully valid connection URL for the Redis server.
job_store_args.connection_string = 'http://10.2.1.5:6379
```

### Configuring the Jobs Service

The jobs service's job store is configured using the `store_class` and `store_args` settings.

Defaults to: `DirectoryJobStore`

DirectoryJobStore

``` toml
[settings.nv.svc.farm.jobs]

# Set the jobs service to use a DirectoryJobStore
# This usually isn't required as it is already the default, but shown for completeness
store_class = "nv.svc.farm.services.jobs.facilities.store.directory.DirectoryJobStore"

# You pass arguments to the Job Store, by setting its arguments
# in the store_args parameter, similar to a dict. You only need to
# specify what you want to change.

# Set the directory where new job definitions will be saved
store_args.new_job_definition_save_location = 'c:\farm\job-definitions

# Specify additional directories to search and monitor for job definitions
store_args.job_directories = ['c:\tmp\job-definitions','d:\other\job-defs']
```

A simple example that changes the default location:

``` toml
[settings.nv.svc.farm.jobs]

# Set the directory where new job definitions will be saved
store_args.new_job_definition_save_location = 'c:\farm\job-definitions
```

RedisJobStore

``` toml
[settings.nv.svc.farm.jobs]

# Configures a RedisJobStore

# Set the job service to use a RedisJobStore
store_class = "nv.svc.farm.services.jobs.facilities.store.directory.RedisJobStore"

# You pass arguments to the Job Store, by setting its arguments
# in the store_args parameter, similar to a dict. You only need to
# specify what you want to change.

# This requires a fully valid connection URL for the Redis server.
store_args.connection_string = 'http://10.2.1.5:6379
```

#### Controlling Access

To restrict access to the jobs service's `jobs/save` and `jobs/remove` endpoints, a configurable API key must be specified as part of the request header in the `X-API-KEY` field.

You can specify your own API key, by adding the snippet below to your jobs services configuration.

``` toml
[settings.nv.svc.farm.jobs]
api_key = "change-me"
```

## Job Store Topologies

The default configuration for Farm involves all Farm Agents using the RemoteJobStore to pull job definitions from the Farm Queue's jobs service using a DirectoryJobStore. This works for most deployments and is the case even for single-system Standalone use cases. For large Farm clusters, this can be upgraded to using a RedisJobStore if the performance of the jobs service becomes a bottleneck or high-availability is required.

It is also possible to run additional independent jobs services, taking advantage of Farm's service component architecture. This allows you to spin up jobs services for specific job-types or workloads (e.g., Windows and Linux). A centralized jobs service can also be used by Farm Agent's running in different Farm instances, where centralized management of job definitions can be separated from hardware allocation and Farm tasks submission.
