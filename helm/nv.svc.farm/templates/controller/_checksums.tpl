{{- define "nv-svc-farm.controller.checksums" }}
{{- $ := .root -}}
checksum/config1: {{ include (print $.Template.BasePath "/controller/configmap-capacity.yaml") $ | sha256sum }}
checksum/config2: {{ include (print $.Template.BasePath "/controller/configmap-container-spec-overrides.yaml") $ | sha256sum }}
checksum/config3: {{ include (print $.Template.BasePath "/controller/configmap-job-template-spec-overrides.yaml") $ | sha256sum }}
{{- end }}