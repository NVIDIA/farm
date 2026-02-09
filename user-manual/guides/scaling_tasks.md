# Scaling Tasks

In a Farm instance, the tasks service handles the submission and management of all tasks. While effective in smaller deployments, its default configuration using a [SQLite](https://www.sqlite.org/) database can limit scalability and performance in high-load scenarios.

This guide explores how to configure the tasks service to work with more robust database options, ensuring scalability and reliability in demanding environments.

## Background

Farm uses Encode's [Databases](https://www.encode.io/databases/) Python module to manage the database connection; providing support for [SQLite](https://www.sqlite.org/), MySQL and [PostgresSQL](https://www.postgresql.org/) compatible databases.

This allows you to choose a database, running on the same host or remotely, suited for your specific performance, scalability, and resilience needs.

The database **must support** the `CREATE IF NOT EXISTS` syntax for `TABLE` and `INDEX`. While MySQL does not other MySQL compatible databases such as [MariaDB](https://mariadb.com/kb/en/installing-and-using-mariadb-via-docker/) do. NVIDIA has used SQLite and MariaDB instances with the tasks service.

## MariaDB Example

We will walk through the steps required to configure the tasks service to connect to a MariaDB database. Alternative databases are configured similarly, but the specifics for running them will vary.

### Prerequisites

- Docker or Docker Desktop for Windows

- MariaDB Container

- MySQL command-client client (Windows or Linux)

- MariaDB user account with `CREATE` privileges to create the required database and tables.

### Run MariaDB via Docker

This guide uses MariaDB running in a container using Docker. This is a very easy method as the container has everything required to run the database and is a great way to test in a development environment.

Running MariaDB on Windows using WSL (Windows Subsystem for Linux).

Using Windows WSL (Windows Subsystem for Linux), you can run a Linux environment on your Windows system, including installing Docker and running Linux containers. Otherwise, you can [install a local Windows instance of MariaDB](https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/installing-mariadb/binary-packages/installing-mariadb-msi-packages-on-windows).

Steps to run MariaDB on a Windows system using WSL and Docker:

1.  [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

2.  Choose Ubuntu 24.04 as your Linux distribution.

3.  [Install Docker](https://docs.docker.com/engine/install/ubuntu/).

4.  Install the mysql client.

5.  Determine the IP address of your WSL instance.

Follow the steps below to pull the latest version of MariaDB and run it:

1.  Start the MariaDB instance, locally or in a hosted environment:

    ``` shell
    docker run --name farm-mariadb -e MYSQL_ROOT_PASSWORD="CHANGE-ME" -e MYSQL_USER="farm" -e MYSQL_PASSWORD="change_me" -e MYSQL_DATABASE=FarmTasks -p 3306:3306 -d mariadb:latest
      
    ```

    **Specify your own values.**

    `/resources/mariadb_run.sh`

    This starts a MariaDB container, using command arguments and environment variables to configure the running instance.

    `--name`

    :   What to call the running MariaDB Docker container.

    `MYSQL_ROOT_PASSWORD`

    :   The password for the `root` user of the MariaDB instance.

    `MYSQL_USER`

    :   The MariaDB username that Farm will use to connect to the instance.

    `MySQL_PASSWORD`

    :   The password for the `MYSQL_USER`.

    `MYSQL_DATABASE`

    :   The name to use for the tasks database.

    `-p 3306:3306`

    :   Maps the standard MySQL port of 3306 from the host to the container.

    You will need these values in order to configure the tasks service to use the MariaDB instance and to access it via the `mysql` client.

2.  `CREATE` and `GRANT` the Farm user the proper permissions.

    The previous `docker` command should have created the user with the proper permissions. If not, you can use the following SQL while connected to the MariaDB instance using the `mysql` client.

    ``` sql
    CREATE USER 'farm'@'%' IDENTIFIED BY 'change_me';
     GRANT CREATE, SELECT, INSERT, UPDATE, DELETE ON FarmTasks.* TO 'farm'@'%';
     FLUSH PRIVILEGES;
     
    ```

## Configure Farm

To configure the tasks service to use the MariaDB instance, we need to specify the URL to use when connecting to the database.

If the tasks service is running as part of a Farm Queue (e.g., `farm`) or `farm-api` invocation), this should be added to the Farm Queue's configuration file. Otherwise, you can create a more focused configuration for running `tasks-svc`.

1.  Set the database URL.

    The tasks service uses the `connection_string` to establish the database connection. It must use the format `mysql://<username>:<password>@<host>:<port>/<db_name>` and be network accessible by the tasks service.

    Add this configuration setting to the appropriate TOML configuration file.

    ``` toml
    [settings.nv.svc.farm.tasks.dbs.task-persistence]
     # connection_string = "mysql://<username>:<password>@<host>:<port>/<db_name>"
     connection_string = "mysql://farm:change_me@192.168.1.50:3306/FarmTasks"
     
    ```

2.  Start the farm, farm-api, or tasks service using the configuration overrides, based on your Farm deployment.

    ``` shell
    # Farm Queue + Farm Agent
     farm -c queue_config.toml

     # Farm Queue only
     farm-api -c queue_config.toml

     # Tasks service running standalone
     tasks-svc -c tasks_config.toml
     
    ```
