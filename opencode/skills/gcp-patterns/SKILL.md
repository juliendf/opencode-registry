---
name: gcp-patterns
description: GCP architecture patterns, services, and best practices. Covers GKE, Cloud Run, Cloud Functions, and GCP-specific solutions for production-grade cloud infrastructure.
---

# GCP Patterns

Google Cloud architecture patterns and best practices across GCP services and cloud-native patterns.

## Workflow

1. **Design**: Choose compute model (GKE Autopilot, Cloud Run, Functions); design VPC and IAM
2. **Implement**: Use Terraform or Config Connector for IaC; enforce Organization Policies
3. **Secure**: Enable Binary Authorization (GKE), VPC Service Controls, Workload Identity, Security Command Center
4. **Operate**: Configure Cloud Monitoring SLOs, log sinks, Error Reporting, and Recommender

## Key Principles

1. **Serverless first**: Cloud Run and Cloud Functions for simplicity before moving to GKE
2. **GKE Autopilot**: Use Autopilot mode unless specific node-level control is required
3. **Workload Identity always**: Never use service account key files; use Workload Identity for pods
4. **Organization Policies**: Enforce security constraints at org level for all projects
5. **BigQuery for analytics**: GCP's primary analytics strength; use it for any data warehouse need
6. **Committed use discounts**: 1-year CUD for predictable GKE/VM workloads

## Patterns

### GKE Autopilot with Workload Identity

```hcl
resource "google_container_cluster" "main" {
  name     = "prod-cluster"
  location = "europe-west1"
  enable_autopilot = true
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }
}

resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.app.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[production/app-service]"
}
```

### Landing Zone Organization

Bootstrapped org structure: `Organization > Folder: prod|non-prod|shared-services > Project per concern (networking, GKE, data, audit)`. Organization Policies enforced at root: `requireShieldedVm`, `disableServiceAccountKeyCreation`, `restrictCloudRunRegion`.
