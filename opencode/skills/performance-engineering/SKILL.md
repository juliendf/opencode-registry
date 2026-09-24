---
name: performance-engineering
description: Performance engineering patterns for system optimization, bottleneck identification, and scalability. Covers performance testing, profiling, and tuning across applications, databases, and infrastructure.
---

# Performance Engineering

Performance engineering driven by measurement, not assumptions. Application profiling, load testing, database tuning, infrastructure configuration — always with quantified before/after metrics.

## Core Expertise

### Performance Testing
- Load/stress testing: Locust, k6, JMeter, Gatling; ramp-up, soak, spike patterns
- Baseline & regression: Establish SLA baselines; detect regressions in CI/CD
- Profiling: CPU hotspots, memory allocation, GC pressure, thread contention
- Real user monitoring: APM (Datadog, New Relic), p50/p95/p99 latency tracking

### Bottleneck Analysis
- Application: N+1 queries, synchronous blocking, inefficient algorithms, object churn
- Database: Slow query analysis, missing indexes, execution plans, connection pool exhaustion
- Infrastructure: CPU scheduling, memory pressure, I/O wait, network latency, container limits
- Caching: Redis/Memcached hit rates, invalidation storms, CDN offload efficiency

### Scalability Engineering
- Horizontal/vertical scaling with auto-scaling policies and load balancer tuning
- Async processing: queue-based decoupling, batch operations, event-driven architectures
- Capacity planning: growth projections, cost-aware forecasting, performance budgets
- Microservices: service mesh latency, inter-service timeout/retry tuning, circuit breakers

### Optimization Techniques
- Code: Algorithm complexity reduction, lazy loading, connection/resource pooling
- Database: Query rewriting, index design, read replicas, partitioning
- Network: gzip/brotli compression, HTTP/2 multiplexing, keep-alive, payload minimization
- Infrastructure: Kernel tuning, storage I/O optimization, instance right-sizing

## Workflow

1. **Baseline & Profile**: Measure current state under realistic load; capture p95/p99 latencies
2. **Identify Bottlenecks**: Profile app, analyze slow queries, check infrastructure — find the biggest constraint
3. **Optimize & Validate**: Implement targeted fix, re-run load test, confirm with before/after metrics
4. **Monitor & Iterate**: Add dashboards/alerts, track trends, plan next optimization cycle

## Key Principles

1. **Measure first** — gut feelings are hypotheses, not facts
2. **Fix the bottleneck** — optimizing non-bottlenecks yields no improvement
3. **Test under realistic load** — synthetic load must reflect actual patterns and data volumes
4. **Quantify impact** — every optimization shows before/after latency, throughput, resource usage
5. **Consider trade-offs** — caching improves speed but adds consistency complexity
6. **Embed in CI/CD** — performance regression tests should fail the pipeline
7. **Capacity plan proactively** — model growth ahead of demand

## Key Examples

### Load Test with Staged Ramp-Up (Locust)
```python
from locust import HttpUser, task, between, LoadTestShape

class APIUser(HttpUser):
    wait_time = between(1, 3)
    def on_start(self):
        resp = self.client.post("/auth/token", json={"username": "test_user", "password": "test_pass"})
        self.token = resp.json()["access_token"]

    @task(3)
    def get_products(self):
        self.client.get("/api/products", headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def create_order(self):
        self.client.post("/api/orders", json={"product_id": 42, "quantity": 1},
                         headers={"Authorization": f"Bearer {self.token}"})

class StagesShape(LoadTestShape):
    stages = [
        {"duration": 60, "users": 50, "spawn_rate": 5},
        {"duration": 180, "users": 200, "spawn_rate": 10},
        {"duration": 240, "users": 500, "spawn_rate": 50},
    ]
    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
# Key metrics: p50/p95/p99 latency, RPS, error rate, CPU/mem during test
```

### N+1 Query Fix
```python
# BAD: 1 query for orders + N queries for users
orders = db.query(Order).all()
results = [{"id": o.id, "user": db.query(User).get(o.user_id).name} for o in orders]

# GOOD: single JOIN with eager loading
from sqlalchemy.orm import joinedload
orders = db.query(Order).options(joinedload(Order.user)).all()
results = [{"id": o.id, "user": o.user.name} for o in orders]

# Missing index fix:
# CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
# Verify: EXPLAIN ANALYZE — look for Index Scan vs Seq Scan, actual rows
```
