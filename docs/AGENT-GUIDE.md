# Agent Selection Guide

Quick reference for choosing the right agent for your task. Start simple and escalate to specialists when needed.

## 🚀 Quick Start

**New to the system?** Start here:

| What you want to do | Use this agent |
|---------------------|----------------|
| Just ask a question | `ask-me-anything` |
| Write some code | `build-code` |
| Fix a bug | `debug` |
| Plan a new feature | `plan-design` |

## 📋 Primary Agent Workflow

Follow this progression for complex projects:

### 1. **Planning Phase**

```text
Vague idea → plan-design → plan-architecture → build-code
```

- **`plan-design`** — Turn ideas into functional specifications (non-technical)
- **`plan-architecture`** — Convert specs into technical system design
- **`build-code`** — Implement the actual solution

### 2. **Development Phase**

```text
Implementation → review → debug (if issues)
```

- **`build-code`** — Write features, APIs, frontend code
- **`review`** — Code quality and security review (auto-invoked for high-stakes)
- **`debug`** — Investigate and fix issues end-to-end

### 3. **Infrastructure Phase**

```text
Code ready → build-infrastructure → deployment
```

- **`build-infrastructure`** — CI/CD, Kubernetes, cloud infrastructure
- Handles Terraform, Docker, AWS/GCP/Azure deployment

## 🎯 When to Use Each Agent

### Primary Agents

| Agent | Use When | Don't Use When |
|-------|----------|----------------|
| **ask-me-anything** | Questions about code, concepts, docs | You need to modify files |
| **plan-design** | Vague requirements, need user stories | You already have a clear spec |
| **plan-architecture** | Have functional spec, need tech design | You need actual implementation |
| **build-code** | Implement features, write code | Infrastructure or deployment needs |
| **review** | Code quality check, security audit | You need fixes implemented (it only reviews) |
| **debug** | Something's broken, need diagnosis + fix | Simple questions (use ask-me-anything) |
| **build-infrastructure** | Kubernetes, CI/CD, cloud deployment | Application code (use build-code) |

### Specialist Subagents (Auto-Delegated)

Primary agents automatically invoke these when domain keywords are detected:

| Category | Specialists | Auto-triggered by keywords |
|----------|-------------|---------------------------|
| **Core Architecture** | backend-architect, microservices-architect, api-designer, graphql-architect, fullstack-developer | API, microservices, architecture, GraphQL |
| **Languages** | python-pro, typescript-pro, golang-pro, java-pro, dotnet-pro, bash-expert, sql-pro, react-specialist, vue-expert | Language names, frameworks |
| **Infrastructure** | aws-specialist, azure-specialist, gcp-specialist, cloud-architect, kubernetes-expert, terraform-expert, upbound-crossplane-expert, deployment-engineer, gitops-specialist, network-engineer, observability-engineer, platform-engineer, sre-engineer | Cloud platforms, K8s, IaC, CI/CD, networking |
| **Quality & Security** | security-auditor, penetration-tester, performance-engineer, test-automator, debugger | Security, performance, testing, debugging |
| **Data & AI** | database-optimizer, data-engineer, ai-engineer, ml-engineer, mlops-engineer | Database, ML, data pipelines, AI |
| **Developer Experience** | cli-developer, dx-optimizer, mcp-developer | CLI tools, DX, MCP servers |
| **Specialized Domains** | mobile-developer, payment-integration, reverse-engineer, technical-writer | Mobile, payments, reverse engineering, docs |
| **Meta-Orchestration** | context-manager, workflow-orchestrator | Workflow automation, context management |

> **Note:** You rarely invoke subagents directly. Primary agents handle delegation automatically based on your request's keywords.

## 🛤️ Common Usage Patterns

### New Feature Development

```text
1. plan-design: "I want users to track their orders"
2. plan-architecture: [receives functional spec] → technical design
3. build-code: [receives architecture] → implementation
4. review: [auto-invoked for security-sensitive code]
```

### Bug Investigation

```text
1. debug: "API returns 500 when creating users"
   → Investigates, finds root cause, implements fix
```

### Infrastructure Setup

```text
1. build-infrastructure: "Deploy Node.js app to GKE with monitoring"
   → Creates Kubernetes manifests, Terraform, CI/CD
```

### Quick Questions

```text
1. ask-me-anything: "How does JWT work in our codebase?"
   → Searches code, explains implementation
```

## 🔄 Agent Handoffs

Agents naturally hand off to each other:

```text
plan-design → plan-architecture
"Next step: Switch to plan-architecture for technical design"

plan-architecture → build-code  
"Ready for build-code to implement this design"

build-code → review (automatic for high-stakes)
[Auto-invokes for auth, security, payments, migrations]

Any agent → ask-me-anything
"Use ask-me-anything to research best practices for..."
```

## 🚨 When NOT to Use Agents

**Don't use agents for:**

- Simple file edits you can do faster manually
- Reading a single file (use your editor)
- Trivial questions easily googled

**Do use agents for:**

- Multi-file changes
- Complex debugging across components  
- Architecture decisions
- Code that needs review
- Infrastructure automation

## 💡 Tips for Better Results

### 1. **Start Broad, Get Specific**

- ❌ "Fix line 42 in auth.js"
- ✅ "Users can't log in, getting 401 errors"

### 2. **Provide Context**

- Include error messages, stack traces, recent changes
- Mention constraints (timeline, technology requirements)
- Share what you've already tried

### 3. **Use Progressive Refinement**

- Start with plan-design for unclear requirements
- Let agents hand off naturally through the workflow
- Don't skip planning phases for complex features

### 4. **Trust the Delegation**

- Primary agents know when to call specialists
- Include relevant keywords in your requests
- Don't manually specify subagents (they auto-route)

## 🔧 Advanced Patterns

### Multi-Domain Projects

For projects touching multiple areas:

```text
User: "Build a React app with Node.js API and PostgreSQL, deployed to AWS"

build-code will auto-delegate to:
- react-specialist (frontend)
- typescript-pro (Node.js API) 
- database-optimizer (PostgreSQL design)
- aws-specialist (deployment architecture)
```

### Iterative Development

```text
1. plan-design: MVP feature spec
2. build-code: Basic implementation  
3. review: Security check
4. plan-design: Extended features
5. build-code: Enhanced version
```

### Debugging Complex Issues

```text
1. debug: Initial investigation
   → May delegate to performance-engineer, database-optimizer, etc.
   → Returns with root cause + fix
```

---

## Need Help?

- **Unclear which agent to use?** Start with `ask-me-anything`
- **Agent not doing what you expect?** Check if you're using the right one for your goal
- **Multiple agents suggested?** Follow the progression: design → architecture → build → review

Remember: Agents work best when you describe **what you want to achieve**, not **how to achieve it**. Let them figure out the approach and delegate to specialists automatically.
