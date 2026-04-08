---
model_tier: "medium"
name: kubernetes-ops
description: Safely interact with Kubernetes clusters using kubectl CLI or a Kubernetes MCP server (whichever is available). Covers core operations, Helm lifecycle, and structured debugging workflows. All state-changing operations require explicit user approval.
compatibility: opencode
license: MIT
metadata:
  version: "1.0.0"
---

# Kubernetes Operations

Safely interact with Kubernetes clusters from any agent context. This skill detects available tooling (MCP server or kubectl CLI), enforces approval for all state-changing operations, and provides structured workflows for common tasks and debugging.

## When to Use This Skill

Activate when the user needs to:

- Inspect, create, update, or delete Kubernetes resources
- Debug failing pods, services, or deployments
- Manage Helm releases (install, upgrade, rollback, uninstall)
- Check cluster status, logs, or resource usage
- Troubleshoot networking, scheduling, or OOM issues

**Do NOT use this skill for:**

- Designing Kubernetes architectures from scratch (delegate to the kubernetes-expert subagent)
- Writing Helm charts or Kustomize overlays (that is authoring, not operating)
- Cloud provider cluster provisioning (EKS, GKE, AKS setup)

## Workflow

### Step 1: Detect Available Tooling

Before running any Kubernetes command, determine which interface is available.

#### 1.1 Check for Kubernetes MCP Server

Look for available MCP tools whose names contain `kubernetes` or `kubectl` (case-insensitive). Examples of matching patterns:

- `kubectl_get`, `kubectl_apply`, `kubernetes_get_pods`
- `k8s_list_resources`, `kube_describe`

If matching MCP tools are found, **prefer them** over the CLI. MCP tools return structured data and handle authentication natively.

#### 1.2 Fall Back to kubectl CLI

If no Kubernetes MCP tools are detected, verify that `kubectl` is available by running:

```bash
kubectl version --client --short 2>/dev/null || kubectl version --client 2>/dev/null
```

If this succeeds, use `kubectl` via Bash for all operations.

#### 1.3 Fail Clearly if Neither is Available

If neither MCP tools nor `kubectl` CLI are found, stop and inform the user:

> No Kubernetes tooling detected. To proceed, either:
>
> - Install `kubectl`: <https://kubernetes.io/docs/tasks/tools/>
> - Configure a Kubernetes MCP server in your OpenCode settings

Do not attempt to install tooling.

### Step 2: Establish Context

Before any operation, detect and display the current Kubernetes context and namespace. **Always do this first.**

Run the following (via MCP or CLI):

```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{..namespace}'
```

Present the result to the user:

> **Current context:** `<context-name>`
> **Current namespace:** `<namespace>` (or `default` if unset)
>
> Proceeding in this context. Confirm or specify a different context/namespace.

**Wait for user confirmation before proceeding.** If the user specifies a different context or namespace, switch accordingly before continuing.

### Step 3: Classify and Execute Operations

Every Kubernetes operation falls into one of two categories. **Never skip classification.**

#### Read-Only Operations (No Approval Required)

These commands inspect state without modifying it. Execute freely:

| Operation | kubectl | Helm |
|---|---|---|
| List/get resources | `kubectl get <resource>` | `helm list` |
| Describe resources | `kubectl describe <resource>` | `helm status <release>` |
| View logs | `kubectl logs <pod>` | -- |
| Resource usage | `kubectl top pods/nodes` | -- |
| View config | `kubectl config view` | `helm get values <release>` |
| Explain resources | `kubectl explain <resource>` | `helm show values <chart>` |
| Search charts | -- | `helm search repo <keyword>` |
| List repos | -- | `helm repo list` |

#### State-Changing Operations (Approval Required)

**All** of the following require explicit user approval before execution. Present what will be done and wait for confirmation.

**Cluster resource mutations:**

- `kubectl apply` -- create or update resources from manifests
- `kubectl create` -- imperatively create resources
- `kubectl delete` -- remove resources
- `kubectl patch` -- partial update of resources
- `kubectl edit` -- interactive edit (avoid; prefer apply)
- `kubectl scale` -- change replica count
- `kubectl label` / `kubectl annotate` -- metadata changes that may trigger controllers
- `kubectl cordon` / `kubectl uncordon` -- mark nodes unschedulable
- `kubectl drain` -- evict all pods from a node
- `kubectl taint` -- add/remove node taints
- `kubectl rollout restart` -- restart all pods in a workload
- `kubectl rollout undo` -- rollback a workload

**Container interaction (may cause side effects):**

- `kubectl exec` -- execute commands inside a running container
- `kubectl cp` -- copy files to/from containers
- `kubectl port-forward` -- open a network tunnel to a pod/service

**Helm mutations:**

- `helm install` -- deploy a new release
- `helm upgrade` -- update an existing release
- `helm uninstall` -- remove a release
- `helm rollback` -- revert to a previous revision
- `helm repo add` / `helm repo update` -- modify local repo configuration

#### Approval Format

Before executing any state-changing operation, present:

```text
ACTION REQUIRES APPROVAL

Context:   <current-context>
Namespace: <target-namespace>
Command:   <full command to execute>
Effect:    <brief description of what this will change>

Proceed? (yes/no)
```

**Wait for explicit "yes" before executing.** If the user declines, do not execute and ask for alternative instructions.

### Step 4: Production Environment Safety

After classifying an operation as state-changing, apply an additional safety check for production environments.

#### 4.1 Detect Production

Check if any of the following patterns appear in the current context name or target namespace (case-insensitive):

- `prod`, `prd`, `production`, `live`

#### 4.2 Production Warning

If production indicators are detected, escalate the approval with an explicit warning:

```text
PRODUCTION ENVIRONMENT DETECTED

Context:            <context-name>
Namespace:          <namespace>
Command:            <full command>
Resources affected: <summary of what will change>

This will modify PRODUCTION resources. Proceed? (yes/no)
```

**Never bypass this check.** Production safety is paramount regardless of how routine the operation appears.

## Helm Operations

### Repo Management

```bash
# Add a chart repository
helm repo add <name> <url>

# Update all repositories
helm repo update

# Search for charts
helm search repo <keyword>

# List configured repos
helm repo list
```

`helm repo list` and `helm search repo` are read-only. `helm repo add` and `helm repo update` require approval (they modify local state).

### Release Lifecycle

```bash
# Install a new release
helm install <release> <chart> -n <namespace> --values values.yaml

# Check release status
helm status <release> -n <namespace>

# Upgrade an existing release
helm upgrade <release> <chart> -n <namespace> --values values.yaml

# Rollback to a previous revision
helm rollback <release> <revision> -n <namespace>

# Uninstall a release
helm uninstall <release> -n <namespace>

# Get current values
helm get values <release> -n <namespace>
```

Always include `-n <namespace>` explicitly in Helm commands. Before `helm upgrade` or `helm uninstall`, run `helm status` first and show the user the current state.

## Debugging Workflows

When the user reports a Kubernetes issue, identify the failure pattern and follow the corresponding checklist. Run each step in order, stopping when the root cause is identified.

### CrashLoopBackOff

A pod is repeatedly crashing and being restarted.

1. `kubectl describe pod <pod> -n <ns>` -- check Events section for error messages, check exit code in Last State
2. `kubectl logs <pod> -n <ns>` -- check application logs for the current (possibly partial) run
3. `kubectl logs <pod> -n <ns> --previous` -- check logs from the last crashed container
4. Check if the image is correct: verify the `Image` field in describe output
5. Check resource limits: look for OOMKilled exit code (137) in container status
6. Check for missing ConfigMaps/Secrets: look for mount errors in Events
7. Check liveness probe: misconfigured probes can kill healthy containers

### Pending Pods

A pod is stuck in Pending state and not being scheduled.

1. `kubectl describe pod <pod> -n <ns>` -- check Events and Conditions for scheduling failures
2. Check node resources: `kubectl describe nodes | grep -A 5 "Allocated resources"` or `kubectl top nodes`
3. Check for taints/tolerations: `kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints`
4. Check for node selector or affinity mismatches in the pod spec
5. If using PVCs: `kubectl get pvc -n <ns>` -- check if the PVC is Bound
6. Check ResourceQuota: `kubectl describe resourcequota -n <ns>`

### OOMKilled

A container was terminated due to exceeding memory limits.

1. `kubectl describe pod <pod> -n <ns>` -- look for `OOMKilled` in Last State, exit code 137
2. Check current memory limits: look at `resources.limits.memory` in the container spec
3. Check actual usage before kill: `kubectl top pod <pod> -n <ns>` (if the pod is running)
4. Review if limits are realistic for the workload
5. Check for memory leaks in application logs: `kubectl logs <pod> -n <ns> --previous`
6. Recommend: increase memory limits or fix the application memory usage

### ImagePullBackOff

Kubernetes cannot pull the container image.

1. `kubectl describe pod <pod> -n <ns>` -- check Events for the exact pull error
2. Verify the image name and tag exist: check for typos in the image reference
3. Check image pull secrets: `kubectl get pod <pod> -n <ns> -o jsonpath='{.spec.imagePullSecrets}'`
4. If using a private registry: verify the secret exists and contains valid credentials
   `kubectl get secret <secret-name> -n <ns> -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d`
5. Check if the node can reach the registry (network policies, firewall rules)
6. Check if the image tag is `latest` and the pull policy is `IfNotPresent` (stale cache issue)

### Networking / Service Issues

A service is not reachable, or pods cannot communicate.

1. Verify the service exists and has the correct selector:
   `kubectl get svc <service> -n <ns> -o wide`
2. Check that endpoints are populated:
   `kubectl get endpoints <service> -n <ns>`
   If endpoints are empty, the selector does not match any running pods.
3. Verify pod labels match the service selector:
   `kubectl get pods -n <ns> --show-labels`
4. Check if the target pods are Running and Ready:
   `kubectl get pods -n <ns> -l <selector>`
5. Test DNS resolution from within the cluster:
   `kubectl run dns-test --image=busybox:1.36 --rm -it --restart=Never -- nslookup <service>.<ns>.svc.cluster.local`
   (This creates a temporary pod -- requires approval.)
6. Check network policies that may be blocking traffic:
   `kubectl get networkpolicy -n <ns>`
7. Check if an ingress or gateway is involved:
   `kubectl get ingress -n <ns>`

## Guidelines

### General Principles

- **Explicit namespaces**: Always include `-n <namespace>` in commands. Never rely on implicit defaults after the initial context check.
- **Dry-run first**: For complex apply operations, suggest `--dry-run=client -o yaml` first so the user can review the manifest before applying.
- **One operation at a time**: Do not batch multiple state-changing operations. Execute each one individually with its own approval cycle.
- **Show before mutate**: Before any delete, scale, or update, show the current state of the affected resource so the user knows what will change.

### MCP Server Considerations

- MCP tools may use different parameter names than kubectl flags. Adapt the workflow to the tool's interface while maintaining the same safety checks.
- If the MCP server returns structured data (JSON), prefer it over CLI text output for accuracy.
- Apply the same approval requirements regardless of whether the operation is executed via MCP or CLI.

### What This Skill Does NOT Cover

- Cluster provisioning or teardown (use cloud-specific tools)
- Writing Helm charts, Kustomize overlays, or Kubernetes manifests from scratch
- Deep architecture decisions (delegate to the kubernetes-expert subagent)
- CI/CD pipeline configuration for Kubernetes deployments
