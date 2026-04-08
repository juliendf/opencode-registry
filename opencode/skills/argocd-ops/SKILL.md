---
model_tier: "medium"
name: argocd-ops
description: Safely interact with ArgoCD using the argocd CLI or an ArgoCD MCP server (whichever is available). Covers application management, sync operations, rollbacks, and structured debugging workflows. All state-changing operations require explicit user approval.
compatibility: opencode
license: MIT
metadata:
  version: "1.0.0"
---

# ArgoCD Operations

Safely interact with ArgoCD from any agent context. This skill detects available tooling (MCP server or argocd CLI), enforces approval for all state-changing operations, and provides structured workflows for application management and debugging.

## When to Use This Skill

Activate when the user needs to:

- Inspect, sync, create, or delete ArgoCD applications
- Check application health and sync status
- Manage application rollbacks and history
- Debug sync failures, degraded health, or drift issues
- Manage ArgoCD projects, repos, or clusters
- View and manage ApplicationSets

**Do NOT use this skill for:**

- Designing GitOps architecture or repository structure (delegate to the gitops-specialist subagent)
- Writing ArgoCD Application or ApplicationSet manifests from scratch (that is authoring, not operating)
- Installing or upgrading ArgoCD itself (use Helm/kubectl or the kubernetes-ops skill)
- Flux CD operations (this skill is ArgoCD-specific)

## Workflow

### Step 1: Detect Available Tooling

Before running any ArgoCD command, determine which interface is available.

#### 1.1 Check for ArgoCD MCP Server

Look for available MCP tools whose names contain `argocd` or `argo_cd` (case-insensitive). Examples of matching patterns:

- `argocd_app_get`, `argocd_app_list`, `argocd_app_sync`
- `argo_cd_get_application`, `argocd_list_applications`

If matching MCP tools are found, **prefer them** over the CLI. MCP tools return structured data and handle authentication natively.

#### 1.2 Fall Back to argocd CLI

If no ArgoCD MCP tools are detected, verify that the `argocd` CLI is available by running:

```bash
argocd version --client 2>/dev/null
```

If this succeeds, use `argocd` via Bash for all operations.

**Note:** The argocd CLI requires authentication. If commands fail with auth errors, instruct the user to log in first:

```bash
argocd login <server> --sso
```

#### 1.3 Fall Back to kubectl

If neither MCP tools nor the argocd CLI are available, ArgoCD resources can be queried via kubectl since ArgoCD uses Kubernetes CRDs. Verify kubectl is available:

```bash
kubectl get crd applications.argoproj.io 2>/dev/null
```

If the CRD exists, use kubectl for read operations on ArgoCD resources. Note that kubectl cannot trigger syncs or perform ArgoCD-specific operations -- only inspect resources.

#### 1.4 Fail Clearly if Nothing is Available

If no tooling is found, stop and inform the user:

> No ArgoCD tooling detected. To proceed, either:
>
> - Install the `argocd` CLI: <https://argo-cd.readthedocs.io/en/stable/cli_installation/>
> - Configure an ArgoCD MCP server in your OpenCode settings
> - Ensure `kubectl` has access to a cluster with ArgoCD installed

Do not attempt to install tooling.

### Step 2: Establish Context

Before any operation, detect and display the current ArgoCD context. **Always do this first.**

#### Using argocd CLI

```bash
argocd context
```

This shows the current ArgoCD server and authenticated user.

#### Using kubectl

```bash
kubectl config current-context
kubectl get applications.argoproj.io -A --no-headers 2>/dev/null | head -5
```

This shows the Kubernetes context and confirms ArgoCD applications exist.

Present the result to the user:

> **ArgoCD server:** `<server-url>` (or Kubernetes context if using kubectl)
> **Authenticated as:** `<user>` (if available)
> **Applications found:** `<count>`
>
> Proceeding in this context. Confirm or specify a different context.

**Wait for user confirmation before proceeding.** If the user specifies a different server or context, switch accordingly before continuing.

### Step 3: Classify and Execute Operations

Every ArgoCD operation falls into one of two categories. **Never skip classification.**

#### Read-Only Operations (No Approval Required)

These commands inspect state without modifying it. Execute freely:

| Operation | argocd CLI | kubectl equivalent |
|---|---|---|
| List applications | `argocd app list` | `kubectl get applications.argoproj.io -A` |
| Get app details | `argocd app get <app>` | `kubectl get application <app> -n argocd -o yaml` |
| View app diff | `argocd app diff <app>` | -- |
| View app history | `argocd app history <app>` | -- |
| View app manifests | `argocd app manifests <app>` | -- |
| View app logs | `argocd app logs <app>` | -- |
| List projects | `argocd proj list` | `kubectl get appprojects.argoproj.io -n argocd` |
| Get project details | `argocd proj get <proj>` | `kubectl get appproject <proj> -n argocd -o yaml` |
| List repos | `argocd repo list` | `kubectl get secrets -n argocd -l argocd.argoproj.io/secret-type=repository` |
| List clusters | `argocd cluster list` | `kubectl get secrets -n argocd -l argocd.argoproj.io/secret-type=cluster` |
| List ApplicationSets | -- | `kubectl get applicationsets.argoproj.io -A` |
| Get account info | `argocd account get-user-info` | -- |

#### State-Changing Operations (Approval Required)

**All** of the following require explicit user approval before execution. Present what will be done and wait for confirmation.

**Application sync and lifecycle:**

- `argocd app sync <app>` -- trigger a sync to apply desired state
- `argocd app create <app>` -- register a new application
- `argocd app delete <app>` -- remove an application (and optionally its resources)
- `argocd app set <app>` -- modify application parameters
- `argocd app unset <app>` -- remove application parameters
- `argocd app patch <app>` -- patch application fields
- `argocd app rollback <app> <id>` -- revert to a previous sync revision
- `argocd app terminate-op <app>` -- cancel an in-progress sync operation
- `argocd app wait <app>` -- wait for an app to reach a target state (safe but blocks)

**Resource-level actions:**

- `argocd app actions run <app> <action>` -- run a resource action (e.g., restart)
- `argocd app resources delete <app> --kind <kind> --name <name>` -- delete a specific resource within an app

**Project management:**

- `argocd proj create <proj>` -- create a new project
- `argocd proj delete <proj>` -- delete a project
- `argocd proj set <proj>` -- modify project settings
- `argocd proj add-destination <proj>` -- allow a new cluster/namespace target
- `argocd proj remove-destination <proj>` -- remove a cluster/namespace target
- `argocd proj add-source <proj>` -- allow a new repository source
- `argocd proj remove-source <proj>` -- remove a repository source
- `argocd proj allow-cluster-resource <proj>` / `deny-cluster-resource` -- modify cluster resource permissions
- `argocd proj allow-namespace-resource <proj>` / `deny-namespace-resource` -- modify namespace resource permissions

**Repository and cluster management:**

- `argocd repo add <url>` -- register a new repository
- `argocd repo rm <url>` -- remove a repository
- `argocd cluster add <context>` -- register a new cluster
- `argocd cluster rm <server>` -- remove a cluster

**Account management:**

- `argocd account update-password` -- change account password
- `argocd account generate-token` -- generate an API token

**kubectl-based mutations (when using kubectl fallback):**

- `kubectl apply` on ArgoCD CRDs (Application, AppProject, ApplicationSet)
- `kubectl delete` on ArgoCD resources
- `kubectl patch` / `kubectl edit` on ArgoCD resources

#### Approval Format

Before executing any state-changing operation, present:

```text
ACTION REQUIRES APPROVAL

Server:      <argocd-server or k8s-context>
Application: <app-name> (if applicable)
Project:     <project-name> (if applicable)
Command:     <full command to execute>
Effect:      <brief description of what this will change>

Proceed? (yes/no)
```

**Wait for explicit "yes" before executing.** If the user declines, do not execute and ask for alternative instructions.

### Step 4: Production Environment Safety

After classifying an operation as state-changing, apply an additional safety check for production environments.

#### 4.1 Detect Production

Check if any of the following production indicators appear (case-insensitive):

- Application name contains: `prod`, `prd`, `production`, `live`
- Destination namespace contains: `prod`, `prd`, `production`, `live`
- Destination cluster name or URL suggests production
- ArgoCD project name contains production indicators

#### 4.2 Production Warning

If production indicators are detected, escalate the approval with an explicit warning:

```text
PRODUCTION ENVIRONMENT DETECTED

Server:      <argocd-server>
Application: <app-name>
Destination: <cluster> / <namespace>
Command:     <full command>
Effect:      <summary of what will change>

This will modify a PRODUCTION application. Proceed? (yes/no)
```

**Never bypass this check.** Production safety is paramount regardless of how routine the operation appears.

## Common Operations

### Application Sync

Before syncing, always check the current state and diff:

```bash
# Check current status
argocd app get <app>

# Preview what will change
argocd app diff <app>

# Sync (requires approval)
argocd app sync <app>

# Sync specific resources only
argocd app sync <app> --resource <group>:<kind>:<name>

# Sync with prune (delete resources not in Git)
argocd app sync <app> --prune

# Force sync (replace instead of apply)
argocd app sync <app> --force

# Dry-run sync
argocd app sync <app> --dry-run
```

Always run `argocd app diff` before `argocd app sync` so the user can see what will change. Suggest `--dry-run` for complex or unfamiliar syncs.

### Application Rollback

```bash
# View deployment history
argocd app history <app>

# Rollback to a specific revision (requires approval)
argocd app rollback <app> <history-id>
```

Always show `argocd app history` before rolling back so the user can choose the correct revision.

### Application Creation

```bash
# Create from a Git repo
argocd app create <app> \
  --repo <repo-url> \
  --path <path> \
  --dest-server <cluster-url> \
  --dest-namespace <namespace> \
  --project <project>

# Create from a Helm chart
argocd app create <app> \
  --repo <helm-repo-url> \
  --helm-chart <chart-name> \
  --revision <version> \
  --dest-server <cluster-url> \
  --dest-namespace <namespace> \
  --project <project>
```

### Application Deletion

```bash
# Delete the ArgoCD application only (keep deployed resources)
argocd app delete <app> --cascade=false

# Delete the application AND all deployed resources
argocd app delete <app> --cascade=true
```

Always clarify with the user whether `--cascade=true` or `--cascade=false` is intended. The default (`--cascade=true`) deletes all deployed resources -- this is destructive.

## Debugging Workflows

When the user reports an ArgoCD issue, identify the failure pattern and follow the corresponding checklist. Run each step in order, stopping when the root cause is identified.

### Sync Failed

An application sync completed with errors.

1. `argocd app get <app>` -- check Sync Status, Health Status, and Conditions
2. `argocd app sync <app> --dry-run` -- preview what the sync would do (read-only)
3. Check sync result details in the app events or UI for specific resource errors
4. Common causes:
   - Schema validation errors (invalid manifests)
   - Immutable field changes (e.g., changing a Service type)
   - Resource already exists and is not managed by ArgoCD
   - Insufficient RBAC permissions for the ArgoCD service account
5. If a specific resource is failing: `argocd app resources <app>` to list all resources and their sync status
6. Check ArgoCD application controller logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=100`

### OutOfSync but Not Syncing

An application shows OutOfSync but auto-sync is not triggering.

1. `argocd app get <app>` -- check if auto-sync is enabled in the sync policy
2. Check if the app has a sync window that is currently blocking: `argocd proj windows list <project>`
3. Check if the app has reached its retry limit: look at `status.operationState`
4. Check if there is a pending operation: `argocd app get <app> -o json | grep operationState`
5. Verify the source repo is accessible: `argocd repo get <repo-url>`
6. Check if the refresh has detected changes: `argocd app diff <app>`

### Degraded Health

An application is synced but health status is Degraded.

1. `argocd app get <app>` -- identify which resources are Degraded
2. `argocd app resources <app>` -- list all resources with their health status
3. For each degraded resource, inspect the underlying Kubernetes resource:
   - Deployments: `kubectl describe deployment <name> -n <ns>` -- check replica counts, conditions
   - Pods: follow the CrashLoopBackOff or Pending checklist from the kubernetes-ops skill
   - Services: check endpoints are populated
   - Ingress: check if the load balancer is provisioned
4. Check if health checks are custom: misconfigured custom health checks can report false Degraded status
5. Check ArgoCD resource health assessment: `argocd app get <app> -o json | jq '.status.resources[] | select(.health.status != "Healthy")'`

### Missing / Unknown Health

Resources show Missing or Unknown health status.

1. `argocd app get <app>` -- identify Missing/Unknown resources
2. For Missing resources: they exist in Git but not in the cluster
   - Check if the namespace exists
   - Check if the CRD is installed (for custom resources)
   - Check if a previous sync was partial or failed
3. For Unknown health: ArgoCD does not have a health check for this resource type
   - This is informational, not necessarily an error
   - Custom health checks can be added via `argocd-cm` ConfigMap
4. Verify the application destination: `argocd app get <app> -o json | jq '.spec.destination'`

### Repository Connection Issues

ArgoCD cannot connect to or read from a Git repository.

1. `argocd repo list` -- check repository connection status
2. `argocd repo get <repo-url>` -- get detailed status for the specific repo
3. Common causes:
   - SSH key expired or revoked
   - PAT/token expired
   - Repository URL changed or repo deleted
   - Network connectivity from ArgoCD to the Git server
4. Check ArgoCD repo-server logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-repo-server --tail=100`
5. For SSH repos, verify the known hosts configuration: `kubectl get configmap argocd-ssh-known-hosts-cm -n argocd -o yaml`

### ApplicationSet Not Generating Applications

An ApplicationSet exists but is not creating the expected applications.

1. `kubectl get applicationset <name> -n argocd -o yaml` -- check the spec and status
2. Check the generator configuration:
   - Git generator: verify the repo, revision, and file/directory patterns
   - Cluster generator: `argocd cluster list` to verify registered clusters
   - Matrix/merge generators: check inner generator outputs
3. Check ApplicationSet controller logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-applicationset-controller --tail=100`
4. Verify the template renders correctly by manually substituting generator parameters
5. Check if the AppProject allows the target destinations and sources

## Guidelines

### General Principles

- **Diff before sync**: Always run `argocd app diff` before `argocd app sync` so the user sees what will change.
- **Check before delete**: Before deleting an app, show its current state and clarify cascade behavior with the user.
- **One operation at a time**: Do not batch multiple state-changing operations. Execute each one individually with its own approval cycle.
- **Show before mutate**: Before any sync, rollback, or deletion, show the current state of the affected application.
- **Prefer declarative**: When creating or modifying applications, prefer suggesting manifest changes committed to Git over imperative CLI commands.

### MCP Server Considerations

- MCP tools may use different parameter names than argocd CLI flags. Adapt the workflow to the tool's interface while maintaining the same safety checks.
- If the MCP server returns structured data (JSON), prefer it over CLI text output for accuracy.
- Apply the same approval requirements regardless of whether the operation is executed via MCP or CLI.

### Relationship with kubernetes-ops Skill

This skill manages ArgoCD as a deployment tool. For issues that trace to underlying Kubernetes resources (pod failures, networking, storage), defer to the kubernetes-ops skill for debugging. The handoff point is when an ArgoCD-level investigation reveals the issue is in the deployed workload, not in the sync/delivery pipeline.

### What This Skill Does NOT Cover

- Designing GitOps repository structures or branching strategies
- Writing ArgoCD Application, ApplicationSet, or AppProject manifests from scratch
- Installing, upgrading, or configuring the ArgoCD server itself
- Flux CD operations (use a separate workflow)
- Deep Kubernetes debugging beyond ArgoCD resource health (use the kubernetes-ops skill)
