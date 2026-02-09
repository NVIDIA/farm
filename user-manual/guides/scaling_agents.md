# Scaling Agents

The agents service is responsible for monitoring all potential Farm Agents that have registered themselves via the controller service. Typically, it operates as part of the Farm Queue, though in larger deployments it can function either standalone or with redundancy.

By default, the agents service relies on an in-memory data store, which can constrain scalability and performance. To overcome these limitations, the in-memory agents store can be replaced with a Redis-backed instance.

This guide explains how to configure the agents service to use Redis as its backend.

## Background

The agents service uses classes derived from the `BaseAgentManager` to manage the connected Farm Agents. The default configuration uses the `DictAgentManager` to instantiate an in-memory dictionary store. For deployments with large numbers of Farm Agents, the agents service can be configured to use the `RedisAgentManager`.

### Run Redis via Docker

This guide uses Redis running in a container using Docker. This is a very easy method as the container has everything required to run the database and is a great way to test in a development environment.

Running Redis on Windows Using `WSL (Windows Subsystem for Linux)`

Using Windows `WSL (Windows Subsystem for Linux)`, you can run a Linux environment on your Windows system, including installing Docker and running Linux containers. Otherwise, you can [install Redis for Windows for development](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/).

Steps to run Redis on a Windows system using WSL and Docker:

- [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)

- Choose Ubuntu 24.04 as your Linux distribution

- [Install Docker](https://docs.docker.com/engine/install/ubuntu/)

- Determine the IP address of your WSL instance

Follow the steps below to pull the latest version of MariaDB and run it.

Ensure that you have a running instance of Redis.

``` shell
docker run --name farm-redis -p 6379:6379 -d redis:latest
```

## Configure Farm

If the agents service is running as part of a Farm Queue (e.g., `farm` or `farm-api` invocation), this should be added to the Farm Queue's configuration file. Otherwise, you can create a more focused configuration for running `agents-svc`.

1.  Configure the agent service.

The agents service instantiates an `AgentManager` based upon the class path defined in its `manager_class` setting. The corresponding `manager_args` is used to store any manager specific configuration settings.

For the `RedisAgentManager`, it uses a `connection_string` to establish the Redis connection. This must use a [compatible format](https://aioredis.readthedocs.io/en/v2.0.1/api/high-level/#aioredis.client.Redis.from_url) such as `redis://\<host\>:\<port\>` to specify a Redis instance that is network accessible by the agent service.

Add these configuration settings to the appropriate TOML configuration file:

``` toml
[settings.nv.svc.farm.agents]
# configure the agents service to use the `RedisAgentManager`
# by specifying its full class path
manager_class = "nv.svc.farm.services.agents.facilities.managers.redis.RedisAgentManager"

# Set the connection_string to the Redis instance
# using a compatible format "redis://<host>:<port>>"
manager_args.connection_string= "redis://10.2.1.40:6379"
```

Start `farm`, `farm-api`, or `agents-svc` using the configuration overrides, based on your Farm deployment.

``` shell
# Use if running the agents service as part of Farm Queue + Farm Agent
farm -c queue_config.toml

# Use if running the agents service as part of Farm Queue only
farm-api -c queue_config.toml

# Use if running the agents service independently
agents-svc -c agentsvc_config.toml
```

When using Redis as the backend, you can choose to run a single instance of the agents service as part of `farm` or `farm-api` or run it independently with `agents-svc`.

It also allows you to run additional instances all utilizing the same Redis backend, including in horizontally scalable and resilient deployments. The Farm Agent's controller service can be configured to point to specific instances of the agents service or distributed behind a load-balancer, allowing you to scale as needed.
