# Agent Selection Guide

Quick reference for choosing the right agent. Start simple, escalate to specialists when needed.

## Quick Start

**New to the system?** Start here:

| What you want to do | Use this agent |
|---------------------|----------------|
| Just ask a question | `ask-me-anything` |
| Write some code | `build` |
| Fix a bug | `debug` |
| Plan a feature or architecture | `plan` |

## Primary Agent Workflow

Follow this progression for complex projects:

### 1. Planning Phase
```
Vague idea → plan → build
```

- **`plan`** — Turn ideas into functional specifications, then translate into technical system design
- **`build`** — Implement the actual solution

### 2. Development Phase
```
Implementation → review → debug (if issues)
```

- **`build`** — Write features, APIs, frontend code
- **`review`** — Code quality, security, and test coverage review (auto-invoked for high-stakes)
- **`debug`** — Investigate and fix issues end-to-end

### 3. Infrastructure Phase
```
Code ready → V2 subagent → deployment
```

- **`subagents/infrastructure-engineer`** — CI/CD, Kubernetes, cloud infrastructure. Invoke through the V2 `subagent` tool when independent execution is needed.
- Handles Terraform, Docker, AWS/GCP/Azure deployment

## When to Use Each Agent

### Primary Agents

| Agent | Use When | Don't Use When |
|-------|----------|----------------|
| **ask-me-anything** | Questions about code, concepts, docs | You need to modify files |
| **plan** | Need specs, architecture, or system design | You need actual implementation |
| **build** | Implement features, write code | Infrastructure or deployment needs |
| **review** | Code quality check, security audit | You need fixes implemented (it only reviews) |
| **debug** | Something's broken, need diagnosis + fix | Simple questions (use ask-me-anything) |

### Specialist Subagents

Invoke these through V2 `subagent` when independent tool execution needs its own context. IDs include the `subagents/` path prefix.

| Subagent | When to Invoke |
|----------|---------------|
| **subagents/infrastructure-engineer** | Kubernetes, Terraform, CI/CD, cloud deployment |
| **subagents/data-engineer** | Spark, Airflow, dbt, data pipelines |
| **subagents/ml-engineer** | PyTorch, TensorFlow, model training |
| **subagents/mlops-engineer** | Kubeflow, MLflow, model serving |
| **subagents/ai-engineer** | RAG, LLM apps, vector databases |
| **subagents/penetration-tester** | Authorized security scanning and vulnerability assessment |
| **subagents/security-auditor** | Compliance checks, security audits |
| **subagents/mobile-developer** | React Native, Flutter, iOS/Android |
| **subagents/cli-developer** | CLI tool building, cross-compilation |
| **subagents/fullstack-developer** | Complex multi-layer features |

### Skills

Skills inject knowledge and workflows into the current context. Load a skill with V2 `skill` and its exact ID, for example `skill` input `{"id":"python-pro"}`. No child-session overhead.

**Language expertise:** python-pro, typescript-pro, react-specialist, vue-expert, golang-pro, sql-pro, bash-expert

**Architecture patterns:** api-designer, backend-architect, graphql-architect, microservices-architect, cloud-architect

**Infrastructure patterns:** aws-patterns, gcp-patterns, azure-patterns, terraform-patterns, kubernetes-patterns, sre-patterns, observability-patterns, network-patterns, gitops-patterns, platform-patterns, crossplane-patterns, devops-patterns

**Quality & security:** debugging-guide, performance-engineering, test-automation

**Workflows:** mcp-builder, project-docs, content-research-writer, proofreader, second-opinion

> **Note:** Skills are loaded by you or by primary agents when domain expertise is needed. They don't spawn new context — they infuse knowledge into the current session.

## Common Usage Patterns

### New Feature Development
```
1. plan: "I want users to track their orders" → functional spec + architecture
2. build: [receives architecture] → implementation
3. review: [auto-invoked for security-sensitive code]
```

### Bug Investigation
```
1. debug: "API returns 500 when creating users"
   → Loads debugging-guide skill, investigates, finds root cause, implements fix
```

### Infrastructure Setup
```
1. build: calls V2 `subagent` with `agent: "subagents/infrastructure-engineer"`
   → Creates Kubernetes manifests, Terraform, CI/CD pipeline
```

### Language-Specific Work
```
1. build: calls V2 `skill` with `id: "python-pro"`
   → Codes with Python best practices, modern patterns, type safety
```

## Agent Handoffs

Agents naturally hand off to each other:

```
plan → build
"Next step: build can implement this design"

build → review (automatic for high-stakes)
[Auto-invokes for auth, security, payments, migrations]

build → `subagents/infrastructure-engineer` (via V2 `subagent`)
"Deploy to Kubernetes using infrastructure-engineer"

Any agent → ask-me-anything
"Use ask-me-anything to research best practices"
```

## Tips for Better Results

### 1. Start Broad, Get Specific
- No: "Fix line 42 in auth.js"
- Yes: "Users can't log in, getting 401 errors"

### 2. Provide Context
- Include error messages, stack traces, recent changes
- Mention constraints (timeline, technology requirements)
- Share what you've already tried

### 3. Use Progressive Refinement
- Start with `plan` for unclear requirements
- Let agents hand off naturally through the workflow
- Don't skip planning phases for complex features

### 4. Skill Before Subagent
- Load a skill when you need domain knowledge (language patterns, architecture)
- Invoke a subagent when you need autonomous tool execution (deploy, scan, train)

---

## Need Help?

- **Unclear which agent to use?** Start with `ask-me-anything`
- **Agent not doing what you expect?** Check if you're using the right one
- **Multiple agents needed?** Follow the progression: plan → build → review

Remember: Agents work best when you describe **what you want to achieve**, not **how to achieve it**.
