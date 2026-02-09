# Deploying on Google GCP

It is possible to deploy Farm on Google Cloud using [GKE](https://cloud.google.com/kubernetes-engine).

GKE will give you a managed Kubernetes cluster reducing the overhead of maintaining the cluster itself.

It is recommended to read through this guide as well as the deployment guide linked below before starting the deployment to make sure all pre-requisites are fulfilled.

## Prerequisites

### GKE Configuration

If you are familiar with Google Cloud, but not GKE, then we recommend starting with the [user guide](https://cloud.google.com/kubernetes-engine/docs) to get a high level overview and then working through the [GKE tutorial](https://cloud.google.com/kubernetes-engine/docs/quickstarts/create-cluster) to gain familiarity with the topic.

In order to deploy Farm on EKS an adequately sized cluster must be setup and configured for use. It is expected that a user has a Google Cloud account with appropriate quotas for the desired instance type(s) in a specified region.

Typically, at least two types of node configurations are needed depending on the type of workload:

- One or more node(s) and/or node group(s) configured for `Farm services`.

- One or more node(s) and/or node group(s) configured for `Farm workers`. This typically includes:

  - Non-GPU workloads.

  - GPU workloads (T4/A10/A40/A100 GPU required) running on supported [accelerated computing instance types](https://cloud.google.com/compute/docs/gpus) using a supported x86 platform.

Additional considerations:

- Managing Load Balancers/Ingresses via the [GKE Ingress](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress).

- Managing cluster auto-scaling (e.g.: with a [Cluster Autoscaler](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler))

This document aims to be unopinionated and will not describe how to setup and manage any of the additional resources.

It will assume that the various services can be reached from outside the cluster and that the application has been securely configured.

### GKE Version

Farm has been tested on Kubernetes versions 1.22 and higher. We'd recommend using, where possible, GKE 1.24 or higher. [Release notes](https://cloud.google.com/kubernetes-engine/docs/release-notes)

## Considerations

### Security

It is strongly recommended to not expose Farm to the public internet yet. Farm does not ship with authN/authZ and has limited authentication for job submission via tokens. If this is a technical requirement for your organization, be sure to restrict access to public endpoints (e.g.: security groups, Firewalls, etc.) Consult with your organization's security team to best determine how to properly secure Google Cloud, GKE, and Farm (see [Security in GKE](https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview) for more details).

### Capacity Tuning

Tuning the Farm controller's maximum job capacity can be achieved through configuring `farm-values.yaml`. This will limit the number of jobs that can run in parallel and may be useful for people running in mixed environments where they share Kubernetes with other workloads.

``` yaml
apps:
   controller:
      serviceConfig:
         capacity:
            max_capacity: 32
```

Cluster auto-scaling is highly coupled with the configuration of worker node(s) and/or node group(s) within the cluster and goes outside the scope of this document.

Please refer to the [Official GKE Autoscaling documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler) for more details.

### Number of GPUs

Farm will parallelize work based on the number of available GPUs. Once work has been assigned to a GPU, it will occupy the GPU until it completes.

In a production environment, it will take some experimentation to determine the optimal number of GPUs for the work being performed.

### Storage

Hard drive size selection must take into consideration both the containers being used and the types of jobs being executed.

Tasks execute inside a container and must have sufficient temporary storage for the task. Generally, a volume of around 100GB is a good starting point, but this is highly coupled with the requirements and workflow of your project.

If writing data to Google Cloud Storage, data may first temporarily be written to the running instance. As such, the instance must have sufficient storage for any temporary files (this can be fairly large for rendering related jobs). This will depend on the workload and their respective data management implementation.

A cluster's exact needs will be determined by the jobs the cluster is meant to execute.

It is good practice to begin with oversized resources and then eventually pair back or grow into the resources as necessary rather than have an undersized cluster that may alarm or become unavailable due to resource starvation.

### Management Services

Multiple services handle communication, life cycle, and interaction across the Farm cluster. These instances are considered memory intensive and should be treated as such. These services include the agents, controller, dashboard, jobs, logs, metrics, retries, settings, tasks, and UI services.

### Ingress

Farm does not deploy an Ingress. In order to be able to reach the services from outside a Kubernetes cluster an Ingress may be required. On GKE a load balancer and ingress are [available](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress)

## Deployment

With the GKE cluster configured, the deployment steps are identical to the general Kubernetes deployment documentation. Please follow this guide to continue with the installation of Farm.
