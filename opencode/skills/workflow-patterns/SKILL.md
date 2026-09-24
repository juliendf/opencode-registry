---
name: workflow-patterns
description: Workflow orchestration patterns for complex process design, state machine implementation, and business process automation. Covers saga patterns, error compensation, and transaction management.
---

# Workflow Patterns

Workflow orchestration patterns for designing reliable, maintainable business processes with graceful failure recovery.

## Core Expertise

### Workflow Design & State Machines
- Process modeling: sequential, parallel split/join, exclusive choice, event-based gateways
- State definitions, transition rules, decision logic, loop constructs
- Compensation flows and rollback procedures for long-running transactions
- Sub-process decomposition and reusable process fragments

### Transaction Management & Saga Patterns
- Saga choreography vs. orchestration trade-offs
- Compensation transactions per step (forward vs. backward recovery)
- Idempotency guarantees across distributed steps; exactly-once semantics
- Two-phase commit alternatives for distributed systems

### Error Handling & Recovery
- Exception boundaries, exponential backoff retry, circuit breakers
- Dead letter queues for unrecoverable failures with alerting
- Timeout management and SLA-driven escalation
- Checkpoint/restart: resume from last successful step

### Observability & Human Tasks
- Process metrics: throughput, p95/p99 duration, success/failure per step
- Audit trails with complete state history; KPI dashboards
- Human approval workflows with assignment, escalation, delegation
- Bottleneck detection via process mining and step-level latency analysis

## Workflow

1. **Map the process**: Identify states, transitions, decision points, integrations, failure scenarios
2. **Design compensation**: Define compensation for every mutating step — model happy path and failure path together
3. **Instrument from start**: Track state transitions, durations, errors from first implementation
4. **Test failure scenarios**: Simulate network failures, timeouts, partial completions

## Key Principles

1. **Model failures explicitly** — every failable step needs defined compensation/escalation
2. **Idempotency is required** — all steps must be safely retryable
3. **Prefer choreography for simple flows** — reduces coupling vs orchestration
4. **Observe everything** — un-instrumented workflows are black boxes
5. **Version workflows carefully** — running instances complete on original version
6. **Keep steps atomic** — one thing per step to simplify compensation
7. **Human tasks need SLAs** — approval workflows without escalation block indefinitely

## Examples

### Saga Pattern with Compensation
```typescript
interface SagaStep<T> {
  name: string
  execute: (ctx: T) => Promise<void>
  compensate: (ctx: T) => Promise<void>
}

async function runSaga<T>(steps: SagaStep<T>[], context: T): Promise<void> {
  const completed: SagaStep<T>[] = []
  for (const step of steps) {
    try {
      await step.execute(context)
      completed.push(step)
    } catch (err) {
      for (const done of [...completed].reverse()) {
        try { await done.compensate(context) }
        catch (e) { /* log + alert — manual intervention needed */ }
      }
      throw err
    }
  }
}
// Usage: each step defines execute() and compensate() for rollback
```

### State Machine with Typed Transitions
```typescript
type Status = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'

const transitions: Record<Status, Status[]> = {
  pending:   ['confirmed', 'cancelled'],
  confirmed: ['shipped',   'cancelled'],
  shipped:   ['delivered'],
  delivered: [], cancelled: [],
}

class StateMachine {
  constructor(private state: Status = 'pending') {}

  transition(next: Status): void {
    if (!transitions[this.state].includes(next))
      throw new Error(`Invalid: ${this.state} -> ${next}`)
    this.state = next
  }
  get current(): Status { return this.state }
}
```
