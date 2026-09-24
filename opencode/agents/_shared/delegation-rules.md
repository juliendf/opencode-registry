---
name: Delegation Rules
description: Routing rules for skill loading vs subagent invocation
type: shared-config
mode: subagent
hidden: true
---

# Delegation Rules

When to load a **skill** (cheap, injected into current context) vs invoke a **subagent** (expensive, fresh context with tool access).

## Decision Rule

```
Need domain knowledge or reusable guidance?                 → skill(id="<skill-id>")
Need a child agent to execute independent tool work?         → subagent(agent="subagents/<agent-id>")
```

## Skill Loading (prefer this)

Skills provide knowledge: patterns, best practices, and reference material. Load them into current context; they do not spawn child sessions.

Load a skill when the user needs:
- Language expertise (Python, TypeScript, React, Go, Bash, SQL, Vue)
- Architecture patterns (API design, backend, microservices, GraphQL, cloud)
- Infrastructure knowledge (AWS, GCP, Azure, K8s, Terraform, SRE, etc.)
- Debugging, performance, testing guidance
- Code review patterns, security checklists
- Documentation writing, payment integration patterns

**Syntax:**
```
skill({"id": "python-pro"})
skill({"id": "kubernetes-patterns"})
skill({"id": "debugging-guide"})
```

## Subagent Invocation (when needed)

Subagents run autonomously with their own tools and permissions. Use when work BENEFITS from separate execution.

| Subagent | When to Invoke |
|----------|---------------|
| `subagents/infrastructure-engineer` | Running kubectl/terraform/helm/aws-cli, deployment, IaC implementation |
| `subagents/data-engineer` | Building Spark/Airflow/dbt pipelines and data transformations |
| `subagents/ml-engineer` | Training models and implementing PyTorch/TensorFlow |
| `subagents/mlops-engineer` | Kubeflow pipelines, model serving, ML infrastructure |
| `subagents/ai-engineer` | Building RAG systems, LLM apps, vector DB integration |
| `subagents/penetration-tester` | Running authorized security scans and exploit tooling |
| `subagents/security-auditor` | Running security scanners and compliance checks |
| `subagents/mobile-developer` | Xcode/Android Studio and mobile build chains |
| `subagents/cli-developer` | Building CLI tools and cross-compilation |
| `subagents/fullstack-developer` | Complex multi-layer implementation needing autonomous execution |

**Syntax:**
```
subagent({
  "agent": "subagents/infrastructure-engineer",
  "description": "Review staging deployment manifests",
  "prompt": "Inspect the manifests and report risks. Do not apply changes."
})
```

## No Research Tools as Substitute

Do not spawn a subagent merely to answer a knowledge question; load a relevant skill instead. Research tools remain valid for external facts and documentation.

Use a subagent only when separate execution or independent analysis adds value. Use webfetch, Context7, or web search directly when the task is research rather than execution.

## Parallel Execution

When multiple subagents or skills are needed simultaneously, invoke them in parallel (multiple calls in same message).
