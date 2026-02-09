{{- define "nv-svc-farm.app.cfgchecksum" -}}
{{- $ := .root -}}
checksum/config: {{ include (print $.Template.BasePath "/settings-configmap.yaml") $ | sha256sum }}
{{- end }}