{{- define "nv-svc-farm.app.waitForService" -}}
{{- $svcName := .svcName -}}
{{- $mergedSvc := .svc -}}
{{- $ := .root -}}
{{- $ctx := (dict "svcName" $svcName "svc" $mergedSvc "root" .root "Release" .Release "Chart" .Chart "Template" .Template "Values" .Values ) -}}
{{- $waitForServices := $mergedSvc.initImage.waitForServices -}}
{{- $initImageRepo := $mergedSvc.initImage.repository -}}
{{- $initImageTag := $mergedSvc.initImage.tag -}}
{{- $targetInitResources := default dict $mergedSvc.initImage.resources }}
{{- $targetInitSecurityContext := default dict $mergedSvc.initImage.securityContext }}
{{- $g := $ -}}
{{- range $waitForServices -}}
    {{- $targetServiceName := "" -}}
    {{- $targetServicePort := 0 -}}
    {{- $targetServiceHost := "" -}}
    {{- $skipServiceLookup := false -}}

    {{- if kindIs "map" . }}
        {{- $targetServiceName = (tpl .name $ctx ) -}}
        {{- $targetServicePort = (tpl .port $ctx) -}}
        {{- $targetServiceHost = (tpl .host $ctx ) -}}
        {{- /* If both port and host are explicitly provided, skip service definition lookup */ -}}
        {{- if and $targetServicePort $targetServiceHost }}
        {{- $skipServiceLookup = true -}}
        {{- end }}
    {{- else -}}
        {{- $targetServiceName = . -}}

    {{- end -}}

    {{- if not $skipServiceLookup }}
    {{- $targetServiceDef := dict -}}
    {{- if hasKey $.Values.apps $targetServiceName -}}
    {{- $targetServiceDef = mergeOverwrite (deepCopy $.Values.defaults)   (deepCopy $.Values.global) (deepCopy (index $.Values.apps $targetServiceName)) -}}
    {{- else if hasKey $.Values $targetServiceName -}}
    {{- $targetServiceDef = mergeOverwrite (deepCopy $.Values.defaults) (deepCopy $.Values.global) (deepCopy (index $.Values $targetServiceName)) -}}
    {{- end -}}
    {{- if $targetServiceDef.enabled -}}

        {{- $targetService := $targetServiceDef.service -}}
        {{- if not $targetServicePort -}}
        {{- $targetServicePort = $targetService.port -}}
        {{- end -}}

        {{- if not $targetServiceHost -}}
            {{- $targetctx := (dict "svcName" . "root" $ "Release" $.Release "Chart" $.Chart "Template" $.Template "Values" $.Values ) -}}
            {{- $targetServiceHost = include "nv-svc-farm.app.fullname" $targetctx  -}}
        {{- end -}}

- name: wait-for-{{ $targetServiceName }}-svc
  image: "{{ $initImageRepo }}:{{ $initImageTag }}"
  command: ['sh', '-c', 'echo -e "Waiting for {{ $targetServiceName }} service"; while ! nc -z -w 2 {{ $targetServiceHost }} {{ $targetServicePort }}; do sleep 1; printf "-"; done; echo -e " >> {{ $targetServiceName }} service is ready.";']
  securityContext:
{{- toYaml $targetInitSecurityContext | nindent 4 }}
  resources:
{{- toYaml $targetInitResources | nindent 4 }}
{{ printf "\n" }}    {{- end }}
    {{- else }}
{{- /* Skip service lookup, use explicitly provided host and port */ -}}

- name: wait-for-{{ $targetServiceName }}-svc
  image: "{{ $initImageRepo }}:{{ $initImageTag }}"
  command: ['sh', '-c', 'echo -e "Waiting for {{ $targetServiceName }} service"; while ! nc -z -w 2 {{ $targetServiceHost }} {{ $targetServicePort }}; do sleep 1; printf "-"; done; echo -e " >> {{ $targetServiceName }} service is ready.";']
  securityContext:
{{- toYaml $targetInitSecurityContext | nindent 4 }}
  resources:
{{- toYaml $targetInitResources | nindent 4 }}
{{ printf "\n" }}    {{- end }}
{{- end }}
{{- end }}

{{- define "magda.var_dump" -}}
{{- . | mustToPrettyJson | printf "\nThe JSON output of the dumped var is: \n%s" | fail }}
{{- end -}}
