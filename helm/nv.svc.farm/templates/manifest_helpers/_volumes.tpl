{{- define "nv-svc-farm.app.volumes" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- $extraVolumeTemplates := concat (default list .svc.extraVolumeTemplates) (default list $.Values.global.extraVolumeTemplates) ($.Values.defaults.extraVolumeTemplates) -}}
{{- $allVolumes := concat $mergedSvc.volumes $mergedSvc.extraVolumes }}
{{- $ctx := (dict "svcName" $svcName "svc" $mergedSvc "Template" $.Template "Values" $.Values "Release" $.Release "root" $) -}}

{{- tpl ( $allVolumes | toYaml ) $ctx }}
{{- range $extraVolumeTemplates }}
{{ include . $ctx }}
{{- end }}

{{- end }}

{{- define "nv-svc-farm.app.volumeMounts" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- $extraVolumeMountTemplates := concat (default list .svc.extraVolumeMountTemplates) (default list $.Values.global.extraVolumeMountTemplates) ($.Values.defaults.extraVolumeMountTemplates) -}}
{{- $ctx := (dict "svcName" $svcName "svc" $mergedSvc "Template" $.Template "Values" $.Values "Release" $.Release "root" $) -}}
{{ tpl ((concat $mergedSvc.volumeMounts $mergedSvc.extraVolumeMounts) | toYaml) $ctx }}
{{- range $extraVolumeMountTemplates }}
{{ include . $ctx }}
{{- end }}

{{- end -}}


