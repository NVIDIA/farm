# Deploying on AWS

It is possible to deploy Farm on AWS using [EKS](https://aws.amazon.com/eks/) EKS will give you a managed Kubernetes cluster reducing the overhead of maintaining the cluster itself.

This guide won't be going into how to deploy an EKS cluster but will cover the pre-requisites for running OV Farm on an EKS cluster.

It is recommended to read through this guide as well as the deployment guide linked below before starting the deployment to make sure all pre-requisites are fulfilled.

## Prerequisites

### AWS Configuration

If you are familiar with AWS, but not EKS, then we recommend starting with the [user guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html) to get a high level overview and then working through the [Amazon EKS workshop](https://www.eksworkshop.com) to gain familiarity with the topic.

General AWS EKS documentation can be found [here](https://docs.aws.amazon.com/eks/index.html) and provides details on getting started, best practices, API surface, and using the AWS EKS cli.

Note: if using a pre-existing EKS cluster before `1.24` and updating, then it is recommended to familiarize yourself with [Dockershim deprecation](https://docs.aws.amazon.com/eks/latest/userguide/dockershim-deprecation.html). If starting from `1.24`, no intervention is required.

In order to deploy Farm on AWS an adequately sized cluster must be setup and configured for use. It is expected that a user has an AWS account with appropriate EC2 service quotas for the desired instance type(s) in a specified region. These EC2 instances are expected to be part of a VPC with configured security groups and subnets and an EKS cluster must be running on a supported version of K8S.

Typically, at least two types of node configurations are needed depending on the type of workload:

- One or more node(s) and/or node group(s) configured for `Farm services`.

- One or more node(s) and/or node group(s) configured for `Farm workers`. This typically includes:

  - Non-GPU workloads.

  - GPU workloads (T4/A10/A100 GPU required) running on supported accelerated computing instance types (P4, G5, G4dn families) using a supported x86 accelerated [EKS optimized Amazon Linux AMI](https://docs.aws.amazon.com/eks/latest/userguide/eks-optimized-ami.html#gpu-ami).

Additional considerations:

- Managing Load Balancer(s)/Ingress(es) via the [ALB Controller](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html).

- Managing cluster auto-scaling (e.g.: with a [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler) or with [Karpenter](https://github.com/aws/karpenter), depending on your desired node configuration).

This document aims to be unopinionated and will not describe how to setup and manage any of the additional resources.

It will assume that the various services can be reached from outside the cluster (e.g.: Ingress []{#--}[AWS Application Load Balancer](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)) and that the application has been securely configured (e.g.: through configured [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html) and/or [Web Application Firewall ACLs](https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html)).

### EKS Version

Farm has been tested on Kubernetes versions 1.22 and higher. We'd recommend using, where possible, EKS 1.24 or higher.

## Considerations

### Security

It is strongly recommended to not expose Farm to the public internet yet. Farm does not ship with authN/authZ and has limited authentication for job submission via tokens. If this is a technical requirement for your organization, be sure to restrict access to public endpoints (e.g.: security groups, AWS WAF, etc.).

Consult with your organization's security team to best determine how to properly secure AWS, EKS, and Farm (see [Security in Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/security.html) for more details).

### Capacity Tuning

Tuning the Farm controller's maximum job capacity can be achieved through configuring `farm-values.yaml`. This will limit the number of jobs that can run in parallel and may be useful for people running in mixed environments where they share Kubernetes with other workloads.

``` yaml
apps:
   controller:
      serviceConfig:
         capacity:
            max_capacity: 32
```

Cluster auto-scaling is highly coupled with the configuration of worker node(s) and/or node group(s) within the cluster and goes outside the scope of this document. This is typically achieved with the [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler) and/or the open-source project [Karpenter](https://github.com/aws/karpenter).

Please refer to the [Official AWS Autoscaling documentation](https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html) for more details.

### Number of GPUs

Farm will parallelize work based on the number of available GPUs. Once work has been assigned to a GPU, it will occupy the GPU until it completes.

In a production environment, it will take some experimentation to determine the optimal number of GPUs for the work being performed.

### Storage

Hard drive size selection must take into consideration both the containers being used and the types of jobs being executed.

You must have sufficient temporary storage for the container to execute a task. Generally, an EBS Volume around 100GB is a good starting point, but this is highly coupled with the requirements and workflow of your project.

If writing data to S3, data may first temporarily be written to the running instance. As such, the instance must have sufficient storage for any temporary files (this can be fairly large for rendering related jobs). This will depend on the workload and their respective data management implementation.

A cluster's exact needs will be determined by the jobs the cluster is meant to execute.

It is good practice to begin with oversized resources and then eventually scale down or grow into the resources as necessary rather than have an undersized cluster that may alarm or become unavailable due to resource starvation.

### Management Services

Multiple services handle communication, life cycle, and interaction across the Farm cluster. These instances are considered memory intensive and should be treated as such. These services include the agents, controller, dashboard, jobs, logs, metrics, retries, settings, tasks, and UI services.

### Ingress

Farm does not deploy an Ingress. In order to be able to reach the services from outside a Kubernetes cluster an Ingress may be required. On AWS an application load balancer ingress is available: [documentation](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)

## Deployment

With the AKS cluster configured, the deployment steps are identical to the general Kubernetes deployment documentation. Please follow this guide to continue with the installation of Farm.
