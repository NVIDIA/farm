# Deploying on Kubernetes

The following document describes configuring and deploying Farm with on Kubernetes. These instructions are generic and should apply to standard Kubernetes clusters as well as the various cloud flavours of Kubernetes. The intended audience for this document is experienced systems administrators familiar with Kubernetes, CSP Kubernetes offerings (if applicable), and the deployment of [Helm](https://helm.sh/) charts.

## Prerequisites

### NVIDIA Device Plugin

The Kubernetes cluster must have the [NVIDIA Device Plugin](https://github.com/NVIDIA/k8s-device-plugin#deployment-via-helm) installed. This plugin provides a daemonset that automatically exposes the number of GPUs available, keeps track of GPU health, and runs GPU enabled containers.

The NVIDIA Device Plugin runs as a daemonset on all nodes by default in the cluster. A `nodeSelector` can be used to isolate the daemonset to only run on GPU nodes.

On Helm install:

``` shell
--set nodeSelector=<LABEL>=VALUE
```

Or via a values file:

``` yaml
# nvidia-device-plugin-values.yaml
nodeSelector:
   <LABEL>: <VALUE>
```

Once the NVIDIA Device Plugin has been installed. You can verify the number of GPUs on the nodes via the following command:

``` shell
kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia.com/gpu"
```

### Kubernetes Version

Farm has been tested on Kubernetes versions 1.22 and higher. We'd recommend using, where possible, Kubernetes 1.24 or higher.

## Considerations

### Security

It is strongly recommended to not expose Farm to the public internet. Farm does not ship with authN/authZ and has limited authentication for job submission via tokens. If this is a technical requirement for your organization, be sure to restrict access to public endpoints (e.g.: security groups in cloud deployments, Firewalls and VPN access for on premise).

### Capacity Tuning

Tuning the Farm controller's maximum job capacity can be achieved through configuring `farm-values.yaml`. This will limit the number of jobs that can run in parallel and may be useful for people running in mixed environments where they share Kubernetes with other workloads.

``` yaml
apps:
   controller:
      serviceConfig:
         capacity:
            max_capacity: 32
```

### Number of GPUs

Farm will parallelize work based on the number of available GPUs. Once work has been assigned to a GPU, it will occupy the GPU until it completes.

In a production environment, it will take some experimentation to determine the optimal number of GPUs for the work being performed.

### Storage

Hard drive size selection must take into consideration both the containers being used and the types of jobs being executed.

Tasks execute inside a container and must have sufficient temporary storage for the task. Generally, a volume of around 100GB is a good starting point, but this is highly coupled with the requirements and workflow of your project.

Depending on the workload, data may be stored temporarily locally before. As such, the instance must have sufficient storage for any temporary files (this can be fairly large for rendering related jobs for example).

A cluster's exact needs will be determined by the jobs the cluster is meant to execute.

It is good practice to begin with oversized resources and then eventually pair back or grow into the resources as necessary rather than have an undersized cluster that may alarm or become unavailable due to resource starvation.

### Management Services

Multiple services manage communication, lifecycle processes, and interactions within the cluster. These services are resource-intensive, particularly in terms of memory, and should be allocated accordingly. Key components include `agents`, `controller`, `dashboard`, `jobs`, `logs`, `metrics`, `retries`, `settings`, `tasks`.

### Ingress

To access services from outside the Kubernetes cluster, you'll need to configure an Ingress Controller. The Kubernetes ecosystem offers several proven options, with [NGINX Ingress](https://docs.nginx.com/nginx-ingress-controller/) and [Traefik Ingress](https://doc.traefik.io/traefik/providers/kubernetes-ingress/) being fully validated for use with Farm. While the Farm Helm Chart includes NGINX Ingress Controller configurations and Helm Chart, it does not deploy the controller itself by default - allowing you to choose and configure the ingress solution that best fits your needs.

Enabling the deployment of NGINX Ingress Controller as well as configuring the ingress can be done by setting the following values in your `farm-values.yaml` file for example:

``` yaml
global:
   ingress:
      enabled: true # Generates Ingress resources
      ingressClassName: nginx
nginx:
   enabled: true # Deploys NGINX Ingress Controller
   controller:
      service:
         type: NodePort
         nodePorts:
            http: 32080
```

In this example the NGINX Ingress Controller is deployed as a NodePort service. This allows you to access the controller from outside the Kubernetes cluster by navigating to `http://<node-ip>:<node-port>`.

## Deploying the Helm Chart

### Prerequisites

#### Local

- A valid [NVIDIA NGC API key](https://docs.nvidia.com/base-command-platform/user-guide/#generating-api-key).

- [Installing](https://docs.nvidia.com/base-command-platform/user-guide/#installing-ngc-cli) the NGC CLI and [configuring](https://docs.nvidia.com/base-command-platform/user-guide/#configuring-ngc-cli-for-use) it.

- [Helm](https://helm.sh/) [Installation guide](https://helm.sh/docs/helm/helm_install/).

#### Cluster

- A recent NVIDIA driver version that's certified for the Omniverse applications that you'll be using for Farm tasks (it should be preinstalled with current accelerated AMIs listed above).

- NVIDIA k8s-device-plugin (see section 1.B).

- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#installation-guide) (should be preinstalled with current accelerated AMIs listed above).

- It is assumed that a method of targeting specific nodes is utilized (e.g. [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node)).

### Deploying Farm

In this step, we will deploy the Farm Helm chart. This document will provide a step-by-step guide and should be generic across Kubernetes flavours. For more advanced cases, feel free to examine the [Helm chart](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/helm-charts/nv-svc-farm) itself and determine the best approach for your provider.

A full set of all resources (containers, Helm charts, job definitions) can be found [in this collection](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/collections/farm_kubernetes)

All steps utilize the following values, however you should feel free to change them at your discretion. For this guide, we will assume:

``` shell
NAMESPACE=ov-farm
SECRET_NAME=registry-secret
NGC_API_TOKEN=<your_token>
```

1.  Create a namespace for Farm.

    ``` shell
    kubectl create namespace $NAMESPACE
     
    ```

    As the container images referenced within the Helm chart are private, you will need to [create a secret](https://kubernetes.io/docs/concepts/configuration/secret/#docker-config-secrets) within your cluster namespace to provide your cluster with the NGC API token.

    ``` shell
    kubectl create secret docker-registry $SECRET_NAME \
        --namespace $NAMESPACE \
        --docker-server="..." \
        --docker-username='...' \
        --docker-password=...
     
    ```

2.  Create a `farm-values.yaml` file. This file will be used for specifying overrides during the installation.

    *Replace the highlighted lines with your secret.*

    ``` yaml
    global:
        imagePullSecrets:
           - "SECRET_NAME" # Replace with $SECRET_NAME
     apps:
        controller:
           serviceConfig:
              k8s:
                 jobTemplateSpecOverrides:
                    imagePullSecrets:
                       - name: "SECRET_NAME" # Replace with $SECRET_NAME
     
    ```

    It may be required to add additional overrides in the `farm-values.yaml` file.

    For example, to tell the dashboard service to use a `LoadBalancer` service type and to target `t3.medium` instance types, if these are available in your cluster, you may need to add something like the following:

    ``` yaml
    apps:
        dashboard:
           nodeSelector:
              node.kubernetes.io/instance-type: t3.medium

           service:
              type: LoadBalancer
     
    ```

3.  Install the Farm Helm chart:

    ``` shell
    FARM_HELM_VERSION="2.0.42"

     helm fetch \
        https://helm.ngc.nvidia.com/nvidia/omniverse/charts/nv-svc-farm-$FARM_HELM_VERSION.tgz \
        --username='$oauthtoken' \
        --password=$NGC_API_TOKEN

     helm upgrade \
        --install \
        --create-namespace \
        --namespace $NAMESPACE \
        farm \
        nv-svc-farm-$FARM_HELM_VERSION.tgz \
        --values farm-values.yaml
     
    ```

4.  Validate the installation: Ensure that all pods are in the ready state before proceeding.

    The following command creates a `curl` pod in the namespace that will allow us to query the various service endpoints.

    (For more details on this, refer to the [Official Kubernetes service networking documentation](https://kubernetes.io/docs/concepts/services-networking/connect-applications-service/#accessing-the-service)):

    ``` shell
    kubectl run curl --namespace=$NAMESPACE --image=radial/busyboxplus:curl -i --tty -- sh
     
    ```

    The following code block defines two functions that facilitate querying if the various services are up:

    ``` shell
    check_endpoint() {
        url=$1
        curl -s -o /dev/null "$url" && echo -e "[UP]\t${url}" || echo -e "[DOWN]\t${url}"
     }

     check_farm_status() {
        echo "======================================================================"
        echo "Farm status:"
        echo "----------------------------------------------------------------------"
        check_endpoint "http://farm-agents/queue/management/agents/status"
        check_endpoint "http://farm-dashboard/queue/management/dashboard/status"
        check_endpoint "http://farm-jobs/queue/management/jobs/status"
        check_endpoint "http://farm-jobs/queue/management/jobs/load"
        check_endpoint "http://farm-logs/queue/management/logs/status"
        check_endpoint "http://farm-retries/queue/management/retries/status"
        check_endpoint "http://farm-tasks/queue/management/tasks/status"
        check_endpoint "http://farm-tasks/queue/management/tasks/list?status=submitted"
        echo "======================================================================"
     }
     
    ```

    Once you have the functions available in your `curl` pod, you can query the status of Farm by running:

    ``` shell
    check_farm_status
     
    ```

    Output should be similar to:

    ``` shell
    ======================================================================
     Farm status:
     ----------------------------------------------------------------------
     [UP]     http://farm-agents.ov-farm/queue/management/agents/status
     [UP]     http://farm-dashboard.ov-farm/queue/management/dashboard/status
     [UP]     http://farm-jobs.ov-farm/queue/management/jobs/status
     [UP]     http://farm-jobs.ov-farm/queue/management/jobs/load
     [UP]     http://farm-logs.ov-farm/queue/management/logs/status
     [UP]     http://farm-retries.ov-farm/queue/management/retries/status
     [UP]     http://farm-tasks.ov-farm/queue/management/tasks/status
     [UP]     http://farm-tasks.ov-farm/queue/management/tasks/list?status=submitted
     ======================================================================
     
    ```

    This validates that all Farm services are running and accessible.

5.  Now that you have confirmed that Farm services are available, it is time to run a simple job. This job definition runs the `df` command using the `busybox` container image.

    Use the following command from the [NGC CPU Resource setup documents](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/resources/cpu_verification/setup) to download the example `df.kit` job and sample upload script:

    ``` shell
    ngc registry resource download-version "nvidia/omniverse/cpu_verification:1.0.0"
     
    ```

    Next, retrieve a token from Farm for use in uploading jobs:

    ``` shell
    kubectl get secret farm-jobs -o yaml -n $NAMESPACE | grep api_key | cut -d':' -f2- | tr -d ' ' | base64 -d
     
    ```

    The token is unique per Farm instance and must be kept secure.

    Two libraries are required dependencies of the Python script, install them with:

    ``` shell
    pip install requests
     pip install toml
     
    ```

    Finally, from the directory the files were downloading into, execute the following script to upload the job definition to your cluster:

    ``` shell
    python ./job_definition_upload df.kit --farm-url=<URL to the instance of Farm> --api-key=<API Key as retrieved in previous step>
     
    ```

    The job definition may take up to about 1 minute to propagate to the various services in the cluster.

6.  After a few moments, it should be safe to submit a job to Farm for scheduling. Execute the following snippet (found in the [NGC CPU Resource Quick Start Guide](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/resources/cpu_verification/quick-start-guide)) to submit a job. If you are not using an ingress, port-forward the tasks service i.e. `kubectl port-forward -n $NAMESPACE service/farm-tasks 8012:80`. The `FARM_URL` becomes `localhost:8012`:

    ``` shell
    export FARM_URL=<REPLACE WITH URL OF OMNIVERSE FARM INSTANCE>
     curl -X "POST" \
     "${FARM_URL}/queue/management/tasks/submit" \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     -d '{
     "user": "testuser",
     "task_type": "df",
     "task_args": {},
     "metadata": {
        "_retry": {
           "is_retryable": false
        }
     },
     "status": "submitted"
     }
     
    ```

    After submitting, you should be able to navigate to `${FARM_URL}/queue/management/dashboard`, enter a username (this can be anything you want as no authentication is present) and observe your task in the task list.

7.  Now that you have confirmed that Farm services are available and that you can run a simple job, it is time to run a GPU workload. This job definition runs the `gpu` command using the `nvidia-cuda` container image.

    Use the following command from the [NGC GPU Resource setup documents](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/resources/gpu_verification/setup) to download the example `gpu.kit` job and sample upload script:

    ``` shell
    ngc registry resource download-version "nvidia/omniverse/gpu_verification:1.0.0"
     
    ```

    Next, retrieve a token from Farm for use in uploading jobs:

    ``` shell
    kubectl get secret farm-jobs -o yaml -n $NAMESPACE | grep api_key | cut -d':' -f2- | tr -d ' ' | base64 -d
     
    ```

    This token is unique per Farm instance and must be kept secure.

    Two libraries are required dependencies of the python script, install them with:

    ``` shell
    pip install requests
     pip install toml
     
    ```

    Finally, from the directory the files were downloading into, execute the following script to upload the job definition to your cluster. If you are not using an ingress, port-forward the job service i.e. `kubectl port-forward -n $NAMESPACE service/farm-jobs 8011:80`. The `--farm-url` becomes `localhost:8011`:

    ``` shell
    python ./job_definition_upload.py gpu.kit --farm-url=<url to the instance of omniverse farm> --api-key=<api key as retrieved in previous step>
     
    ```

    The job definition may take up to about 1 minute to propagate to the various services in the cluster.

8.  After a few moments, it should be safe to submit a job to Farm for scheduling. Execute the following snippet (found in the [NGC GPU resource quick start guide](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/resources/gpu_verification/quick-start-guide)) to submit a job. If you are not using an ingress, port-forward the tasks service i.e. `kubectl port-forward -n $NAMESPACE service/farm-tasks 8012:80`. The `FARM_URL` becomes `localhost:8012`:

    ``` shell
    export FARM_URL=<REPLACE WITH URL OF OMNIVERSE FARM INSTANCE>
     curl -X "POST" \
     "${FARM_URL}/queue/management/tasks/submit" \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     -d '{
     "user": "testuser",
     "task_type": "gpu",
     "task_args": {},
     "metadata": {
        "_retry": {
           "is_retryable": false
        }
     },
     "status": "submitted"
     }
     
    ```

    After submitting, you should be able to navigate to `${FARM_URL}/queue/management/dashboard`, enter a username (this can be anything you want as no authentication is present) and observe your task in the task list. In order for the Dashboard to work correctly a ingress must be used:

At this point your cluster should have a working version of Farm able to run basic jobs. It is worth having a closer look at the job definitions to see how workloads are structured and how you may be able to onboard your own workloads. Farm on Kubernetes can run any containerized workload. We would recommend reading the Farm documentation on **creating job definitions**.

In the next section we will target onboarding a rendering workflow.

## Batch Rendering Workloads

Farm can be used as a powerful distributed rendering solution.

### Configuring Storage

Before we dive into the workload itself there are some considerations regarding data access:

#### Nucleus

Farm jobs can be configured to connect directly to a Nucleus instance. This assumes that the Nucleus instance is directly accessible.

1.  Create a Nucleus account that can be used as a service account.

2.  Update the job definitions that need access to Nucleus by adding in the `OMNI_USER` and `OMNI_PASS` environment variables. For example the `create-render` job definition would look like the following if the user and password from step 1 were `foo` and `bar`:

    ``` toml
    [job.create-render]
     job_type = "kit-service"
     name = "create-render"
     command = "/startup.sh"
     # There is inconsistency with how args are parsed within Kit.
     # This is why --enable arguments have a space in them as they do not support `--enable=`
     # They will however be split into individual args when submitting them
     args = [
        "--enable omni.services.render",
        "--/app/file/ignoreUnsavedOnExit=true",
        "--/app/extensions/excluded/0=omni.kit.window.privacy",
        "--/app/hangDetector/enabled=0",
        "--/app/asyncRendering=false",
        "--/rtx/materialDb/syncLoads=true",
        "--/omni.kit.plugin/syncUsdLoads=true",
        "--/rtx/hydra/materialSyncLoads=true",
        "--/rtx-transient/resourcemanager/texturestreaming/async=false",
        "--/rtx-transient/resourcemanager/enableTextureStreaming=false",
        "--/exts/omni.kit.window.viewport/blockingGetViewportDrawable=true",
        "--ext-folder", "/opt/nvidia/omniverse/farm-jobs/farm-job-create-render/exts-job.omni.farm.render",
        "--/crashreporter/dumpDir=/tmp/renders",
        # Example code to set up pushing metrics to a Prometheus push gateway.
        #"--/exts/services.monitoring.metrics/push_metrics=true",
        #"--/exts/services.monitoring.metrics/job_name=create_render",
        #"--/exts/services.monitoring.metrics/push_gateway=http://localhost:9091"
     ]
     task_function = "render.run"
     headless = true
     log_to_stdout = true
     container = ".../.../create-render:2022.2.1"

     [job.create-render.env]
     OMNI_USER = "..."
     OMNI_PASS = "..."
     
    ```

3.  Upload the job definition to the Farm as explained previously and submit the jobs.

It should now be possible to read the files from Nucleus and upload back any results.

#### Kubernetes Persistent Volumes

Farm jobs can be configured to write to [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) which provide a variety of storage solutions that can be exposed to jobs. We will not cover how to configure the backend storage or the PVs themselves as these will vary per deployment. All CSPs do have options available to configure a variety of PV solutions.

1.  After configuring a PV it can be mounted by configuring the `capacity_requirements` (see: [resource limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#resource-units-in-kubernetes)) section in a job definition. For example, to mount a volume `output-storage` into a pod at the location of `/data/output` the job definition can be updated as below:

    ``` toml
    [capacity_requirements]

     [[capacity_requirements.resource_limits]]
     cpu = 2
     memory = "14Gi"
     "nvidia.com/gpu" = 1

     [[capacity_requirements.volume_mounts]]
     mountPath = "/data/output"
     name = "output-storage"

     [[capacity_requirements.volumes]]
     name = "output-storage"
     [capacity_requirements.volumes.persistentVolumeClaim]
     claimName = "aws-credentials"
     
    ```

2.  Upload the job definition to the Farm as previously explained and then submit the jobs.

It should now be possible to read and write (depending on the permissions on the Persisted Volume) data from `/data/output`.

### Onboarding `create-render` Job Definition

1.  With storage now configured, the `create-render` job can be onboarded.

    Use the following command from the [NGC create-render resource setup documents](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/omniverse/resources/create_render/setup) to download the example `job.omni.farm.render.kit` job and sample upload script:

    ``` shell
    ngc registry resource download-version "nvidia/omniverse/create_render:2022.2.1"
     
    ```

2.  Based on the selected storage solution, add the required job definition updates to the `farm.job.create.render.kit` file.

3.  Next, retrieve a token from Farm for use in uploading jobs:

    ``` shell
    kubectl get secret farm-jobs -o yaml -n $NAMESPACE | grep api_key | cut -d':' -f2- | tr -d ' ' | base64 -d
     
    ```

    The token is unique per Farm instance and must be kept secure.

    Two libraries are required dependencies of the Python script, install them with:

    ``` shell
    pip install requests
     pip install toml
     
    ```

    Finally, from the directory the files were downloading into, execute the following script to upload the job definition to your cluster:

    ``` shell
    python ./job_definition_upload job.omni.farm.render.kit --farm-url=<URL to the instance of Farm> --api-key=<API Key as retrieved in previous step>
     
    ```

    The job definition may take up to about 1 minute to propagate to the various services in the cluster.

With the job definition on-boarded, it is possible to submit a render job following the `/guides/render_with_moviecapture` guide.
