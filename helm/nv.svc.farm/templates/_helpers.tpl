{{/*
Expand the name of the chart.
*/}}
{{- define "nv-svc-farm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "nv-svc-farm.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}





{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nv-svc-farm.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nv-svc-farm.labels" -}}
helm.sh/chart: {{ include "nv-svc-farm.chart" . }}
{{ include "nv-svc-farm.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- $mergedConfig := mergeOverwrite .Values.defaults .Values.global }}
{{- $mergedLabels := default dict $mergedConfig.service.extraLabels  -}}
{{- if $mergedLabels }}
{{ toYaml $mergedLabels }}
{{- end }}
{{- end }}

{{- define "nv-svc-farm.annotations" -}}
{{- $mergedAnnotations := merge .Values.service.annotations .Values.global.service.annotations -}}
{{- if $mergedAnnotations }}
{{ toYaml $mergedAnnotations }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nv-svc-farm.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nv-svc-farm.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: {{ .Chart.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "nv-svc-farm.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "nv-svc-farm.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
