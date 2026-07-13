apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{APP_NAME}}
spec:
  selector:
    matchLabels:
      app: {{APP_NAME}}
  template:
    metadata:
      labels:
        app: {{APP_NAME}}
    spec:
      terminationGracePeriodSeconds: 120
      imagePullSecrets:
        - name: registrypullsecret
      containers:
      - name: {{APP_NAME}}
        image: {{IMAGE}}
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: {{MEM_REQUEST}}
            cpu: {{CPU_REQUEST}}
          limits:
            memory: "{{MEM_LIMIT}}"
        ports:
        - name: http
          containerPort: {{PORT}}
        envFrom:
        - configMapRef:
            name: {{CONFIGMAP_NAME}}
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/bash
              - -c
              - |
                echo "PreStop duoc kich hoat. Dang tam dung 60 giay de cho giao dich..."
                sleep 60
{{VOLUME_MOUNTS}}
{{VOLUMES}}
