## Getting Started

This guide helps you set up and run the Farm service locally.

**In this guide:**
- [Clone the Repository](#clone-the-repository)
- [Install Dependencies](#install-dependencies)
- [Docker Daemon Config](#docker-daemon-config)
- [Required Devspace Plugin](#required-devspace-plugin)
- [Cluster Creation](#cluster-creation)
- [Deploy Farm](#deploy-farm)
- [Next steps](#next-steps)

### Clone the Repository

First, clone the Farm repository:

```bash
git clone ssh://.../farm.git
cd nv.svc.farm
```

> **Note:** All `devspace`, `curl`, and `docker` commands in the following guides assume you are executing them from the root of the project (`nv.svc.farm/`). Additionally, some links to Swagger docs and dashboard endpoints will only work after Farm is successfully deployed.

### Install Dependencies

- kind (Kubernetes-in-Docker)
- Docker
- NVIDIA Container Toolkit (nvidia-container-runtime)
- kubectl
- DevSpace

Installation guides:

- kind: [Install kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- Docker Engine: [Install Docker](https://docs.docker.com/engine/install/) • [Post-install (Linux)](https://docs.docker.com/engine/install/linux-postinstall/)
- NVIDIA Container Toolkit: [Install NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- kubectl: [Install tools (kubectl)](https://kubernetes.io/docs/tasks/tools/)
- DevSpace: [Install DevSpace](https://www.devspace.sh/docs/getting-started/installation)

After installing, verify:

```bash
docker --version
```
```bash
# If you just installed NVIDIA Container Toolkit, restart Docker first:
sudo systemctl restart docker
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```
```bash
kubectl version --client --output=yaml
```
```bash
kind version
```
```bash
devspace version
```


### Docker Daemon Config

Ensure your Docker daemon config contains something similar to the following. This will be inherited by kind, avoiding a custom CoreDNS configuration.

Edit `/etc/docker/daemon.json`:
```json
{
    "default-runtime": "nvidia",
    "dns": [
        "10.18.66.182",
        "10.120.237.52",
        "10.120.237.36"
    ],
    "features": {
        "cdi": true
    },
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```
Restart Docker:
```bash
sudo systemctl restart docker
```

You will need to login to the container registries. Devspace will use your local config to store a registry pull secret.

### Required Devspace Plugin

This project requires the nv-core devspace plugin for cluster management. Install it using:

```bash
devspace add plugin ssh://.../devspace-plugin-nv-core.git
```

To update the plugin to the latest version, run:

```bash
devspace update plugin nv-core
```

For more information about the plugin and its capabilities, see the [nv-core plugin documentation](https://.../devspace-plugin-nv-core/-/blob/master/README.md?ref_type=heads).

### Cluster Creation

To create a local development cluster, use:

```bash
devspace nv-core kind create
```

When prompted for cluster configuration, select one of these options:
- `basic-no-gpu - 1 worker nodes`: For local development without GPU requirements
- `basic-byo-gpu - 1 worker nodes`: For local development with GPU support

> **Note:** For this guide, select: `basic-no-gpu - 1 worker nodes` (we won't run GPU tasks).

After creating the cluster, set the namespace for all subsequent commands:

```bash
devspace use namespace farm
```

### Deploy Farm

deploy the cluster
```bash
devspace deploy -p nginx -p local
```

After waiting for the cluster to come up our Farm should be ready.

```bash
❯ kubectl get pods -n farm
NAME                              READY   STATUS      RESTARTS   AGE
farm-agents-77c68dc674-9b72h      1/1     Running     0          4m6s
farm-controller-ff764b95f-6lcls   1/1     Running     0          4m5s
farm-dag-758b7ffcb6-5fz2z         1/1     Running     0          4m6s
farm-dashboard-c6ffdf94f-vv5td    1/1     Running     0          4m5s
farm-jobs-7dffd5b465-6ftgv        1/1     Running     0          4m6s
farm-logs-8bd88475-7ltm8          1/1     Running     0          4m6s
farm-mysql-0                      1/1     Running     0          4m5s
farm-redis-master-0               1/1     Running     0          4m5s
farm-results-54fc87878b-6rr7g     1/1     Running     0          4m6s
farm-retries-7888d95db9-qr4kk     1/1     Running     0          4m6s
farm-settings-6bf95b599-p2twx     1/1     Running     0          4m5s
farm-tasks-64945f75d4-zqnpf       1/1     Running     0          4m6s
job-definitions-loader-wxsvb      0/1     Completed   0          4m5s
```

redeploy cluster with upstream changes
```bash
git pull
devspace deploy --force-build -p nginx -p local
```

### Next steps

Now that Farm is deployed and running, continue to [Create a Job Container](create-a-job-container.md) to learn about:

- **Building job containers**: Create a Docker container with a CLI tool for text processing
- **Testing locally**: Run the container directly with Docker to verify functionality
- **Understanding job structure**: See how containers interact with Farm's storage and APIs
