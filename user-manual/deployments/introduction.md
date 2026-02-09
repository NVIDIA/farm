# Installation and Deployment

Farm consists of multiple component services in a traditional Queue and Agents architecture, which can be deployed in a variety of ways.

Farm Queue

:   Acts as the central scheduler, receiving and organizing tasks submitted by users. It maintains a list of tasks and assigns them to available agents for execution.

Farm Agent

:   Responsible for executing tasks assigned by the Farm Queue. Agents can operate on various infrastructures, including workstations, servers, or cloud platforms, providing flexibility and scalability.

The Farm Queue and Agent services are the same regardless of deployment method. The methods vary by their complexity of installation, scalability, reliability, and the environment in which they run.

## Deployment Types

The Farm deployment options are summarized below. Once you have decided on the method that best suits your use case, in-depth installation and deployment guides are available from the menu on the left.

Once deployed there are a variety of options available to further tune the individual services.

**Standalone**

Farm Standalone runs on physical or Virtual Machines (VM) using either Windows or Linux. Its component service architecture supports flexible configurations: running the Farm Queue and Agent services together, separately (Queue-only or Agent-only), or as individual component services. These configurations are controlled via startup configuration files.

This installation method does not require GPU resources, other than for Agents running GPU tasks.

Farm Standalone is a pure Python implementation and uses standard Python installation processes. Installing Farm requires basic command-line proficiency in either Linux or Windows environments.

**Kubernetes**

For larger-scale deployments, Farm can be deployed on Kubernetes clusters. Farm uses the Kubernetes scheduler to manage task distribution, with all Farm services deployed behind a load balancer for high availability and fail-over support.

This architecture offers maximum scalability and is well-suited for production environments.

**Cloud**

Farm's Kubernetes deployment supports Azure, AWS, GCP, and OCI. While Farm lacks native access control features for cloud environments, you can secure endpoints by utilizing tools like security groups or API Gateways. It is recommended to enforce stricter permissions for accessing management endpoints.

**Alternatives**

Due to its microservices-based architecture, it is possible to mix deployment methods for the service components; for example, deploying the management services (Queue) in Kubernetes while using a standalone agent approach to distribute work across nodes.

Everything is API-driven, and as long as the services can talk to each other, various deployment scenarios are possible.
