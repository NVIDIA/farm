{{- define "nv-svc-farm.app.envvars" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}

{{- $env := $mergedSvc.env }}
{{- $extraEnv := $mergedSvc.extraEnv }}
{{- $extraEnvTemplates := $mergedSvc.extraEnvTemplates }}

{{- $ctx := (dict "svcName" $svcName "svc" $mergedSvc "Template" $.Template "Values" $.Values "root" .root) -}}
{{- tpl ((concat $env $extraEnv) | toYaml ) $ctx }}
{{ range $extraEnvTemplates -}}
{{- include . $ctx }}
{{- end }}
{{- end }}