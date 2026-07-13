apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{PROJECT}}-logs
spec:
  resources:
    requests:
      storage: 2Gi
  storageClassName: nfs-client
  accessModes:
    - ReadWriteMany