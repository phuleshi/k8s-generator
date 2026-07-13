  - host: {{HOST}}
    http:
      paths:
      - pathType: Prefix
        path: /
        backend:
          service:
            name: {{SVC_NAME}}
            port:
              number: 80
