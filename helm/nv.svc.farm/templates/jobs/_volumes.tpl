{{- define "jobs.volume.mounts" -}}
{{- if not .Values.external.redis.enabled }}
- name: tmpdir
  mountPath: "/tmp"
{{- end }}
{{- end }}

{{- define "jobs.volumes" -}}
{{- if not .Values.external.redis.enabled }}
- name: tmpdir
  emptyDir:
    sizeLimit: 500Mi
{{- end }}
{{- end }}
