{{- define "nv-svc-farm.tasks.checksums" }}
{{- $ := .root -}}
checksum/config1: {{ include (print $.Template.BasePath "/tasks/configmap-migrations.yaml") $ | sha256sum }}
{{- end }}