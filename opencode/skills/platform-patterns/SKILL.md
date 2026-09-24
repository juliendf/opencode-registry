---
name: platform-patterns
description: Internal developer platform patterns, self-service infrastructure, and developer experience. Covers platform APIs, GitOps workflows, golden path templates, and Backstage.
---

# Platform Patterns

Internal developer platform (IDP) patterns, self-service infrastructure, and developer portals. Focus on reducing cognitive load, accelerating delivery, and building golden paths that teams actually adopt.

## Core Expertise

### Platform Architecture & Self-Service
- Multi-tenant platform design: RBAC, namespace isolation, resource quotas, cost allocation
- Self-service capabilities: environment provisioning, database creation, access management
- Platform APIs: RESTful/GraphQL design, webhooks, rate limiting, SDK generation

### Developer Experience
- Backstage portal: software templates, component registry, tech radar, API catalog
- Golden path templates: service scaffolding, CI/CD pipelines, security scanning, monitoring
- Onboarding automation: IDE plugins, CLI tools, interactive documentation, feedback loops

### Infrastructure Abstraction
- Crossplane compositions, Terraform modules, Helm chart templates, operator patterns
- Policy enforcement, configuration management, state reconciliation
- Secret management integration (Vault, External Secrets Operator)

### GitOps & Adoption
- Repository structure design, PR automation, approval workflows, drift detection
- Multi-cluster synchronization, environment promotion, rollback procedures
- Adoption metrics, champion programs, training, success tracking

## Workflow

1. **Discover**: Map developer journeys, identify friction points, assess current self-service coverage
2. **Design**: Define platform APIs, golden paths, and Backstage templates
3. **Build**: Implement self-service capabilities incrementally, starting with highest-impact services
4. **Measure**: Track adoption rates, provisioning times, developer satisfaction scores

## Key Principles

1. **Self-service by default**: Platform capabilities must be accessible without raising a ticket
2. **Golden paths, not golden cages**: Recommended paths that devs can deviate from with good reason
3. **Build incrementally**: Ship working self-service for one service type before scaling to all
4. **Measure adoption**: Provisioning time, self-service rate, and developer satisfaction are primary KPIs
5. **Backward compatibility**: Never break existing workflows during platform evolution
6. **Paved roads over policy**: Make the right thing the easy thing

## Example: Backstage Software Template

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: microservice-template
  title: Microservice (Go/Python)
  description: Golden path for new backend microservices
spec:
  owner: platform-team
  type: service
  parameters:
  - title: Service Info
    required: [name, language, team]
    properties:
      name:
        type: string
        pattern: '^[a-z][a-z0-9-]*$'
      language:
        type: string
        enum: [go, python]
      team:
        type: string
  steps:
  - id: fetch
    name: Fetch template
    action: fetch:template
    input:
      url: ./skeleton
      values:
        name: ${{ parameters.name }}
        language: ${{ parameters.language }}
  - id: publish
    name: Publish to GitHub
    action: publish:github
    input:
      repoUrl: github.com?repo=${{ parameters.name }}&owner=my-org
  - id: register
    name: Register in catalog
    action: catalog:register
    input:
      repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
```

## Example: Crossplane Self-Service Environment (Composite Resource Claim)

```yaml
# Developer creates this claim in their namespace -- platform handles the rest
apiVersion: platform.example.com/v1alpha1
kind: Environment
metadata:
  name: my-feature-env
  namespace: team-payments
spec:
  parameters:
    type: dev
    region: eu-west-1
    database:
      engine: postgres
      storageGB: 20
    networking:
      enableIngress: true
  writeConnectionSecretToRef:
    name: my-feature-env-creds
```

The underlying Composition provisions: VPC, RDS instance, EKS namespace, and IAM roles -- all reconciled automatically by Crossplane without developer knowledge of cloud primitives.

## Platform Metrics to Track

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| Self-service rate | > 90% | Tickets = platform debt |
| Provisioning time | < 5 min | Dev flow state preservation |
| Onboarding time | < 1 day | First-day experience signal |
| Developer satisfaction | > 4.5/5 | Leading indicator of adoption |
| Platform uptime | > 99.9% | Blocking dev teams is costly |
