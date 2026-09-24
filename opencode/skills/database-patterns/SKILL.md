---
name: database-patterns
description: Database optimization patterns for modern performance tuning, query optimization, and scalable architectures. Covers advanced indexing, N+1 resolution, multi-tier caching, and partitioning strategies.
---

# Database Patterns

Database optimization patterns for modern performance tuning, query optimization, and scalable database architectures.

## Core Expertise

### Query Optimization
Execution plan analysis (EXPLAIN ANALYZE); query rewriting, window/recursive/CTE patterns; cross-database optimization (PG, MySQL, SQL Server, Oracle); NoSQL aggregation pipelines; cloud DB tuning (RDS, Aurora, Azure SQL).

### Indexing Strategies
B-tree, Hash, GiST, GIN, BRIN, covering indexes; composite/partial indexes; full-text, JSON/JSONB, spatial; index bloat management; cloud-native (Aurora, Azure SQL); MongoDB compound, DynamoDB GSI/LSI.

### Performance Monitoring
pg_stat_statements, MySQL Performance Schema, SQL Server DMVs; active query analysis, blocking detection; historical baselines; APM integration (Datadog, New Relic); automated regression detection.

### N+1 Query Resolution
ORM query analysis, eager loading, batch queries, JOIN optimization; Django ORM, SQLAlchemy, Entity Framework; GraphQL DataLoader batching; database-per-service, CQRS patterns.

### Caching Architectures
Multi-tier: L1 (app) -> L2 (Redis/Memcached) -> L3 (buffer pool); write-through/behind/aside/refresh-ahead; Redis Cluster, Memcached scaling; TTL strategies, event-driven invalidation, cache warming.

### Scaling & Partitioning
Horizontal: range/hash/list partitioning; vertical: column stores, archiving; sharding key design, app-level vs DB-level sharding; read replicas with load balancing; auto-scaling, serverless databases.

### Schema Design & Migration
Normalization vs denormalization trade-offs; zero-downtime migrations, large table strategies; schema versioning, CI/CD integration; data type and constraint optimization.

### Testing & Benchmarking
Load simulation (pgbench, sysbench, HammerDB); automated regression testing in CI/CD; capacity planning and resource forecasting.

### Cost Optimization
CPU/memory/I/O right-sizing; storage tiering, compression, archival; reserved capacity, spot instances, serverless; expensive query identification.

## Key Principles

- Measure first with profiling tools before optimizing
- Design indexes strategically based on query patterns
- Consider denormalization when justified by read patterns
- Implement comprehensive caching for expensive/frequent data
- Monitor slow query logs continuously for proactive optimization
- Value empirical evidence over theoretical optimizations
- Balance performance, maintainability, and cost
- Document optimization decisions with rationale and impact

## Response Approach

1. Analyze current performance via profiling/monitoring tools
2. Identify bottlenecks through systematic query, index, and resource analysis
3. Design optimization strategy for immediate and long-term goals
4. Implement with careful testing and performance validation
5. Set up monitoring for continuous tracking and regression detection
6. Validate improvements through comprehensive benchmarking
