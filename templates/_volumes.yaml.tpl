      volumes:
        - name: {{APP_NAME}}-logs
          persistentVolumeClaim:
            claimName: {{PROJECT}}-logs
