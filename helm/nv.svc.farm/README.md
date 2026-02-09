# nv-svc-farm

![Version: 2.10.14](https://img.shields.io/badge/Version-2.10.14-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 2.10.14](https://img.shields.io/badge/AppVersion-2.10.14-informational?style=flat-square)
Farm application using nv.svc.core framework.

## Overview

This chart assumes that a Kubernetes cluster is already available and configured.

Depending on the ingress controller and namespace some changes may be required.

## Quick start

Before installing it's worth considering Image Pull Secrets and Ingress access.

NOTE: use `--dry-run` to inspect the resulting Kubernetes manifests generated from the helm chart.

```bash
helm upgrade \
    --install \
    nv-svc-farm \
    . \
    --create-namespace \
    --namespace <<NAMESPACE-NAME>> \
    --set global.imagePullSecrets[0].name=registry-secret \
    --set global.image.tag="2.0.0"

```

### Image Pull Secrets

Container images are hosted on **ghcr.io** (GitHub Container Registry).

Therefore, you will need to create an Image Pull Secret to be able to pull the containers within Kubernetes.

NOTE: If the `<<NAMESPACE-NAME>>` namespace does not exist, create it prior to creating the secret.

```bash

kubectl create namespace <<NAMESPACE-NAME>>

kubectl create secret docker-registry \
  registry-secret \
  --namespace <<NAMESPACE-NAME>> \
  --docker-server="ghcr.io" \
  --docker-username='<<YOUR-GITHUB-USERNAME>>' \
  --docker-password=<<YOUR-GITHUB-PAT>>
```

Then during install, specify the global image pull secret.

```bash
--set global.imagePullSecrets[0].name=registry-secret
```

### Ingress Access

This chart does not bundle an ingress controller. You must have an ingress controller already installed in your cluster (e.g., Traefik, NGINX Ingress, HAProxy, etc.).

By default, the chart does not specify an `ingressClassName`, which means it will use your cluster's default ingress class. You can explicitly set the ingress class with `--set global.ingress.ingressClassName="YOUR-INGRESS-CLASS"`.

It's worth getting familiar with the set of options available under the `global.ingress` setting.

#### Access via DNS

This example uses a simple local DNS setup with any ingress controller.

For production setups you'll likely need to configure TLS cert secrets for the hosts (this is beyond the scope of this guide).

To use a custom local DNS, we suggest using nip.io for example `127-0-0-1.nip.io`, which returns 127.0.0.1. For other custom DNS we'll need to update **/etc/hosts** and map it to the Node's Internal IP.

```bash
# Deploy Farm with ingress enabled (assumes ingress controller is already installed)
helm upgrade \
    --install \
    nv-svc-farm \
    . \
    --create-namespace \
    --namespace <<NAMESPACE-NAME>> \
    --set "global.imagePullSecrets[0]=registry-secret" \
    --set global.ingress.host="127-0-0-1.nip.io" \
    --set global.ingress.enabled=true
    # Optionally specify ingress class if not using cluster default:
    # --set global.ingress.ingressClassName="traefik"

kubectl get nodes -o=wide

NAME                          STATUS   ROLES                  AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE       KERNEL-VERSION      CONTAINER-RUNTIME
ov-local-control-plane   Ready    control-plane,master   3h22m   v1.23.4   172.25.0.2    <none>        Ubuntu 21.10   5.15.0-27-generic   containerd://1.5.10
```

Add an entry to your **/etc/hosts**:

```bash
sudo vi /etc/hosts

172.25.0.2      ov.local
```

Check the port your ingress controller is exposing (this varies by controller):

```bash
# Example: Check ingress controller service
kubectl get svc -A | grep ingress
```

A quick check confirms we can reach the service from outside the cluster:

```bash
curl http://ov.local:<INGRESS-PORT>/status
"OK"
```

#### Access via Node's IP

When the ingress host is **not** specified, the ingress controller will default to using the controller service's IP which is then routed via the Node's IP.

```bash
# Install your preferred ingress controller first, then deploy Farm
helm upgrade \
    --install \
    nv.svc.farm \
    . \
    --create-namespace \
    --namespace <<NAMESPACE-NAME>> \
    --set global.imagePullSecrets[0].name=registry-secret \
    --set global.ingress.host="" \
    --set global.ingress.enabled=true
    # Optionally specify ingress class:
    # --set global.ingress.ingressClassName="traefik"

kubectl -n <<NAMESPACE-NAME>> get ingress
NAME                   CLASS    HOSTS   ADDRESS         PORTS   AGE
nv-svc-farm-tasks      <none>   *       10.43.230.160   80      10m

kubectl get nodes -o wide
NAME                    STATUS   ROLES                  AGE   VERSION        INTERNAL-IP   EXTERNAL-IP   OS-IMAGE   KERNEL-VERSION      CONTAINER-RUNTIME
k3d-ov-local-server-0   Ready    control-plane,master   21h   v1.23.6+k3s1   172.18.0.3    <none>        K3s dev    5.15.0-43-generic   containerd://1.5.5
```

A quick check confirms we can reach the service from outside the cluster (port depends on your ingress controller configuration):

```bash
curl http://172.18.0.3:<INGRESS-PORT>/status
"OK"
```

### Understanding Values Configuration Construction

The values are merged internally and externally, -f file.yaml -> .Values.defaults -> .Values.global -> .Values.apps.[appname].
This allows for each service to inherit sane defaults from .Values.defaults and also allows global overrides that effect each .Values.apps[*] and finally application specific overrides .Values.apps.[appname].*

## Configuration

**NOTE: Jobs API Key**

The Jobs API Key is needed for creating job definitions within Farm via the Jobs service.

To retrieve the API key from the cluster, retrieve the Jobs secret and get the "api_key" and base64 decode it.

```bash
kubectl get secret -n <<NAMESPACE-NAME>> farm-jobs -o=jsonpath={.data.api_key} | base64 -d
```

To view values via helm use `helm show values`

**NOTE**: There are **global** values.

## Values

### Agents

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.agents.enabled | bool | `true` | Enable Agents Service |
| apps.agents.initImage.waitForServices | list | `["tasks",{"host":"{{ include \"redis.host\" . }}","name":"redis","port":"{{ .Values.external.redis.port }}"}]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| apps.agents.secret | object | `{"create":false}` | The Agents service has no current secret to create |
| apps.agents.serviceConfig | object | `{"manager_class_selector":{"default":{"class":"nv.svc.farm.services.agents.facilities.managers.memory.DictAgentManager"},"redis":{"class":"nv.svc.farm.services.agents.facilities.managers.redis.RedisAgentManager"}},"url_prefix":"/queue/management/agents"}` | Configuration for Application, not directly an Application setting, should not be a template |
| apps.agents.serviceConfig.manager_class_selector | object | `{"default":{"class":"nv.svc.farm.services.agents.facilities.managers.memory.DictAgentManager"},"redis":{"class":"nv.svc.farm.services.agents.facilities.managers.redis.RedisAgentManager"}}` | Map of Available Manager Classes, used in Settings template to determined which should be used automatically. See apps.agents.settings.nv.svc.farm.agents.[manager_args/manager_class] |
| apps.agents.serviceConfig.url_prefix | string | `"/queue/management/agents"` | URL Prefix for Controller API, used by template in apps.controller.settings.nv.svc.farm.agents.url_prefix |
| apps.agents.settings.nv.svc.farm.agents | object | `{"check_interval":120,"farm_tasks_address":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}","lost_timeout":300,"manager_args":{"connection_string":"{{- if .root.Values.external.redis.enabled }}{{ include \"redis.connection_string\" . }}{{- end }}"},"manager_class":"{{- if .root.Values.external.redis.enabled }}{{ .svc.serviceConfig.manager_class_selector.redis.class }}{{- else -}}{{ .svc.serviceConfig.manager_class_selector.default.class }}{{- end }}","url_prefix":"{{ .Values.apps.agents.serviceConfig.url_prefix }}"}` | Available Agents Settings. This section may include templates. |

### Controller

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.controller.configMapChecksumTemplate | string | `"nv-svc-farm.controller.checksums"` | Additional Checksums to add to Deployment, causes rollout on change. |
| apps.controller.enabled | bool | `true` | Enable Controller |
| apps.controller.extraVolumeMounts | list | `[{"mountPath":"/etc/nvidia/farm/agent","name":"capacity-config"},{"mountPath":"/etc/nvidia/farm/job-spec","name":"job-template-spec-override-config"},{"mountPath":"/etc/nvidia/farm/container-spec","name":"container-spec-override-config"}]` | Extra volume mounts to add to container/deployment, excluding configuration configmap (automatic) |
| apps.controller.extraVolumes | list | `[{"configMap":{"name":"{{ .Release.Name }}-capacity"},"name":"capacity-config"},{"configMap":{"name":"{{ .Release.Name }}-job-template-spec-overrides"},"name":"job-template-spec-override-config"},{"configMap":{"name":"{{ .Release.Name }}-container-spec-overrides"},"name":"container-spec-override-config"}]` | Extra volumes to be attached to Controller Deployment |
| apps.controller.initImage.waitForServices | list | `["agents","logs","jobs","tasks"]` | List of Applications this service should wait for before starting (dependencies). |
| apps.controller.role | object | `{"create":true,"rules":[{"apiGroups":["batch"],"resources":["jobs","jobs/status"],"verbs":["get","list","watch","create","update","patch","delete"]},{"apiGroups":[""],"resources":["pods","pods/log"],"verbs":["get","list","watch","create","update","patch","delete"]}]}` | Role that this Application service account should bind to |
| apps.controller.role.create | bool | `true` | Create role/rolebinding |
| apps.controller.role.rules | list | `[{"apiGroups":["batch"],"resources":["jobs","jobs/status"],"verbs":["get","list","watch","create","update","patch","delete"]},{"apiGroups":[""],"resources":["pods","pods/log"],"verbs":["get","list","watch","create","update","patch","delete"]}]` | Role Permissions |
| apps.controller.serviceConfig | object | `{"capacity":{"max_capacity":32},"k8s":{"containerSpecOverrides":{"securityContext":{"runAsUser":0}},"jobTemplateSpecOverrides":{"activeDeadlineSeconds":86400}},"services_base_url":"/queue/management","url_prefix":"/agent"}` | Configuration for Controller, not directly an Application setting, should not be a template |
| apps.controller.serviceConfig.capacity | object | `{"max_capacity":32}` | Capacity used to render /templates/controller/configmap-capacity.yaml |
| apps.controller.serviceConfig.capacity.max_capacity | int | `32` | Specify the max number of jobs the controller is allowed to run. |
| apps.controller.serviceConfig.k8s.containerSpecOverrides | object | `{"securityContext":{"runAsUser":0}}` | Specify Container spec overrides, these are fields under (spec.template.spec.containers) |
| apps.controller.serviceConfig.k8s.jobTemplateSpecOverrides | object | `{"activeDeadlineSeconds":86400}` | Specify Job template spec overrides, these are fields under (spec.template.spec) |
| apps.controller.serviceConfig.k8s.jobTemplateSpecOverrides.activeDeadlineSeconds | int | `86400` | Specify Active Deadline Seconds override, Job pods running longer than this setting are terminated (default 24 hrs). |
| apps.controller.serviceConfig.services_base_url | string | `"/queue/management"` | Base URL for applications |
| apps.controller.serviceConfig.url_prefix | string | `"/agent"` | URL Prefix for Controller API, used by template in apps.controller.settings.nv.svc.farm.controller.url_prefix |
| apps.controller.settings.nv.svc.farm.controller | object | `{"agent_checkin_interval":30,"bay_controller_args":{"capacity_file":"/etc/nvidia/farm/agent/capacity.json"},"bay_controller_class":"nv.svc.farm.services.controller.facilities.bays.FileBasedMultiSlotBay","job_manager_args":{},"job_manager_class":"nv.svc.farm.services.jobs.facilities.manager.k8s.KubernetesProcessManager","job_store_args":{"jobs_load_endpoint":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"jobs\" \"root\" .root) }}/load"},"job_store_class":"nv.svc.farm.services.jobs.facilities.store.remote.RemoteJobStore","public_to_private_source_queue_hostnames":{},"reconcile_task_state":false,"service_host_url_format_str":"{service_host}{{ .Values.apps.controller.serviceConfig.services_base_url }}","task_checkin_interval":10,"task_checkin_timeout":3600,"task_reconcile_interval":3600,"url_prefix":"{{ .Values.apps.controller.serviceConfig.url_prefix }}"}` | Available Controller Settings. This section may include templates. |
| apps.controller.settings.nv.svc.farm.jobs | object | `{"agent_controller_host":"{{ include \"nv-svc-farm.app.connection-host\" (dict \"svcName\" \"controller\" \"root\" .root) }}","agent_controller_port":"{{ include \"nv-svc-farm.app.port\" (dict \"svcName\" \"controller\" \"root\" .root) }}","agent_controller_protocol":"{{ .svc.service.targetPortName }}","k8s_manager":{"container_spec_overrides_file":"/etc/nvidia/farm/container-spec/container_spec_overrides.json","job_template_spec_overrides_file":"/etc/nvidia/farm/job-spec/job_template_spec_overrides.json","jobs_namespace":"{{ .Release.Namespace }}","log_upload_endpoint":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"logs\" \"root\" .root) }}/upload","ttl_seconds_after_finished":600}}` | Available Jobs Settings |

### DAG

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.dag.additionalInitContainerTemplates | list | `[]` | Additional Init Containers to add to deployment of DAG Application (dependencies) |
| apps.dag.enabled | bool | `true` | Enable DAG Service |
| apps.dag.extraEnvTemplates | list | `["nv-svc-farm.mysql.env-secret"]` | Extra Environment Variables to add to DAG Deployment |
| apps.dag.initImage.waitForServices | list | `[{"host":"{{ include \"nv-svc-farm.mysql.host\" (dict \"Values\" .Values \"Release\" .Release \"root\" .root ) }}","name":"mysql","port":"{{ .Values.external.mysql.port }}"}]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| apps.dag.secret | object | `{"create":true}` | Create DAG Secret - See /templates/dag/secret-dag-mysql.yaml |
| apps.dag.serviceConfig | object | `{"url_prefix":"/queue/management/dag"}` | Configuration for DAG, not directly an Application setting, should not be a template |
| apps.dag.serviceConfig.url_prefix | string | `"/queue/management/dag"` | URL Prefix for DAG API, used by template in apps.dag.settings.nv.svc.farm.dag.url_prefix |
| apps.dag.settings | object | `{"nv":{"svc":{"farm":{"dag":{"database":{"connection_string":"{{- if .root.Values.external.mysql.enabled }}{{ include \"nv-svc-farm.mysql.connection_string\" . }}{{- else -}}{{- print \"sqlite:////tmp/dag-management.db\" -}}{{- end }}"},"store_class":"nv.svc.farm.services.dag.facilities.dag_store.DagDatabaseBackend","task_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}","url_prefix":"{{ .Values.apps.dag.serviceConfig.url_prefix }}"}}}}}` | DAG Application Specific Settings/Overrides |
| apps.dag.settings.nv.svc.farm.dag | object | `{"database":{"connection_string":"{{- if .root.Values.external.mysql.enabled }}{{ include \"nv-svc-farm.mysql.connection_string\" . }}{{- else -}}{{- print \"sqlite:////tmp/dag-management.db\" -}}{{- end }}"},"store_class":"nv.svc.farm.services.dag.facilities.dag_store.DagDatabaseBackend","task_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}","url_prefix":"{{ .Values.apps.dag.serviceConfig.url_prefix }}"}` | Available DAG Settings. This section may include templates. |

### Dashboard

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.dashboard.enabled | bool | `true` | Enable Dashboard Service |
| apps.dashboard.initImage.waitForServices | list | `["tasks"]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| apps.dashboard.serviceConfig.url_prefix | string | `"/queue/management/dashboard"` | URL Prefix for Controller API, used by template in apps.dashboard.settings.nv.svc.farm.dashboard.url_prefix |
| apps.dashboard.settings.nv.svc.farm.dashboard | object | `{"build_dir":"","farm_tasks_address":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}","url_prefix":"{{ .Values.apps.dashboard.serviceConfig.url_prefix }}"}` | Available Dashboard Settings. This section may include templates. |

### Jobs

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.jobs.enabled | bool | `true` | Enable Jobs Service |
| apps.jobs.extraEnv | list | `[{"name":"JOBS_API_KEY","valueFrom":{"secretKeyRef":{"key":"api_key","name":"{{ include \"nv-svc-farm.app.fullname\" (dict \"svcName\" \"jobs\" \"Values\" .Values \"Release\" .Release \"root\" .root ) }}"}}}]` | Extra Environment variables to add to Application Container. May include templates. |
| apps.jobs.extraVolumeMountTemplates | list | `["jobs.volume.mounts"]` | Extra volume mount templates to add to Application container/deployment |
| apps.jobs.extraVolumeTemplates | list | `["jobs.volumes"]` | Extra volume templates to add to Deployment |
| apps.jobs.initImage.waitForServices | list | `[{"host":"{{ include \"redis.host\" $ }}","name":"redis","port":"{{ $.Values.external.redis.port }}"}]` | List of Applications this service should wait for before starting (dependencies). |
| apps.jobs.secret | object | `{"create":true,"name":"jobs"}` | Create Job Application Secret. See /templates/jobs/secret-api-key.yaml |
| apps.jobs.serviceConfig | object | `{"api_key":"","definitions":["df","nvidia-smi-check"],"load_default_job_definitions":false,"store_selector":{"default":{"class":"nv.svc.farm.services.jobs.facilities.store.directory.DirectoryJobStore"},"redis":{"class":"nv.svc.farm.services.jobs.facilities.store.redis.RedisJobStore"}},"url_prefix":"/queue/management/jobs"}` | Configuration for Application, not directly an Application setting, should not be a template |
| apps.jobs.serviceConfig.definitions | list | `["df","nvidia-smi-check"]` | List of Job definitions to load. See |
| apps.jobs.serviceConfig.load_default_job_definitions | bool | `false` | Deploy helm hook to load job definitions on startup. See /templates/jobs/job-definition-loader.yaml |
| apps.jobs.serviceConfig.store_selector | object | `{"default":{"class":"nv.svc.farm.services.jobs.facilities.store.directory.DirectoryJobStore"},"redis":{"class":"nv.svc.farm.services.jobs.facilities.store.redis.RedisJobStore"}}` | Map of Available Store Classes, used in Settings template to determined which should be used automatically. See apps.jobs.settings.nv.svc.farm.jobs.[store_args/store_class] |
| apps.jobs.settings.nv.svc.farm.jobs | object | `{"agent_controller_host":"{{ include \"nv-svc-farm.app.connection-host\" (dict \"svcName\" \"controller\" \"root\" .root) }}","agent_controller_port":"{{ include \"nv-svc-farm.app.port\" (dict \"svcName\" \"controller\" \"root\" .root) }}","agent_controller_protocol":"http","api_key":"@format {env[JOBS_API_KEY]}","farm_facilities_extensions":[],"store_args":{"connection_string":"{{- if .root.Values.external.redis.enabled }}{{ include \"redis.connection_string\" . }}{{- end }}"},"store_class":"{{- if .root.Values.external.redis.enabled }}{{ .svc.serviceConfig.store_selector.redis.class }}{{- else -}}{{ .svc.serviceConfig.store_selector.default.class }}{{- end }}","supported_instance_payload_versions":[],"url_prefix":"{{- .Values.apps.jobs.serviceConfig.url_prefix -}}"}` | Available Jobs Settings. This section may include templates. |

### Logs

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.logs.enabled | bool | `true` | Enable Logs Service |
| apps.logs.serviceConfig | object | `{"url_prefix":"/queue/management/logs"}` | Configuration for Application, not directly an Application setting, should not be a template |
| apps.logs.serviceConfig.url_prefix | string | `"/queue/management/logs"` | URL Prefix for Logs API, used by template in apps.logs.settings.nv.svc.farm.logs.url_prefix |
| apps.logs.settings.nv.svc.farm.logs | object | `{"store_args":{},"store_class":"nv.svc.farm.services.logs.facilities.memory.MemoryLogStore","url_prefix":"{{ .Values.apps.logs.serviceConfig.url_prefix }}"}` | Available Logs Settings. This section may include templates. |

### Results

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.results.enabled | bool | `true` | Enable Results Service |
| apps.results.initImage.waitForServices | list | `["tasks",{"host":"{{ include \"redis.host\" . }}","name":"redis","port":"{{ .Values.external.redis.port }}"}]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| apps.results.secret | object | `{"create":false}` | The Results service has no current secret to create |
| apps.results.serviceConfig | object | `{"manager_class_selector":{"default":{"class":"nv.svc.farm.services.results.facilities.managers.memory.DictResultManager"},"redis":{"class":"nv.svc.farm.services.results.facilities.managers.redis.RedisResultManager"}},"url_prefix":"/queue/management/results"}` | Configuration for Application, not directly an Application setting, should not be a template |
| apps.results.serviceConfig.manager_class_selector | object | `{"default":{"class":"nv.svc.farm.services.results.facilities.managers.memory.DictResultManager"},"redis":{"class":"nv.svc.farm.services.results.facilities.managers.redis.RedisResultManager"}}` | Map of Available Manager Classes, used in Settings template to determine which should be used automatically. See apps.results.settings.nv.svc.farm.results.[manager_args/manager_class] |
| apps.results.serviceConfig.url_prefix | string | `"/queue/management/results"` | URL Prefix for Results API |
| apps.results.settings.nv.svc.farm.results | object | `{"manager_args":{"connection_string":"{{- if .root.Values.external.redis.enabled }}{{ include \"redis.connection_string\" . }}{{- end }}","result_ttl":432000},"manager_class":"{{- if .root.Values.external.redis.enabled }}{{ .svc.serviceConfig.manager_class_selector.redis.class }}{{- else -}}{{ .svc.serviceConfig.manager_class_selector.default.class }}{{- end }}","result_ttl":432000,"task_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}","url_prefix":"{{ .Values.apps.results.serviceConfig.url_prefix }}"}` | Available Results Settings. This section may include templates. |

### Retries

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.retries.enabled | bool | `true` | Enable Retries Service |
| apps.retries.initImage.waitForServices | list | `["tasks"]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| apps.retries.serviceConfig | object | `{"url_prefix":"/queue/management/retries"}` | Configuration for Application, not directly an Application setting, should not be a template |
| apps.retries.serviceConfig.url_prefix | string | `"/queue/management/retries"` | URL Prefix for Retries API, used by template in apps.retries.settings.nv.svc.farm.retries.url_prefix |
| apps.retries.settings.nv.svc.farm.retries | object | `{"farm_tasks_address":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}","url_prefix":"{{ .Values.apps.retries.serviceConfig.url_prefix }}"}` | Available Retries Settings. This section may include templates. |

### Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.settings.enabled | bool | `true` | Enable Settings Service |
| apps.settings.serviceConfig | object | `{"url_prefix":"/queue"}` | Configuration for Application, not directly an Application setting, should not be a template |
| apps.settings.serviceConfig.url_prefix | string | `"/queue"` | URL Prefix for Controller API, used by template in apps.settings.settings.nv.svc.farm.settings.url_prefix |
| apps.settings.settings.nv.svc.farm.settings | object | `{"exposed_settings":{"advanced_rendering_features":{}},"url_prefix":"{{ .Values.apps.settings.serviceConfig.url_prefix }}"}` | Available Settings Service Settings. This section may include templates. |

### Tasks

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.tasks.additionalInitContainerTemplates | list | `["nv-svc-farm.mysql.init"]` | Additional Init Containers to add to deployment of Tasks Application (dependencies) |
| apps.tasks.configMapChecksumTemplate | string | `"nv-svc-farm.tasks.checksums"` | Additional Checksums to add to Deployment, causes rollout on change. |
| apps.tasks.enabled | bool | `true` | Enable Tasks Service |
| apps.tasks.extraEnvTemplates | list | `["nv-svc-farm.mysql.env-secret"]` | Extra Environment Varialbes to add to Agents Deployment |
| apps.tasks.extraVolumes | list | `[{"configMap":{"defaultMode":504,"name":"{{ .Release.Name }}-migrations"},"name":"migrations"}]` | Extra volumes to be attached to Agents Deployment |
| apps.tasks.initImage.waitForServices | list | `[{"host":"{{ include \"nv-svc-farm.mysql.host\" (dict \"Values\" .Values \"Release\" .Release \"root\" .root ) }}","name":"mysql","port":"{{ .Values.external.mysql.port }}"}]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| apps.tasks.secret | object | `{"create":true}` | Create Tasks Secret - See /templates/tasks/secret-tasks-mysql.yaml |
| apps.tasks.serviceConfig | object | `{"skip_db_migrations":false,"url_prefix":"/queue/management/tasks"}` | Configuration for Tasks, not directly an Application setting, should not be a template |
| apps.tasks.serviceConfig.skip_db_migrations | bool | `false` | Skip DB migration on upgrade/deployment |
| apps.tasks.serviceConfig.url_prefix | string | `"/queue/management/tasks"` | URL Prefix for Tasks API, used by template in apps.tasks.settings.nv.svc.farm.controller.url_prefix |
| apps.tasks.settings | object | `{"nv":{"svc":{"farm":{"tasks":{"dag_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"dag\" \"root\" .root) }}","dbs":{"task-persistence":{"connection_string":"{{- if .root.Values.external.mysql.enabled }}{{ include \"nv-svc-farm.mysql.connection_string\" . }}{{- else -}}{{- print \"sqlite:////tmp/task-management.db\" -}}{{- end }}"}},"event_handler_args":{"DAGTaskEventHandler":{"dag_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"dag\" \"root\" .root) }}"},"TaskStatusEventHandler":{"retries_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"retries\" \"root\" .root) }}"}},"event_handlers":["nv.svc.farm.services.tasks.facilities.task_events.status.TaskStatusEventHandler","nv.svc.farm.services.dag.facilities.task_events.DAGTaskEventHandler"],"metrics_collect_interval":60,"url_prefix":"{{ .Values.apps.tasks.serviceConfig.url_prefix }}"}}}}}` | Tasks Application Specific Settings/Overrides |
| apps.tasks.settings.nv.svc.farm.tasks | object | `{"dag_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"dag\" \"root\" .root) }}","dbs":{"task-persistence":{"connection_string":"{{- if .root.Values.external.mysql.enabled }}{{ include \"nv-svc-farm.mysql.connection_string\" . }}{{- else -}}{{- print \"sqlite:////tmp/task-management.db\" -}}{{- end }}"}},"event_handler_args":{"DAGTaskEventHandler":{"dag_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"dag\" \"root\" .root) }}"},"TaskStatusEventHandler":{"retries_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"retries\" \"root\" .root) }}"}},"event_handlers":["nv.svc.farm.services.tasks.facilities.task_events.status.TaskStatusEventHandler","nv.svc.farm.services.dag.facilities.task_events.DAGTaskEventHandler"],"metrics_collect_interval":60,"url_prefix":"{{ .Values.apps.tasks.serviceConfig.url_prefix }}"}` | Available Task Settings. This section may include templates. |

### Defaults

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| defaults.additionalInitContainerTemplates | list | `[]` | Additional templates to render and add as an init container to the target deployment |
| defaults.affinity | object | `{}` | Affinity to attach to Application Deployment Spec |
| defaults.autoscaling | object | `{"enabled":false}` | Autoscaling has not been tested or used |
| defaults.configMapChecksumTemplate | string | `""` | Configmap checksum template to use and attach to deployment |
| defaults.env | list | `[{"name":"NV__SVC__GLOBAL__CONFIG_FILEPATH","value":"/configs/application.yaml"},{"name":"OTEL_SERVICE_NAME","value":"nv.svc.farm-{{ .svcName }}"},{"name":"OTEL_EXPORTER_OTLP_METRICS_PROTOCOL","value":"http/protobuf"},{"name":"CORE_LOADERS_FOR_DYNACONF","value":"[\"TOML\", \"YAML\"]"}]` | Environment Variables to add to Application Deployment/Container |
| defaults.extraVolumeMountTemplates | list | `[]` | Extra volume mount templates to add to Application container/deployment |
| defaults.extraVolumes | list | `[]` | Extra volumes to be attached to Deployment |
| defaults.fullnameOverride | string | `""` | Full Name Override for Application |
| defaults.image.args | list | `[]` | Image Args |
| defaults.image.cmd | list | `["python","-m","nv.svc.farm.services.{{ .svcName }}.entrypoint"]` | Image Command |
| defaults.image.pullPolicy | string | `"IfNotPresent"` | Image pull policy. |
| defaults.image.repository | string | `""` | Image Repository |
| defaults.image.tag | string | `""` | Image tag, overrides the image tag whose default is the chart appVersion. |
| defaults.imagePullSecrets | list | `[]` | Image pull secrets to attach to target serviceaccount |
| defaults.ingress.enableServiceHostRoutes | bool | `false` | Enable service-specific host routes like <svc>.BASE -> / |
| defaults.ingress.enabled | bool | `false` | Enable rendering and application of ingress objects |
| defaults.ingress.host | string | `""` | Ingress host to route on |
| defaults.ingress.ingressClassName | string | `""` | Leave empty to use cluster default, or specify your ingress controller class (e.g., "nginx", "traefik", "haproxy"). |
| defaults.ingress.path | string | `""` | Path to route |
| defaults.ingress.pathType | string | `"Prefix"` | Route type |
| defaults.ingress.tls | list | `[]` | Tls configuration |
| defaults.initImage.repository | string | `"busybox"` | Init image repository. Must have netcat installed. |
| defaults.initImage.resources | object | `{}` | Init Image resources, limits/reqs/etc |
| defaults.initImage.securityContext | object | `{}` | Init Image Security Context |
| defaults.initImage.tag | string | `"1.35"` | Init image tag. |
| defaults.initImage.waitForServices | list | `[]` | List of Applications this service should wait for before starting (dependencies). If object contains name, port, host keys the string may include a template. |
| defaults.nameOverride | string | `""` | Name Override for Application |
| defaults.nodeSelector | object | `{}` | Node Selector to attach to Application Deployment Spec |
| defaults.podAnnotations | object | `{}` | Pod Annotations to add to Pods created by the target K8s Deployment |
| defaults.podLabels | object | `{"kratos_logging":"true","kratos_metrics":"true"}` | Pod Labels to add to Pods created by the target K8s Deployment |
| defaults.podSecurityContext | object | `{}` | Pod Security Context |
| defaults.probes | object | `{"livenessProbe":{"failureThreshold":5,"httpGet":{"path":"/health","port":"http"},"initialDelaySeconds":30,"periodSeconds":5},"readinessProbe":{"failureThreshold":5,"httpGet":{"path":"/ready","port":"http"},"initialDelaySeconds":30,"periodSeconds":5},"startupProbe":{"failureThreshold":5,"httpGet":{"path":"/startup","port":"http"},"initialDelaySeconds":30,"periodSeconds":5}}` | Liveness, Readiness and Startup Probes for Applications |
| defaults.replicaCount | int | `1` | Replica count to use for target service |
| defaults.resources | object | `{}` | Resources to attach to target Deployment/container |
| defaults.revisionHistoryLimit | int | `5` | The amount of prior Deployment objects to maintain in history |
| defaults.role.bindingServiceAccountName | string | `""` | ServiceAccount name this role should bind to |
| defaults.role.create | bool | `false` | Create this role, if required for the Application |
| defaults.role.name | string | `""` | Roles name to use, ServiceAccount name will be used if empty |
| defaults.role.rules | list | `[]` | List of role permissions |
| defaults.secret | object | `{"create":false,"name":""}` | Create a secret, if available for the target Application |
| defaults.securityContext | object | `{"runAsNonRoot":true,"runAsUser":1000}` | Deployment Security Context |
| defaults.service.annotations | object | `{}` | Annotations |
| defaults.service.containerPort | int | `8011` | ContainerPort to forward traffic from Kubernetes Service into pod container |
| defaults.service.extraLabels | object | `{}` | Extra Labels |
| defaults.service.port | int | `80` | Port. |
| defaults.service.protocol | string | `"TCP"` | Protocol |
| defaults.service.targetPortName | string | `"http"` | Target Container port name. |
| defaults.service.transportHost | string | `"0.0.0.0"` | Transport host for service (the host the application is listening on). Usually is 0.0.0.0 in containers. |
| defaults.service.type | string | `"ClusterIP"` | Type |
| defaults.serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| defaults.serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| defaults.serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
| defaults.serviceConfig | object | `{"url_prefix":""}` | Configuration for Application, not directly an Application setting, should not be a template |
| defaults.serviceMonitor.enabled | bool | `false` | Enable rendering of service monitor |
| defaults.serviceMonitor.extraLabels | object | `{"release":"prometheus"}` | Extra labels to add to service monitor |
| defaults.serviceMonitor.prometheusNamespace | string | `""` | Sets prometheus namespace label |
| defaults.settings.nv.svc.core.root_path | string | `""` | Available Core Settings. |
| defaults.settings.nv.svc.facilities.monitoring.metrics | object | `{"collector_url":"","export_interval_s":30,"export_metrics_to_collector":false,"export_metrics_to_console":false,"mount_metrics_endpoint_separate_http_server":true,"secure":false,"separate_http_server_port":8002}` | Available Monitoring Facility Settings |
| defaults.settings.nv.svc.kubernetes.client | object | `{"kube_config_context":"","kube_config_path":"","load_in_cluster_config":true,"verify_ssl":true}` | Available Kubernetes Client Settings |
| defaults.settings.nv.svc.server.http | object | `{"cors":{"allow_credentials":false,"allow_headers":[],"allow_methods":[],"allow_origins":[],"enabled":false},"host":"{{ .svc.service.transportHost }}","http":{"enabled":true},"loop":"uvloop","port":"{{ .svc.service.containerPort }}"}` | Available HTTP Server Settings |
| defaults.tolerations | list | `[]` | Tolerations to attach to Application Deployment Spec |
| defaults.volumes | list | `[{"configMap":{"name":"{{ include \"nv-svc-farm.app.fullname\" . }}-config"},"name":"service-config"}]` | Volumes to add to Application Deployment/container |

### External Dependencies

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| external.mysql | object | `{"auth":{"database":"ovFarmTaskStore","existingSecret":null,"existingSecretPasswordKey":"mysql-password","password":"","username":"ovfarm"},"enabled":false,"host":"","port":3306}` | External MySQL Configuration |
| external.redis | object | `{"auth":{"enabled":false,"existingSecret":null,"existingSecretPasswordKey":"redis-password","password":""},"enabled":false,"host":"","port":6379,"tls":{"enabled":false}}` | External Redis Configuration |

### Global

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| global.image.repository | string | `"ghcr.io/nvidia/farm"` | Image Repository |
| global.image.tag | string | `""` | Image Tag |
| global.initImage.resources | object | `{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"500m","memory":"512Mi"}}` | Init image resources |
| global.serviceConfig | object | `{"controller_service_url":"","jobs_service_url":"","tasks_service_url":""}` | Configuration for Application, not directly an Application setting, should not be a template |
| global.settings.nv.svc.farm.controller | object | `{"agents_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"agents\" \"root\" .root) }}","operator_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"operator\" \"root\" .root) }}","service_host_url_format_str":"","tasks_service_url":"{{ include \"nv-svc-farm.app.connection-string\" (dict \"svcName\" \"tasks\" \"root\" .root) }}"}` | Available Controller Settings |
| global.settings.nv.svc.server.http.cors | object | `{"allow_credentials":false,"allow_headers":["*"],"allow_methods":["*"],"allow_origins":["*"],"enabled":true}` | Available Cors Settings |

### Other Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| apps.jobs.service.name | string | `"jobs"` |  |
| apps.jobs.serviceConfig.api_key | string | `""` | Direct API key to use |
| apps.operator.enabled | bool | `false` |  |
| apps.operator.serviceConfig.url_prefix | string | `"/agent/operator"` |  |
| defaults.extraEnv | list | `[]` | Extra Environment variables to add to Application Container. May include templates. |
| defaults.extraEnvTemplates | list | `[]` | Extra Environment Varialbes template functions to render and add to Application Deployment |
| defaults.extraVolumeMounts | list | `[]` | Extra volume mounts to add to container/deployment, excluding configuration configmap (automatic) |
| defaults.extraVolumeTemplates | list | `[]` | Extra volume templates to render and add to Deployment |
| defaults.settings.nv.svc.core.logging.log_level | string | `"INFO"` |  |
| defaults.volumeMounts | list | `[{"mountPath":"/configs","name":"service-config"}]` | Volume mounts to add to container/deployment |
| external.mysql.auth | object | `{"database":"ovFarmTaskStore","existingSecret":null,"existingSecretPasswordKey":"mysql-password","password":"","username":"ovfarm"}` | MySQL authentication configuration |
| external.mysql.auth.database | string | `"ovFarmTaskStore"` | Database name |
| external.mysql.auth.existingSecret | string | `nil` | Name of existing secret containing MySQL password |
| external.mysql.auth.existingSecretPasswordKey | string | `"mysql-password"` | Key in existingSecret that contains the password |
| external.mysql.auth.password | string | `""` | MySQL password (leave empty to use existingSecret) |
| external.mysql.auth.username | string | `"ovfarm"` | MySQL username |
| external.mysql.enabled | bool | `false` | Enable external MySQL connection |
| external.mysql.host | string | `""` | MySQL host (e.g., "mysql.database.svc.cluster.local") |
| external.mysql.port | int | `3306` | MySQL port |
| external.redis.auth | object | `{"enabled":false,"existingSecret":null,"existingSecretPasswordKey":"redis-password","password":""}` | Redis authentication configuration |
| external.redis.auth.enabled | bool | `false` | Enable Redis authentication |
| external.redis.auth.existingSecret | string | `nil` | Name of existing secret containing Redis password |
| external.redis.auth.existingSecretPasswordKey | string | `"redis-password"` | Key in existingSecret that contains the password |
| external.redis.auth.password | string | `""` | Redis password (leave empty to use existingSecret) |
| external.redis.enabled | bool | `false` | Enable external Redis connection |
| external.redis.host | string | `""` | Redis host (e.g., "redis.cache.svc.cluster.local") |
| external.redis.port | int | `6379` | Redis port |
| external.redis.tls | object | `{"enabled":false}` | Redis TLS configuration |
| external.redis.tls.enabled | bool | `false` | Enable TLS connection (uses rediss:// instead of redis://) |
| fullnameOverride | string | `""` |  |
| global.initImage | object | `{"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"500m","memory":"512Mi"}}}` | Configuration for Init Containers |
| imagePullSecrets | list | `[]` |  |
| nameOverride | string | `""` |  |
| redis_host_override | string | `""` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)

## License

Use of Farm is covered under the [Apache 2.0 License](https://github.com/NVIDIA/farm/blob/main/LICENSE).
