# Deploying a Standalone Farm

This guide walks through installing Farm as a standalone solution on Windows or Linux. It is suitable for use cases ranging from a single system running both Queue and Agent, to a small distributed farm, with one Queue and multiple Agents. This is a straightforward choice for deployments with limited scaling needs.

In larger installations, services can be configured to run individually with scalable back-end solutions.

For enterprise-scale deployments, we recommend Kubernetes, which offers a robust and highly scalable alternative.

## Prerequisites

- Windows 10 or later

- Ubuntu 22.04 LTS or later

- [Python](https://python.org/) 3.10 or later

## Windows and Linux Installers

The Windows and Linux versions of Farm 2.0 Standalone are available as an NGC Resource:

- [Farm Standalone](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/resources/farm_standalone).

It contains OS specific compressed files of the `nv.svc.farm` Python module as a [Python wheel package (.whl)](https://peps.python.org/pep-0427/), along with operating system-specific dependencies and executables.

The `create-render` job definition, used for launching Kit-based rendering, is also included in `job.omni.farm.render.kit`

Download the Farm 2.0 Standalone resource, uncompress the appropriate OS-specific file, and follow the installation instructions, below.

## Installation

1.  Start a command shell.

2.  cd into the unzipped folder containing the Farm 2.0.x standalone package.

    **Windows**

    ``` shell
    cd c:\Users\Username\Downloads
      cd nv-svc-farm@2.0.42-offline-wheels-windows_x86_64

      dir
      
    ```

    You should see the Farm 2.0.x whl file and a dependencies folder:

    ``` shell
    Volume in drive C is Windows

      Directory of C:\Users\Username\Downloads\nv-svc-farm@2.0.42-offline-wheels-windows_x86_64

      01/01/2025  09:00 AM    <DIR>          .
      01/01/2025  09:00 AM    <DIR>          ..
      01/01/2025  09:00 AM    <DIR>          dependencies
      01/01/2025  09:00 AM    3,182,894      nv_svc_farm-2.0.42-py3-none-any.whl
      
    ```

    **Linux**

    ``` shell
    cd /home/user/Downloads
      tar -xvf nv-svc-farm@2.0.42-offline-wheels-linux_x86_64.tar.gz
      cd farm-install

      ls -l
      
    ```

    You should see the Farm 2.0.x whl file and a dependencies folder:

    ``` shell
    drwxr-xr-x 2 user user    4096 Jan  1 09:00 dependencies
      -rw-r--r-- 1 user user 3182300 Jan  1 09:00 nv_svc_farm-2.0.42-py3-none-any.whl
      
    ```

    The `nv_svc_farm-2.0.42-py3-none-any.whl` Python package contains all of the Farm 2.0 services in a single module, while `dependencies` contains Python modules required by Farm 2.0 Standalone.

3.  Install the Farm 2.x standalone Python module and dependencies.

    ``` shell
    python3 -m pip install --find-links dependencies nv_svc_farm-2.0.42-py3-none-any.whl
     
    ```

This installs all of the Python modules required to run Farm 2.0 standalone on your system.

## Post Installation

The installation method outlined above installs the Farm 2.0 Standalone Python module into the `site-packages` directory for your Python version. This module contains all of the individual Farm 2.0 service components.

Executables for each of the service components are also installed:

Windows

:   Executables are installed into the `Scripts` directory located alongside the `site-packages` directory.

Linux

:   Shell scripts are installed into `$HOME/.local/bin`.

You can add this directory to your `PATH` environment, if it is not already.

The individual services can be deployed in arbitrary combinations with proper configuration.

For convenience, three executables are included, which bundle the appropriate services, to support the three most common use-cases:

`farm`

:   Runs Farm Queue and Farm Agent in a single thread, suitable for single-system deployments or very small farm instances.

`farm-api`

:   Runs Farm Queue as its own service to control a small farm instance, without Farm Agent.

`controller-svc`

:   Runs Farm Agent for worker-nodes.

These can be combined in the following scenarios:

Single system:

- Run `farm`

Farm Queue and Agent system with additional systems running Farm Agent:

- Management system runs `farm`.

- Worker systems run `controller-svc` configured to connect to the Farm Queue.

Farm Queue system with additional systems running Farm Agent:

- Management system runs `farm-api`.

- Worker systems run `controller-svc` configured to connect to the Farm Queue.

When required, the individual service components can be used to distribute and scale:

Distributed environments:

- Farm Queue and/or individual management services run on appropriately sized hardware (e.g., `agents-svc`, `jobs-svc` `tasks-svc`), optionally leveraging scalable backends.

- Worker systems run `controller-svc`.

Farm's component architecture depends on the services being able to communicate with each other. The default installation uses the localhost network interface, only suitable for single-system use. Multi-system deployments require configuring the services and ensuring the host system's network configuration will route and allow the network traffic (i.e., network firewalls).

### Performing a Basic Post-Installation Test

We will use `farm` to verify that the installation was successful, running in a single-system configuration using localhost.

1.  Open a new shell and run `farm` to start Farm Queue and Agent on your system:

    ``` shell
    farm
     
    ```

    The shell should soon be filled with log output from the running services:

    ``` json
    {"Timestamp": 1733523950528043900, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Agents service.", "Attributes": {"app.clock": 6.132918358, "timestamp": "2024-12-06T22:25:50.528043900Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "2c458727-c674-416a-aac8-2998a1158cd2", "app.version": "2.0.42"}}
     {"Timestamp": 1733523951000045500, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Dashboard service.", "Attributes": {"app.clock": 6.604920149, "timestamp": "2024-12-06T22:25:51.000045500Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "0b57b47f-5ae3-4ecf-aca0-9fe04147f146", "app.version": "2.0.42"}}
     {"Timestamp": 1733523951660300000, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Jobs service.", "Attributes": {"app.clock": 7.265174627, "timestamp": "2024-12-06T22:25:51.660300000Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "c692b84f-3a12-4461-9995-a6d64a4ecec5", "app.version": "2.0.42"}}
     {"Timestamp": 1733523952359613000, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Job definitions directory: 'C:\Users\Username\AppData\Local\nvidia\nv-svc-farm\job-definitions'", "Attributes": {"app.clock": 7.964487553, "timestamp": "2024-12-06T22:25:52.359613000Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "2e42f350-18be-4121-85f8-fc37f3b319d3", "app.version": "2.0.42"}}
     {"Timestamp": 1733523952570612900, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Logs service.", "Attributes": {"app.clock": 8.175487518, "timestamp": "2024-12-06T22:25:52.570612900Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "e6bb6b45-997d-4e4f-bddb-fe0742eef59a", "app.version": "2.0.42"}}
     {"Timestamp": 1733523953510712800, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Retries service.", "Attributes": {"app.clock": 9.115587473, "timestamp": "2024-12-06T22:25:53.510712800Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "43a3025c-6ed1-4da0-bf68-0a629195c4a2", "app.version": "2.0.42"}}
     {"Timestamp": 1733523953999341600, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Settings service.", "Attributes": {"app.clock": 9.604216099, "timestamp": "2024-12-06T22:25:53.999341600Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "1cfadd58-133d-4345-ab88-573cd8873445", "app.version": "2.0.42"}}
     {"Timestamp": 1733523954612988900, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Tasks service.", "Attributes": {"app.clock": 10.21786356, "timestamp": "2024-12-06T22:25:54.612988900Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "8b64d4b2-ee41-4707-bfc9-82fceb7ede85", "app.version": "2.0.42"}}
     {"Timestamp": 1733523955216623100, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "connection string: sqlite:///C:\\Users\\Username\\AppData\\Local\\nvidia\\nv-svc-farm/task-management.db", "Attributes": {"app.clock": 10.821497679, "timestamp": "2024-12-06T22:25:55.216623100Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "309d43b8-98db-4143-8f1e-d3d37b10e7c6", "app.version": "2.0.42"}}
     {"Timestamp": 1733523955748864900, "SeverityNumber": 9, "SeverityText": "INFO", "InstrumentationScope": "", "Body": "Configuring Controller service.", "Attributes": {"app.clock": 11.353739738, "timestamp": "2024-12-06T22:25:55.748864900Z"}, "Resource": {"app.namespace": "nv.svc", "app.name": "nv.svc.farm", "app.instance.id": "fd2da74c-6f7c-488c-9266-682958a58800", "app.version": "2.0.42"}}
     
    ```

**If `farm` is not recognized, it likely means the executables directory is not in your `PATH`; either add it or specify the exact location of `farm`**

1.  Confirm that the installation completed successfully by querying the API endpoint that provides the service health status and manually verifying that the response is `"OK"`:

In a new shell:

``` shell
curl http://localhost:8222/status
"OK"
```

1.  You may now try accessing the Farm 2.0 Queue Dashboard and interactive endpoint documentation using the following URLs in your web-browser:

    [Farm Queue Dashboard](http://localhost:8222/queue/management/dashboard)

    :   `http://localhost:8222/queue/management/dashboard`

    [Farm 2.0 endpoint documentation](http://localhost:8222/docs)

    :   `http://localhost:8222/docs`

## Testing Your Farm Instance

To verify that your Farm instance is working, follow the steps outlined in the `/guides/testing_farm` guide and then return here.

## Farm Configuration

Each Farm service can be configured via a TOML settings file, allowing you to define how each service operates and communicates. This provides precise control over deployment and ensures the flexibility needed for diverse environments.

The default configuration binds the services to localhost, restricting access to the local system. This setup is secure and suitable for scenarios where Farm tasks are submitted and executed on a single system. For most workflows, however, connecting from other systems and distributing workloads across multiple machines is required.

Begin by creating a configuration to bind the services to a different network port.

1.  Keep `farm` running in its own shell.

2.  Open a new shell and query the available IP addresses on your system.

    Windows

    ``` shell
    ipconfig | find "IPv4"
      
    ```

    You should see a list of addresses **(example only)**:

    ``` shell
    IPv4 Address. . . . . . . . . . . : 10.2.1.40
      IPv4 Address. . . . . . . . . . . : 172.17.0.1
      IPv4 Address. . . . . . . . . . . : 192.168.1.50
      IPv4 Address. . . . . . . . . . . : 192.168.2.60
      
    ```

    Linux

    ``` shell
    hostname -I
      
    ```

    You should see a list of addresses **(example only)**;

    ``` shell
    10.2.1.40 172.17.0.1 192.168.1.50 192.168.2.60
      
    ```

    These are the available network IP addresses on your system.

3.  We will use cURL to demonstrate that the Farm services will only work with the localhost address. Replace the address 192.168.1.50 with one listed in the previous step, but keeping the port of 8222.

    ``` shell
    curl http://localhost:8222/status
     "OK"

     curl http://192.168.1.50:8222/status
     curl: (7) Failed to connect to 192.168.1.50 port 8222 after 2033 ms: Could not connect to server
     
    ```

4.  We will now create a configuration file to specify that the Farm services should use a different address.

    Create a text file named `farm_config.toml` with the following content, but using one of **your** IP addresses from the previous step.

    ``` toml
    [settings.nv.svc.server.http]
     # The host ip address that the services should bind to.
     host = "192.168.1.50"
     
    ```

5.  In the shell running `farm`, use ctrl+c to stop it and then re-run passing in the `farm_config.toml` file you just created.

    ``` shell
    farm -c farm_config.toml
     
    ```

6.  After a few moments, re-run the cURL commands.

    ``` shell
    curl http://localhost:8222/status
     curl: (7) Failed to connect to localhost port 8222 after 2033 ms: Could not connect to server

     curl http://192.168.1.50:8222/status
     "OK"
     
    ```

    The services are now bound to the 192.168.1.50 address and no longer respond to localhost. This enables any system that can access the 192.168.1.50 address to communicate with the Farm services running on this system.

7.  In addition to the host IP address, you can also configure the host port to which the services should bind.

    Update your `farm_config.toml` to include the port setting and restart `farm`.

    ``` toml
    [settings.nv.svc.server.http]
     # The host IP address and port that the services should bind to.
     host = "192.168.1.50"
     port = "8111"
     
    ```

    The Farm services are now bound to the 8111 port.

    ``` shell
    curl http://192.168.1.50:8111/status
     "OK"
     
    ```

By creating configuration files to set parameters of the various Farm services, you can adapt and tune them to match your deployment requirements.

Any deployment that requires interaction from another system requires the use of an externally accessible IP address, whether adding additional worker nodes or submitting tasks to the Farm Queue from another system.

### Configuring Separate Farm Queue and Agents

To run Farm Queue and Farm Agent separately, use the `farm-api` and `controller-svc` executables, providing each with its own configuration toml.

farm vs farm-api

The only difference between `farm` and `farm-api` is that `farm` runs all of the Farm services, while `farm-api` does not include the `controller-svc`. The `controller-svc` is the Farm Agent service that registers itself with the Farm Queue to indicate that a system can execute Farm tasks. It then monitors the Farm Queue and assigns itself any tasks that it has been configured to accept.

If you want the system that is running the Farm Queue to also act as a Farm Agent and run within the same process, then you can use `farm`. If you want to either run the Farm Agent as a separate process on the system, or only run Farm Agent on other systems, then use `farm-api`.

#### Configuring Farm Queue

The configuration we will use for `farm-api` is the same as what we used for `farm` in the previous step. You can choose to use localhost or any external ip address.

1.  Create a configuration for `farm-api` named `farm_queue.toml`.

    ``` toml
    [settings.nv.svc.server.http]
     # The host ip address that the services should bind to.
     host = "192.168.1.50"
     
    ```

2.  In a new shell, start `farm-api` specifying the `farm_queue.toml` configuration file.

    ``` shell
    farm-api -c farm_queue.toml
     
    ```

    The terminal should fill with output from the `farm-api` services.

#### Configuring Farm Agents

Ensure the Farm 2.0 Standalone services are installed on the Farm Agent worker-node if running on a separate system than Farm Queue.

1.  Now create a configuration for `controller-svc` named `farm_agent.toml`.

    This configuration will be more involved as we need to tell the Farm Agent `controller-svc` how it can connect to the Farm Queue services started by `farm-api`. If using localhost for `farm-api`, you must also use it for `controller-svc`.

    If you want to bind the `controller-svc` to the same network address as `farm-api`, you must specify a different port. If running on different systems, or different network addresses, you can use the default port 8222.

    ``` toml
    [settings.nv.svc.server.http]
     # The host ip address and port that the services should bind to.
     host = "192.168.2.60"
     port = "8111"

     [settings.nv.svc.farm.controller]
     # The service endpoints of the Farm Queue that the Farm Agent controller must connect to
     job_store_args.jobs_load_endpoint = 'http://192.168.1.50:8222/queue/management/jobs/load
     job_manager_args.log_upload_endpoint = 'http://192.168.1.50:8222/queue/management/logs/upload
     tasks_service_url = 'http://192.168.1.50:8222/queue/management/tasks
     agents_service_url = 'http://192.168.1.50:8222/queue/management/agents
     
    ```

    The `[settings.nv.svc.farm.controller]` section is where URLs for the Farm Queue endpoints are configured. These have been set using the IP address and port **(if changed)** specified in the `farm_queue.toml` used when starting `farm-api`.

2.  In a new shell, start `controller-svc` specifying the `farm_agent.toml` configuration file.

    ``` shell
    controller-svc -c farm_agent.toml
     
    ```

    The terminal should fill with output from the `controller-svc` service. It will take a moment for the Farm Agent controller service to start and then connect to the Farm Queue services.

    You can use the /connected endpoint of the `controller-svc` to check if it has connected to the Farm Queue.

    In a new terminal:

    ``` shell
    curl http://192.168.2.1:8111/connected
     {"agent_id":"PW024S5J-60932","is_connected":false,"active_tasks":[]}

     curl http://192.168.2.1:8111/connected
     {"agent_id":"PW024S5J-60932","is_connected":true,"active_tasks":[]}
     
    ```

3.  Repeat this process for each Farm Agent worker-node you want available as part of your Farm instance.

## Summary

You can configure Farm 2.0 to operate based on your specific needs, whether running on the same system, or multiple ones, as long as the Farm 2.0 Standalone services have been installed and configured so the services know how to connect to each other.

The only requirements are:

- Farm 2.0 Standalone has been installed on all systems running as a Farm Queue and/or Farm Agent.

- The Farm Agent controller service is configured to be able to find the Farm Queue services.

- There is a viable network route for the Farm Agent controller service to communicate with the Farm Queue services.

- The Farm Agent controller service can only be configured to connect to one Farm Queue.

It is not necessary for systems that will submit jobs to a Farm Queue instance to have any Farm services installed, they can directly submit jobs via the Queue's submission API endpoint over the network.

## Next Steps

You should now have basic familiarity with how to configure and run Farm Standalone services to meet your specific requirements. With its component service architecture, Farm allows you to deploy its services balancing convenience with scalability. In addition, some of the services can be configured to leverage alternative backends in situations requiring greater resiliency and performance.

- Decide how and where you want to run the services:

  - Farm Queue:

    - For small deployments use either `farm` or `farm-api`.

    - For larger deployment consider running individual services at scale using the Kubernetes and cloud installation guides.

  - Farm Agent:

    - Run `controller-svc` on all of your Farm worker-nodes.

- Ensure each of the services are configured properly and the Farm Agent worker nodes can connect to the Farm Queue.

- Install and configure job definitions for the job types you want to support on your Farm instance.

- For Kit rendering using Movie Capture, ensure that the create-render job definition is installed and properly configured.

Use the resources listed below, as well as our other guides, to further explore how to best leverage Farm.

## Additional Items

### Restricting Access

Farm assumes a secure environment with minimal restrictions, requiring an `api_key` for some endpoints. In untrusted settings, we suggest using an API Gateway and an identity service to safeguard management endpoints; however, configuring these security measures is beyond the scope of this guide.

Minimally, we advise you to change the default `api_key` used by the jobs service to validate certain requests.

You can specify your own API key by adding the snippet below to your jobs service's configuration, typically included as part of the Farm Queue.

``` toml
[settings.nv.svc.farm.jobs]
api_key = "change-me"
```

This is discussed in the `/guides/job_stores` guide.

### Rendering Using Kit Applications

If you want to use the *Movie Capture* Kit extension to submit Kit-based renders to your Farm instance, you must ensure that a properly configured create-render job definition is available.

This is discussed in the `/guides/rendering_with_kat` guide.
