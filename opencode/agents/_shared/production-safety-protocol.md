---
name: Production Safety Protocol
description: Shared production environment safety protocol for infrastructure agents
type: shared-config
mode: subagent
hidden: true
version: "1.0.0"
---

# Production Environment Safety Protocol

**All infrastructure agents MUST follow this protocol before executing any write/destructive command.**

## Detection & Confirmation Steps

1. **Detect environment** using the tool-appropriate command:
   - Kubernetes: `kubectl config current-context`
   - Terraform: `terraform workspace show`
   - Cloud CLI: check active profile/project/subscription
   - Helm: check release namespace

2. **Identify production indicators**:
   - Context/workspace/profile contains: `prod`, `production`, `live`, `prd`
   - Namespace: `production`, `prod-*`
   - AWS account, GCP project, or Azure subscription tagged as production

3. **Present confirmation before executing**:
   ```
   ⚠️  PRODUCTION ENVIRONMENT DETECTED

   Context: <tool-specific context>
   Command: <command to execute>
   Resources affected: <summary of changes>

   This will modify PRODUCTION resources.
   Proceed? (yes/no)
   ```

4. **Wait for explicit user confirmation** before executing.

**Never bypass this check. Production safety is paramount.**

## Inline Summary for Agent Files

When referencing this protocol in an agent, include this condensed block:

```
## CRITICAL: Production Safety
See `_shared/production-safety-protocol.md`. Before ANY write command:
1. Check environment context (kubectl/terraform/cloud CLI)
2. Warn if production indicators detected (prod, prd, live, production)
3. Show affected resources and require explicit user confirmation
Never bypass this check.
```
