---
name: kubernetes-patterns
description: Kubernetes production patterns for container orchestration, cluster management, and cloud-native architectures. Covers security hardening, performance optimization, and workload orchestration.
---

# Kubernetes Patterns

Kubernetes production patterns for designing, deploying, and managing production clusters with security hardening and performance optimization.

## Workflow

1. **Assess**: Check current context, review existing configurations and security posture
2. **Design**: Define architecture, resource strategy, security policies, and networking
3. **Implement**: Deploy workloads, configure HPA/autoscaling, enable monitoring
4. **Validate**: Test failure scenarios, verify RBAC, confirm health probes and rollback

## Key Principles

1. **Least privilege**: RBAC and network policies scoped tightly to each workload
2. **Declarative configs**: All resources version-controlled, applied via GitOps
3. **Design for failure**: Pod disruption budgets, multi-AZ, readiness/liveness probes
4. **Resource limits**: Every workload has requests and limits set
5. **Immutable images**: No mutable tags in production; digest pinning preferred
6. **Observability first**: Metrics, logs, and traces instrumented before go-live

## Patterns

### Production Deployment with HPA

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      securityContext: { runAsNonRoot: true, runAsUser: 1000 }
      containers:
      - name: api
        image: registry.example.com/api-service@sha256:abc123
        resources:
          requests: { cpu: 100m, memory: 128Mi }
          limits:   { cpu: 500m, memory: 512Mi }
        readinessProbe:
          httpGet: { path: /healthz, port: 8080 }
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api-service }
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
```
