apiVersion: v1
kind: ConfigMap
metadata:
  name: {{CONFIGMAP_NAME}}
data:
{{ENV_KEYS}}
