{{/*
Lookup existing Jobs Api Key if it exists.
*/}}
{{- define "jobs.store.existingApiKey" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- if and (not $mergedSvc) (eq $svcName "jobs" ) -}}
    {{- $mergedSvc = mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values.apps "jobs")) -}}
{{- end -}}
{{- $ctx := dict "svcName" $svcName "svc" $mergedSvc "root" $ "Chart" .Chart "Release" .Release -}}

{{- $secret := (lookup "v1" "Secret" .Release.Namespace (include "nv-svc-farm.app.fullname" $ctx ) ) }}
{{- $secretData := (get $secret "data") | default dict }}
{{- $jobsKitDecoded := (get $secretData "api_key") | b64dec }}
{{- $jobsKitDecoded | trimAll " " | trimAll "\"" }}
{{- end }}

{{/*
Jobs Api Key
*/}}
{{- define "jobs.store.apiKey" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- if and (not $mergedSvc) (eq $svcName "jobs" ) -}}
    {{- $mergedSvc = mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values.apps "jobs")) -}}
{{- end -}}
{{- $ctx := dict "svcName" $svcName "svc" $mergedSvc "root" $ "Chart" .Chart "Release" .Release -}}
{{- if $mergedSvc.serviceConfig.api_key }}
{{- $mergedSvc.serviceConfig.api_key }}
{{- else if ne (include "jobs.store.existingApiKey" $ctx) "" }}
{{- include "jobs.store.existingApiKey" $ctx }}
{{- else }}
{{- $newKey := randAlphaNum 64 }}
{{- printf "%s" $newKey }}
{{- end }}
{{- end }}