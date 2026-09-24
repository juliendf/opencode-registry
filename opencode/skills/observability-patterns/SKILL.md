---
name: observability-patterns
description: Observability patterns for distributed systems. Covers metrics, logging, tracing (OpenTelemetry), and alerting for cloud-native applications.
---

# Observability Patterns

Monitoring, logging, and distributed tracing patterns for cloud-native systems. Covers the three pillars of observability -- metrics, logs, traces -- using OpenTelemetry, Prometheus, Grafana, and modern observability platforms.

## Core Expertise

### OpenTelemetry & Tracing
- OTel SDK integration (auto and manual instrumentation) across Go, Python, Java, Node.js
- OTel Collector: pipeline configuration, processors, exporters (Jaeger, Tempo, Zipkin, OTLP)
- Trace context propagation, span attribute enrichment, sampling strategies (head/tail/adaptive)
- Trace-to-logs correlation, service dependency mapping, trace analysis for debugging

### Metrics Engineering
- Prometheus: counter/gauge/histogram design, PromQL optimization, recording rules, federation
- Metric cardinality management, remote write, SLI/SLO metric definitions
- Kubernetes observability: kube-state-metrics, cAdvisor, node-exporter, custom metrics
- Cloud provider metrics integration (CloudWatch, Azure Monitor, Cloud Monitoring)

### Logging Infrastructure
- Structured logging best practices: JSON format, correlation IDs, log levels
- Log aggregation: Loki, ELK/OpenSearch, CloudWatch Logs, Datadog
- Log parsing, enrichment, retention policies, cost optimization
- Log-based alerting and log-to-trace correlation

### Alerting & Dashboards
- Alert design: symptom-based over cause-based, fatigue reduction, deduplication
- Multi-window SLO alerting (burn rate), escalation policies, runbook integration
- Grafana: dashboard as code (Jsonnet/Grafonnet), effective visualization, dashboard standards
- PagerDuty/OpsGenie integration, alert testing and validation

## Workflow

1. **Map**: Identify services, dependencies, and critical user journeys
2. **Instrument**: Add OTel SDK, define SLI metrics, implement structured logging
3. **Collect**: Deploy OTel Collector pipelines, configure Prometheus scraping
4. **Visualize**: Build dashboards for operations, SREs, and executives; set up SLO alerting
5. **Iterate**: Refine signals after incidents; optimize costs; improve runbooks

## Key Principles

1. **Signal quality over quantity**: Fewer, high-quality signals beat dashboards nobody reads
2. **SLO-driven alerting**: Alert on symptoms (user impact) not causes (CPU spikes)
3. **Cost-conscious**: Cardinality, sampling, and retention policies are first-class concerns
4. **Correlate signals**: Traces linked to logs, logs linked to metrics enables fast debugging
5. **Observability as code**: Dashboards, alerts, and recording rules version-controlled in Git
6. **Test observability**: Verify signals fire correctly during chaos/load tests

## Example: OTel Collector Pipeline + Prometheus Alert

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
  prometheus:
    config:
      scrape_configs:
      - job_name: 'app'
        static_configs:
        - targets: ['app:8080']

processors:
  batch:
    timeout: 10s
  memory_limiter:
    limit_mib: 512
  resource:
    attributes:
    - key: service.environment
      value: production
      action: upsert

exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
  prometheusremotewrite:
    endpoint: "http://mimir:9009/api/v1/push"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, resource]
      exporters: [otlp/tempo]
    metrics:
      receivers: [prometheus]
      processors: [batch]
      exporters: [prometheusremotewrite]
---
# Prometheus alert rule
groups:
- name: api-latency
  rules:
  - alert: HighP99Latency
    expr: histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)) > 1.0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "P99 latency > 1s for {{ $labels.service }}"
      runbook: "https://wiki/runbooks/high-latency"
```
