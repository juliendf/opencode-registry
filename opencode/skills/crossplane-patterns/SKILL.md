---
name: crossplane-patterns
description: Crossplane and Upbound patterns for cloud-native infrastructure as code with Kubernetes CRDs. Covers composition functions, provider configuration, managed resources, and control plane architecture.
---

# Crossplane Patterns

Crossplane and Upbound patterns for cloud-native infrastructure as code using Kubernetes Custom Resource Definitions, composition functions, and control plane architecture.

## Core Expertise

### Crossplane Core & Upbound Platform
- Managed Resources (MR): direct cloud resource representations with reconciliation
- Composite Resources (XR) and Claims: higher-level abstractions with namespaced access
- CompositeResourceDefinitions (XRD): OpenAPI v3 schema definitions for custom platform APIs
- Compositions: patch & transform, pipeline mode with function chaining
- Upbound Cloud: managed control planes, Spaces, organizations, Upbound CLI (up)

### Provider Ecosystem
- Official provider families: AWS, Azure, GCP, Kubernetes (monolithic vs family architecture)
- Provider configuration: authentication, rate limiting, region settings, credential injection
- Custom providers via Terrajet/Upjet generation from Terraform providers
- Package management: OCI-based distribution, version pinning, dependency resolution

### Composition Design
- Patch & Transform: field mapping, string transforms, convert, math operations
- Composition Functions (pipeline mode): Go-based, Python (beta), function-auto-ready
- Function pipelines: chaining, context passing, external data integration
- Environment Configs: injecting cluster-specific data into compositions
- PatchSets: reusable patch definitions for DRY compositions

### GitOps & Enterprise Patterns
- ArgoCD/Flux integration: sync waves for XRDs before Compositions, health checks for XRs
- Configuration packages: bundling XRDs and Compositions for versioned distribution
- Multi-tenancy: namespace isolation, RBAC per team, resource quotas
- Platform engineering: self-service APIs with Backstage catalog integration
- Migration from Terraform: state import patterns, brownfield adoption

## Workflow

1. **Design**: Define platform APIs (XRD schemas), user personas, and provider dependencies
2. **Implement**: Create XRDs, build Compositions with P&T or function pipelines, configure providers
3. **Test**: Validate resource creation, status propagation, RBAC, and edge cases
4. **Deploy**: Ship via GitOps; monitor control plane health, reconciliation timing, and resource conditions

## Key Principles

1. **Kubernetes-native**: Leverage K8s patterns (CRDs, controllers, RBAC) for all infrastructure
2. **Declarative reconciliation**: Desired state in Git; Crossplane continuously reconciles
3. **Composable abstractions**: Build platform APIs that hide cloud complexity from developers
4. **GitOps-ready**: XRDs and Compositions version-controlled and deployed via ArgoCD/Flux
5. **Secure credentials**: Use ESO or provider-specific workload identity; never store keys in cluster
6. **Developer-friendly**: Claims provide namespaced, self-service access without cluster-admin rights

## Examples: XRD + Composition with Function Pipeline

```yaml
# CompositeResourceDefinition - self-service PostgreSQL API
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.com
spec:
  group: database.example.com
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  claimNames:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        properties:
          spec:
            properties:
              parameters:
                required: [storageGB, tier]
                properties:
                  storageGB:
                    type: integer
                    minimum: 20
                  tier:
                    type: string
                    enum: [dev, prod]
---
# Composition - Pipeline mode with functions
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: postgres-on-aws
spec:
  compositeTypeRef:
    apiVersion: database.example.com/v1alpha1
    kind: XPostgreSQLInstance
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: rds-instance
        base:
          apiVersion: rds.aws.upbound.io/v1beta1
          kind: Instance
          spec:
            forProvider:
              region: eu-west-1
              instanceClass: db.t3.micro
              engine: postgres
              engineVersion: "15"
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.allocatedStorage
  - step: auto-ready
    functionRef:
      name: function-auto-ready
```
