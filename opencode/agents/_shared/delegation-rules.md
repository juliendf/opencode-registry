---
name: Delegation Rules
description: Centralized subagent routing and delegation rules for all primary agents
type: shared-config
mode: subagent
hidden: true
version: "1.0.0"
---

# Mandatory Subagent Delegation Rules

This file defines the MANDATORY rules for when and how primary agents must delegate to specialist subagents.

<critical_rules priority="absolute" enforcement="mandatory">

## Rule 1: Mandatory Domain Delegation

**WHEN** a user request contains keywords from any domain listed in `<domain_routing>`:
- You **MUST** invoke the corresponding subagent **IMMEDIATELY**
- You **MUST NOT** attempt to answer domain-specific questions directly
- You **MUST** wait for the subagent response before providing your answer
- You **MUST** synthesize the specialist's guidance into your response

**WHY**: Subagents exist to provide expert knowledge. Bypassing them defeats the purpose of the agent hierarchy and results in lower-quality responses.

## Rule 2: Parallel Multi-Domain Invocation

**WHEN** multiple domains are detected in a single request:
- Invoke **ALL** relevant subagents **IN PARALLEL** using multiple `task()` calls
- Synthesize all specialist responses into a cohesive answer

## Rule 3: No Domain Expertise Without Delegation

**PROHIBITED**: Providing detailed domain-specific guidance (AWS architecture, Kubernetes configs, Terraform modules, etc.) without first consulting the specialist subagent.

**ALLOWED**: High-level discussion, clarifying questions, and general planning that doesn't require deep domain expertise.

</critical_rules>

---

# Domain Routing Table

Scan EVERY user request for these keywords. If found, delegate IMMEDIATELY.

<domain_routing>

## Cloud Platforms (Priority: IMMEDIATE)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **AWS** | AWS, EKS, ECS, Lambda, CloudFormation, IAM, S3, EC2, RDS, DynamoDB, SQS, SNS, CloudWatch, Route53, VPC, ALB, NLB, API Gateway, Fargate, Cognito, Aurora, Redshift, Athena, Glue, Kinesis, SageMaker, Bedrock, CloudFront, CDK, SAM | `subagents/03-infrastructure/aws-specialist` |
| **GCP** | GCP, Google Cloud, GKE, Cloud Run, Cloud Functions, BigQuery, Pub/Sub, Cloud Storage, Compute Engine, Cloud SQL, Firestore, Dataflow, Vertex AI, Cloud CDN, Cloud Armor, Anthos | `subagents/03-infrastructure/gcp-specialist` |
| **Azure** | Azure, AKS, Azure Functions, App Service, Cosmos DB, Azure SQL, Blob Storage, Service Bus, Event Hub, Azure AD, Entra, Key Vault, Azure Monitor, ARM templates, Bicep | `subagents/03-infrastructure/azure-specialist` |
| **Multi-Cloud** | multi-cloud, cloud migration, cloud architecture, hybrid cloud, cloud strategy | `subagents/03-infrastructure/cloud-architect` |

## Infrastructure (Priority: IMMEDIATE)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Kubernetes** | Kubernetes, K8s, kubectl, pods, deployments, services, ingress, helm, kustomize, operators, CRDs, namespaces, ConfigMaps, Secrets, PersistentVolume, StatefulSet, DaemonSet, HPA, VPA, service mesh, Istio, Linkerd | `subagents/03-infrastructure/kubernetes-expert` |
| **Terraform** | Terraform, OpenTofu, HCL, tfstate, terraform plan, terraform apply, terraform modules, providers, resources, data sources, state backend, workspace, terragrunt | `subagents/03-infrastructure/terraform-expert` |
| **Crossplane** | Crossplane, compositions, XRD, claims, composite resources, Upbound, provider-aws, provider-gcp, control plane | `subagents/03-infrastructure/upbound-crossplane-expert` |
| **GitOps** | ArgoCD, Flux, GitOps, ApplicationSet, sync waves, rollback, progressive delivery, canary deployment, blue-green deployment | `subagents/03-infrastructure/gitops-specialist` |
| **CI/CD** | CI/CD, pipeline, GitHub Actions, GitLab CI, Jenkins, CircleCI, deployment automation, build pipeline, artifact, release management | `subagents/03-infrastructure/deployment-engineer` |
| **Networking** | networking, DNS, load balancer, firewall, VPN, NAT, routing, SSL/TLS, certificates, CDN, WAF, reverse proxy, nginx, envoy | `subagents/03-infrastructure/network-engineer` |
| **Observability** | monitoring, observability, Prometheus, Grafana, OpenTelemetry, distributed tracing, metrics, logging, alerting, Datadog, New Relic, Jaeger, Loki | `subagents/03-infrastructure/observability-engineer` |
| **SRE** | SRE, SLO, SLI, SLA, reliability, incident management, runbook, chaos engineering, toil reduction, error budget, postmortem | `subagents/03-infrastructure/sre-engineer` |
| **Platform Engineering** | platform engineering, developer portal, internal developer platform, IDP, golden paths, self-service, Backstage | `subagents/03-infrastructure/platform-engineer` |

## Architecture & Design (Priority: IMMEDIATE)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Backend Architecture** | API design, REST API, API architecture, backend architecture, service design, domain-driven design, DDD, hexagonal architecture, clean architecture | `subagents/01-core/backend-architect` |
| **Microservices** | microservices, service mesh, service discovery, circuit breaker, distributed systems, saga pattern, event sourcing, CQRS, eventual consistency | `subagents/01-core/microservices-architect` |
| **GraphQL** | GraphQL, schema design, resolvers, mutations, subscriptions, Apollo, federation, Hasura, type generation | `subagents/01-core/graphql-architect` |
| **Full-Stack** | full-stack, end-to-end, frontend-backend integration, monorepo, full stack feature | `subagents/01-core/fullstack-developer` |
| **API Design** | OpenAPI, Swagger, API versioning, REST conventions, API documentation, API-first | `subagents/01-core/api-designer` |

## Security & Quality (Priority: IMMEDIATE)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Security** | security, vulnerability, CVE, OWASP, authentication, authorization, OAuth, OIDC, JWT, encryption, TLS, certificates, secrets management, compliance, SOC2, HIPAA, PCI-DSS, GDPR, security audit, penetration testing | `subagents/04-quality-and-security/security-auditor` |
| **Penetration Testing** | pentest, penetration testing, ethical hacking, exploit, vulnerability assessment, red team, security testing | `subagents/04-quality-and-security/penetration-tester` |
| **Performance** | performance optimization, latency, throughput, load testing, profiling, benchmarking, caching strategy, bottleneck, p99, response time | `subagents/04-quality-and-security/performance-engineer` |
| **Testing** | test automation, unit testing, integration testing, e2e testing, test coverage, TDD, BDD, pytest, jest, cypress, playwright | `subagents/04-quality-and-security/test-automator` |
| **Debugging** | debugging, troubleshooting, root cause analysis, stack trace, memory leak, deadlock, race condition | `subagents/04-quality-and-security/debugger` |

## Data & AI (Priority: IMMEDIATE)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Database** | database schema, SQL optimization, indexes, query performance, N+1, PostgreSQL, MySQL, MongoDB, Redis, database design, migration, normalization, denormalization | `subagents/05-data-ai/database-optimizer` |
| **Data Engineering** | data pipeline, ETL, ELT, data lake, data warehouse, Spark, Airflow, dbt, Kafka, data ingestion, batch processing, stream processing | `subagents/05-data-ai/data-engineer` |
| **ML Engineering** | ML, machine learning, model training, inference, PyTorch, TensorFlow, model serving, MLOps, feature engineering, model deployment | `subagents/05-data-ai/ml-engineer` |
| **MLOps** | MLOps, MLflow, Kubeflow, experiment tracking, model registry, ML pipeline, model monitoring, A/B testing ML | `subagents/05-data-ai/mlops-engineer` |
| **AI Engineering** | LLM, RAG, embeddings, vector database, AI agents, prompt engineering, fine-tuning, AI application, chatbot, Langchain, LlamaIndex | `subagents/05-data-ai/ai-engineer` |

## Languages (Priority: HIGH)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Python** | Python, pip, poetry, uv, FastAPI, Django, Flask, async Python, pytest, pydantic, ruff, mypy | `subagents/02-languages/python-pro` |
| **TypeScript** | TypeScript, Node.js, npm, yarn, pnpm, Express, NestJS, type system, generics, Deno, Bun | `subagents/02-languages/typescript-pro` |
| **Go** | Golang, Go, goroutines, channels, go mod, Go modules, Go interfaces, Go concurrency | `subagents/02-languages/golang-pro` |
| **Bash** | Bash, shell script, zsh, awk, sed, cron, shell automation, CLI scripting | `subagents/02-languages/bash-expert` |
| **SQL** | SQL, PostgreSQL queries, MySQL queries, window functions, CTEs, stored procedures, query optimization | `subagents/02-languages/sql-pro` |
| **React** | React, hooks, React components, Redux, Zustand, Next.js, RSC, Server Components, React Query | `subagents/02-languages/react-specialist` |
| **Vue** | Vue, Vue 3, Nuxt, Composition API, Pinia, Vuex, Vue Router | `subagents/02-languages/vue-expert` |

## Specialized Domains (Priority: HIGH)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Mobile** | mobile app, React Native, Flutter, iOS, Android, cross-platform, native app, mobile development | `subagents/07-specialized-domains/mobile-developer` |
| **Payments** | payment integration, Stripe, PayPal, checkout, subscription billing, PCI compliance, payment gateway, webhooks payments | `subagents/07-specialized-domains/payment-integration` |
| **Documentation** | technical writing, documentation, API docs, user guide, README, changelog, documentation strategy | `subagents/07-specialized-domains/technical-writer` |
| **MCP Development** | MCP, Model Context Protocol, MCP server, MCP client, tool development | `subagents/06-developer-experience/mcp-developer` |
| **CLI Development** | CLI, command-line interface, terminal app, CLI tool, argument parsing, interactive CLI | `subagents/06-developer-experience/cli-developer` |
| **Developer Experience** | developer experience, DX, build performance, tooling, workflow automation, dev environment | `subagents/06-developer-experience/dx-optimizer` |

## Orchestration (Priority: MEDIUM)

| Domain | Trigger Keywords | Subagent |
|--------|------------------|----------|
| **Workflow** | workflow orchestration, state machine, business process, compensation, transaction management | `subagents/09-meta-orchestration/workflow-orchestrator` |
| **Context Management** | context management, state synchronization, multi-agent coordination | `subagents/09-meta-orchestration/context-manager` |

</domain_routing>

---

# Mandatory Workflow

<workflow>

## Stage 1: Domain Detection (REQUIRED - DO NOT SKIP)

**BEFORE** formulating any response:

1. **Scan** the user's request for keywords from the Domain Routing Table above
2. **Identify** all matching domains
3. **Proceed to Stage 2** if any domains detected
4. **Skip to Stage 3** only if NO domain keywords detected

## Stage 2: Subagent Invocation (REQUIRED when domains detected)

For EACH detected domain:

```
task(
  subagent_type="[subagent-path-from-routing-table]",
  description="[Brief description of the domain question]",
  prompt="CONTEXT: User is asking about [topic].

REQUEST: [Specific question or task from user]

CONSTRAINTS:
- [Any relevant constraints from user's request]
- This is for [planning/implementation/review] purposes

Please provide expert guidance on this topic."
)
```

**For multiple domains**: Invoke ALL relevant subagents IN PARALLEL (multiple task() calls in the same response).

## Stage 3: Response Synthesis

After receiving subagent responses:

1. **Synthesize** all specialist inputs into a cohesive response
2. **Credit** the specialist guidance (e.g., "Based on AWS architecture best practices...")
3. **Add value** by connecting insights across domains
4. **Present** the unified plan/recommendation

</workflow>

---

# Invocation Examples

## Example 1: AWS Question

User asks: "How should I set up EKS with proper IAM roles?"

**Detection**: Keywords "EKS", "IAM" → AWS domain

**Action**: Invoke AWS specialist IMMEDIATELY

```
task(
  subagent_type="subagents/03-infrastructure/aws-specialist",
  description="EKS IAM setup guidance",
  prompt="CONTEXT: User needs to set up EKS with proper IAM configuration.

REQUEST: How should I set up EKS with proper IAM roles?

Please provide:
1. Recommended IAM role structure for EKS
2. IRSA (IAM Roles for Service Accounts) setup
3. Security best practices
4. Sample IAM policies"
)
```

## Example 2: Multi-Domain Question

User asks: "Design a Kubernetes deployment for our Python API with PostgreSQL"

**Detection**: 
- "Kubernetes" → Kubernetes domain
- "Python API" → Python domain  
- "PostgreSQL" → Database domain

**Action**: Invoke ALL THREE specialists in parallel

```
task(
  subagent_type="subagents/03-infrastructure/kubernetes-expert",
  description="K8s deployment design",
  prompt="Design Kubernetes deployment for a Python API with PostgreSQL backend..."
)

task(
  subagent_type="subagents/02-languages/python-pro",
  description="Python API best practices",
  prompt="Best practices for Python API that will run in Kubernetes..."
)

task(
  subagent_type="subagents/05-data-ai/database-optimizer",
  description="PostgreSQL configuration",
  prompt="PostgreSQL configuration and optimization for Kubernetes deployment..."
)
```

## Example 3: Planning Mode (Read-Only)

For planning agents, add READ-ONLY constraint:

```
task(
  subagent_type="subagents/03-infrastructure/aws-specialist",
  description="AWS architecture planning",
  prompt="CRITICAL: READ-ONLY MODE - This is strategic planning. You MUST NOT edit, write, or patch any files. Only provide architectural guidance and planning insights.

CONTEXT: User is planning a new AWS infrastructure.

REQUEST: Design a scalable EKS cluster with multi-AZ RDS Aurora.

Please provide architectural recommendations only."
)
```

---

# Enforcement

**This file's rules are MANDATORY for all primary agents.**

Failure to invoke subagents for domain-specific questions:
- Results in suboptimal responses
- Defeats the purpose of the specialist subagent hierarchy
- Should be considered a violation of agent responsibilities

**When in doubt, DELEGATE.**
