---
name: azure-patterns
description: Azure architecture patterns, services, and best practices. Covers AKS, Azure Functions, ARM templates, and Azure-specific solutions for production-grade cloud infrastructure.
---

# Azure Patterns

Azure architecture patterns and best practices across the Microsoft Azure ecosystem, Azure Well-Architected Framework, and cloud-native patterns.

## Workflow

1. **Design**: Apply Well-Architected pillars; choose compute model (VMs, AKS, Functions, Container Apps)
2. **Implement**: Use Bicep or Terraform for IaC; configure RBAC least privilege and Azure Policy
3. **Secure**: Enable Defender for Cloud, Private Link for PaaS, managed identities everywhere
4. **Operate**: Configure Azure Monitor alerts, Log Analytics, Application Insights, and Azure Backup

## Key Principles

1. **Managed identities always**: Never use passwords or service principal keys for Azure resources
2. **Private endpoints**: Secure PaaS services with Private Link; no public endpoints in production
3. **Infrastructure as code**: Bicep for Azure-native, Terraform for multi-cloud scenarios
4. **Azure Policy for governance**: Enforce compliance at subscription/management group scope
5. **High availability**: Availability zones, geo-replication, paired regions for DR
6. **Cost management**: Reservations, spot VMs, auto-shutdown for dev/test, right-sizing via Advisor

## Patterns

### AKS with Workload Identity and Private Cluster

```bicep
resource aks 'Microsoft.ContainerService/managedClusters@2024-01-01' = {
  name: clusterName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    dnsPrefix: clusterName
    agentPoolProfiles: [{
      name: 'system'
      count: nodeCount; vmSize: 'Standard_D4s_v5'
      osType: 'Linux'; mode: 'System'
      enableAutoScaling: true; minCount: 2; maxCount: 10
    }]
    networkProfile: { networkPlugin: 'azure'; networkPolicy: 'azure' }
    oidcIssuerProfile: { enabled: true }
    securityProfile: { workloadIdentity: { enabled: true } }
    apiServerAccessProfile: { enablePrivateCluster: true }
  }
}
```

### RBAC Role Assignment

```bash
IDENTITY_ID=$(az identity show --name my-app-identity --resource-group my-rg --query principalId -o tsv)
az role assignment create \
  --assignee "$IDENTITY_ID" \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/<sub-id>/resourceGroups/my-rg/providers/Microsoft.Storage/storageAccounts/mysa"
```
