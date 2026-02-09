{{- define "nv-svc-farm.mysql.init" -}}
{{- $mysql := .Values.external.mysql -}}
{{- $mergedTasksSvc := mergeOverwrite (deepCopy .Values.defaults) (deepCopy .Values.global)  (deepCopy (index $.Values.apps "tasks")) -}}
{{- if and (not $mergedTasksSvc.serviceConfig.skip_db_migrations) $mysql.enabled }}
- name: run-db-migrations
  image: "bitnamilegacy/mysql:8.0"
  command: ['bash', '-c', '/etc/nvidia/farm/migrations/run_migrations.sh']
  securityContext:
    runAsUser: 1337
  env:
{{ include "nv-svc-farm.mysql.env-secret" . | nindent 2 }}
  volumeMounts:
  - name: migrations
    mountPath: /etc/nvidia/farm/migrations
      {{- end }}
{{- end -}}



{{/*
Define the mysql host
*/}}
{{- define "nv-svc-farm.mysql.host" -}}
{{- $ := .root -}}
{{- if $.Values.mysql_host_override }}
    {{- $.Values.mysql_host_override }}
{{- else if $.Values.external.mysql.enabled }}
    {{- $.Values.external.mysql.host }}
{{- else }}
    {{- fail "MySQL is not configured. Either enable external.mysql or set mysql_host_override" }}
{{- end }}
{{- end }}

{{/*
Define the mysql connection string
*/}}
{{- define "nv-svc-farm.mysql.connection_string" -}}
{{- $ := .root -}}
{{- $mysql := $.Values.external.mysql -}}
{{- $ctx := dict "root" .root "Release" .Release -}}
{{- $mysqlHost := include "nv-svc-farm.mysql.host" $ctx }}
    {{- if or $mysql.auth.password $mysql.auth.existingSecret }}
        {{- printf "@format mysql://%s:%s@%s:%v/%s" $mysql.auth.username "{env[MYSQL_PASSWORD]}" $mysqlHost $mysql.port $mysql.auth.database }}
    {{- else }}
        {{- printf "mysql://%s:%v/%s" $mysqlHost $mysql.port $mysql.auth.database }}
    {{- end }}
{{- end }}

{{- define "nv-svc-farm.mysql.env-secret" -}}
{{- $mysql := .Values.external.mysql -}}
{{- if or $mysql.auth.password $mysql.auth.existingSecret -}}
- name: MYSQL_PASSWORD
  valueFrom:
    secretKeyRef:
      name: |-
        {{- if $mysql.auth.existingSecret }}
        {{ $mysql.auth.existingSecret }}
        {{- else }}
        {{ include "nv-svc-farm.app.fullname" (dict "svcName" "tasks" "Values" .Values "Release" .Release "root" .root ) }}
        {{- end }}
      key: {{ $mysql.auth.existingSecretPasswordKey }}
{{- end -}}
{{- end -}}
