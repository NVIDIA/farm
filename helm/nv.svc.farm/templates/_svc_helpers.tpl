{{/*
Create the full name of the app
Pass in a service object as context
*/}}
{{- define "nv-svc-farm.app.fullname" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- if not $mergedSvc -}}
    {{- $mergedSvc = mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values.apps $svcName)) -}}
{{- end -}}
{{- if $mergedSvc.fullnameOverride }}
{{- $mergedSvc.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default $svcName $mergedSvc.nameOverride }}
{{- if contains $name $.Release.Name }}
{{- $.Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" $.Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use
Pass in a servicename and service object as context
*/}}
{{- define "nv-svc-farm.app.serviceAccountName" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}

{{- if $mergedSvc.serviceAccount.create }}
{{- default (include "nv-svc-farm.app.fullname" (dict "svcName" $svcName "svc" $mergedSvc "root" $)) $mergedSvc.serviceAccount.name }}
{{- else }}
{{- default "default" $mergedSvc.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Common labels
*/}}
{{- define "nv-svc-farm.app.labels" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- if not $mergedSvc -}}
    {{- $mergedSvc = mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global)  (deepCopy (index $.Values.apps $svcName)) -}}
{{- end -}}
app: {{ $svcName }}
helm.sh/chart: {{ include "nv-svc-farm.chart" $ }}
{{ include "nv-svc-farm.app.selectorLabels" (dict "svcName" $svcName "root" $) }}
{{- if $.Chart.AppVersion }}
app.kubernetes.io/version: {{ $.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ $.Release.Service }}
{{- $mergedLabels := $mergedSvc.service.extraLabels -}}
{{- if $mergedLabels }}
{{ toYaml $mergedLabels }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nv-svc-farm.app.selectorLabels" -}}
{{- $svcName := .svcName -}}
{{- $ := .root -}}
app.kubernetes.io/name: {{ $svcName }}
app.kubernetes.io/instance: {{ $.Release.Name }}
app.kubernetes.io/component: {{ $.Chart.Name }}
{{- end }}


{{- define "nv-svc-farm.app.port" -}}
{{- $svcName := .svcName }}
{{- $mergedSvc := .svc }}
{{- $ := .root }}
{{- if not $mergedSvc }}
    {{- $mergedSvc = mergeOverwrite  (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values.apps $svcName)) }}
{{- end }}
{{- $serviceConfigURLOverridesKey := (printf "%s_service_url" $svcName) }}
{{- if and (hasKey $mergedSvc.serviceConfig $serviceConfigURLOverridesKey) (index $mergedSvc.serviceConfig $serviceConfigURLOverridesKey) }}
        {{- $host := (urlParse (index $mergedSvc.serviceConfig $serviceConfigURLOverridesKey)).host }}
    {{- int (split ":" $host)._1 }}
{{- else }}
{{- $mergedSvc.service.port }}
{{- end }}
{{- end }}

{{- define "nv-svc-farm.app.connection-string" -}}
{{- $svcName := .svcName }}
{{- $ := .root }}
{{- $prefix := .prefix }}
{{- $mergedSvc := mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values.apps $svcName)) }}
{{- $ctx := dict "svcName" $svcName "svc" $mergedSvc "root" $ }}
{{- $targetService := $mergedSvc -}}
{{- $serviceConfigURLOverridesKey := (printf "%s_service_url" $svcName) }}
{{- if and (hasKey $targetService.serviceConfig $serviceConfigURLOverridesKey) (index $targetService.serviceConfig $serviceConfigURLOverridesKey) }}
{{- index $targetService.serviceConfig $serviceConfigURLOverridesKey }}
{{- else }}
{{- $hostname := include "nv-svc-farm.app.fullname" $ctx }}
{{- $port := include "nv-svc-farm.app.port" $ctx }}
{{- $urlPrefix := default $prefix $targetService.serviceConfig.url_prefix }}
{{- $urlPrefix := default "" $urlPrefix }}
{{- (printf "http://%s:%v/%s" $hostname $port (trimPrefix "/" $urlPrefix) | trunc 63 | trimSuffix "-") | trimSuffix "/" }}
{{- end }}
{{- end }}

{{- define "nv-svc-farm.app.connection-host" -}}
{{- $svcName := .svcName }}
{{- $ := .root }}
{{- $prefix := .prefix }}
{{- $mergedSvc := mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values.apps $svcName)) }}

{{- $ctx := dict "svcName" $svcName "svc" $mergedSvc "root" $ }}
{{- $targetService := $mergedSvc }}
{{- $serviceConfigURLOverridesKey := (printf "%s_service_url" $svcName) }}
{{- if and (hasKey $targetService.serviceConfig $serviceConfigURLOverridesKey) (index $targetService.serviceConfig $serviceConfigURLOverridesKey) -}}
    {{- $host := (urlParse (index $targetService.serviceConfig $serviceConfigURLOverridesKey)).host }}
    {{- (split ":" $host)._0 }}
{{- else }}
    {{- include "nv-svc-farm.app.fullname" $ctx -}}
{{- end }}
{{- end }}