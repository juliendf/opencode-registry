---
name: network-patterns
description: Cloud networking patterns, security architectures, and performance optimization. Covers multi-cloud connectivity, service mesh, zero-trust networking, SSL/TLS, global load balancing, and troubleshooting.
---

# Network Patterns

Modern cloud networking patterns, security architectures, and performance optimization across cloud and on-premises environments.

## Workflow

1. **Assess**: Review topology, traffic patterns, security posture, and current pain points
2. **Design**: Define network segmentation, routing strategy, security controls, and HA paths
3. **Implement**: Configure via IaC (Terraform/Ansible); validate connectivity at each OSI layer
4. **Monitor**: Set up flow logs, latency baselines, and alerts for anomalies and security events

## Key Principles

1. **Security first**: Zero-trust by default; no implicit trust between network segments
2. **Defense in depth**: Perimeter + NSG/security groups + network policies + service mesh mTLS
3. **Redundancy everywhere**: Multi-path, multi-region, no single points of failure on critical paths
4. **Automate changes**: Network config changes via IaC and GitOps; no manual CLI in production
5. **Test failure scenarios**: Validate failover quarterly; chaos test routing assumptions
6. **Document topology**: Maintain up-to-date network diagrams and IP address management

## Patterns

### Hub-and-Spoke with Transit Gateway

```hcl
resource "aws_ec2_transit_gateway" "main" {
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"
}

resource "aws_ec2_transit_gateway_vpc_attachment" "spoke" {
  for_each           = var.spoke_vpc_ids
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = each.value.vpc_id
  subnet_ids         = each.value.private_subnet_ids
}

resource "aws_route" "spoke_to_shared" {
  for_each               = var.spoke_route_table_ids
  route_table_id         = each.value
  destination_cidr_block = var.shared_services_cidr
  transit_gateway_id     = aws_ec2_transit_gateway.main.id
}
```

### Kubernetes Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
spec:
  podSelector: { matchLabels: { app: api-service } }
  policyTypes: [Ingress, Egress]
  ingress:
  - from:
    - podSelector: { matchLabels: { app: frontend } }
    ports: [{ protocol: TCP, port: 8080 }]
  egress:
  - to:
    - podSelector: { matchLabels: { app: postgres } }
    ports: [{ protocol: TCP, port: 5432 }]
  - to: [{ namespaceSelector: {} }]
    ports: [{ protocol: UDP, port: 53 }]
```

## Troubleshooting Methodology

Layer-by-layer connectivity validation:
1. **DNS**: `dig <service>.<namespace>.svc.cluster.local` -- verify resolution
2. **Reachability**: `kubectl exec -it <pod> -- curl -v http://<svc>:<port>/healthz`
3. **TLS**: `openssl s_client -connect <host>:443 -showcerts` -- verify cert chain
4. **Flow logs**: Enable VPC Flow Logs / NSG Flow Logs to capture dropped traffic
5. **Service mesh**: `istioctl analyze`, `kubectl describe virtualservice` for misrouted traffic
