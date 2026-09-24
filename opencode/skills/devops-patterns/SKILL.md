---
name: devops-patterns
description: Modern CI/CD pipelines, GitOps workflows, and advanced deployment automation. Covers GitHub Actions, ArgoCD/Flux, progressive delivery, container security, and platform engineering.
---

# DevOps Patterns

Modern CI/CD pipelines, GitOps workflows, and advanced deployment automation including progressive delivery and zero-downtime strategies.

## Workflow

1. **Design**: Define pipeline stages, quality gates, and deployment strategy per environment
2. **Build**: Implement secure, fast CI pipeline with caching and parallel jobs
3. **Deploy**: Configure GitOps sync policies, progressive delivery, and rollback triggers
4. **Measure**: Track DORA metrics; alert on deployment failures and SLO degradation

## Key Principles

1. **Build once, deploy anywhere**: Single artifact promoted through environments via GitOps
2. **Automate everything**: No manual deployment steps; humans approve, automation executes
3. **Fast feedback**: Fail early in CI; keep pipeline under 10 minutes for developer feedback
4. **Progressive delivery**: Never deploy 100% to production instantly; use canary or blue-green
5. **Security in the pipeline**: Scan images and dependencies before every production deploy
6. **Immutable artifacts**: Version-tagged images; no `latest` tag in production

## Patterns

### GitHub Actions CI with Security Scanning

```yaml
name: CI/CD Pipeline
on:
  push: { branches: [main] }
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
      security-events: write
    steps:
    - uses: actions/checkout@v4
    - uses: docker/build-push-action@v5
      with: { context: ., push: false, tags: "${{ env.IMAGE }}:${{ github.sha }}", cache-from: type=gha, cache-to: type=gha,mode=max }
    - uses: aquasecurity/trivy-action@master
      with: { image-ref: "${{ env.IMAGE }}:${{ github.sha }}", format: sarif, exit-code: 1, severity: HIGH,CRITICAL }
    - name: Push & sign
      run: |
        docker push ${{ env.IMAGE }}:${{ github.sha }}
        cosign sign --yes ${{ env.IMAGE }}@${{ steps.build.outputs.digest }}
```

### Deployment Strategies

| Strategy    | Tool                     | Use Case                    |
|-------------|--------------------------|-----------------------------|
| Rolling     | K8s native               | Stateless workloads         |
| Blue-Green  | Argo Rollouts / Flagger  | Instant rollback required   |
| Canary      | Argo Rollouts / Flagger  | Traffic-based risk control  |
| Feature Flag| LaunchDarkly / Flagr     | Decouple deploy from release|

### Anti-Patterns
- Manual deployment steps in production
- Using `latest` or mutable tags in Kubernetes manifests
- Skipping image scanning for non-production environments
- Merging without passing CI checks first
- Long-lived feature branches without frequent rebase
