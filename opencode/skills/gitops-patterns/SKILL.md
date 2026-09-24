---
name: gitops-patterns
description: GitOps patterns with ArgoCD and Flux for declarative, Git-driven continuous deployment. Covers sync policies, progressive delivery, drift detection, and multi-cluster management.
---

# GitOps Patterns

Git-driven continuous deployment using ArgoCD and Flux. Pull-based delivery with continuous reconciliation, drift detection, and progressive delivery on Kubernetes.

## Workflow

1. **Design**: Choose repository structure and environment promotion strategy
2. **Bootstrap**: Install ArgoCD or Flux; configure RBAC, SSO, and secret management
3. **Onboard**: Create Application/Kustomization resources; define sync policies and health checks
4. **Operate**: Monitor sync status, handle drift, manage secret rotation, perform upgrades

## Key Principles

1. **Git as single source of truth**: All changes via Git PRs; no manual kubectl in production
2. **Declarative always**: Define desired state; let controllers reconcile continuously
3. **Self-healing**: Enable auto-sync with selfHeal to correct drift automatically
4. **Auditability**: Complete deployment history in Git; every change has a commit and author
5. **Secure secrets**: Never store plaintext secrets in Git; use SOPS, ESO, or Sealed Secrets
6. **Progressive delivery**: Use Argo Rollouts or Flagger for canary/blue-green in production

## Patterns

### ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  finalizers: [resources-finalizer.argocd.argoproj.io]
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo
    targetRevision: main
    path: apps/my-app/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
    retry: { limit: 5, backoff: { duration: 5s, factor: 2, maxDuration: 3m } }
```

### Flux Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  sourceRef: { kind: GitRepository, name: my-repo }
  path: ./apps/my-app/overlays/production
  prune: true
  wait: true
  timeout: 3m
  healthChecks:
  - { apiVersion: apps/v1, kind: Deployment, name: my-app, namespace: my-app }
```

### Repository & Environment Strategy

Monorepo with Kustomize overlays (`base/` + `overlays/dev|staging|production/`) or per-repo with Helm per-environment values. Secrets via External Secrets Operator or Sealed Secrets; never plaintext in Git.
