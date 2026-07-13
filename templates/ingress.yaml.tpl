apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{PROJECT}}-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "360"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "1800"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "1800"
    nginx.ingress.kubernetes.io/proxy-body-size: 30m
    nginx.ingress.kubernetes.io/proxy_buffer_size: 64k
    nginx.ingress.kubernetes.io/proxy_buffers: 16 32k;
    nginx.ingress.kubernetes.io/proxy_max_temp_file_size: "0"
    nginx.ingress.kubernetes.io/proxy_temp_file_write_size: 64k
    nginx.ingress.kubernetes.io/proxy_http_version: "1.1"
spec:
  rules:
{{INGRESS_RULES}}
