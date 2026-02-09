{{/*
Define the redis host
*/}}
{{- define "redis.host" -}}
    {{- if .Values.global.redis_host_override }}
        {{- .Values.global.redis_host_override }}
    {{- else if .Values.external.redis.enabled }}
        {{- .Values.external.redis.host }}
    {{- else -}}
        {{- fail "Redis is not configured. Either enable external.redis or set redis_host_override" }}
    {{- end }}
{{- end }}

{{/*
Define the redis connection string
*/}}
{{- define "redis.connection_string" -}}
{{- $redisHost := include "redis.host" . }}
{{- $redis := .Values.external.redis -}}
{{- $scheme := ternary "rediss" "redis" $redis.tls.enabled -}}
    {{- if $redis.auth.enabled }}
        {{- print "@format " $scheme "://:" "{env[REDIS_PASSWORD]}" "@" $redisHost ":" $redis.port }}
    {{- else }}
        {{- print $scheme "://" $redisHost ":" $redis.port }}
    {{- end }}
{{- end }}
