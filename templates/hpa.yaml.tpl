apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{APP_NAME}}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{APP_NAME}}
  minReplicas: {{REPLICAS_MIN}}
  maxReplicas: {{REPLICAS_MAX}}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 85
