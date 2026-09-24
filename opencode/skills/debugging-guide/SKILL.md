---
name: debugging-guide
description: Systematic debugging patterns for complex issue diagnosis, root cause analysis, and problem-solving across multiple languages and environments.
---

# Debugging Guide

Systematic debugging patterns for diagnosing complex software issues. Apply evidence-driven techniques — log analysis, stack traces, profiling, distributed tracing — to find root causes efficiently.

## Core Expertise

### Diagnostic Techniques
- **Systematic elimination**: Binary search through code/config; divide-and-conquer to isolate fault domain
- **Hypothesis-driven**: Form falsifiable hypotheses, design minimal experiments, validate with evidence
- **Log & trace analysis**: Stack trace interpretation, log correlation across services, distributed tracing (Jaeger, OTEL)
- **Minimal reproduction**: Reduce to smallest failing case before investigating

### Error Categories
- **Memory issues**: Leaks, buffer overflows, use-after-free — Valgrind, AddressSanitizer, heapdump
- **Concurrency bugs**: Race conditions, deadlocks, thread safety — ThreadSanitizer, lock analysis
- **Performance degradation**: CPU hotspots, GC pressure, I/O blocking, N+1 queries, cache thrash
- **Production failures**: Non-intrusive live debugging, sampling profilers, canary analysis

### Debugging Tools
- **Native**: gdb/lldb (C/C++/Rust), pdb/ipdb (Python), node inspect (JS), delve (Go)
- **System**: strace/ltrace, perf, eBPF/bpftrace for kernel-level tracing
- **Network**: tcpdump/Wireshark for protocol-level debugging
- **Browser/UI**: Chrome DevTools, React DevTools, network waterfall analysis

### Root Cause & Prevention
- **Postmortem**: Timeline reconstruction, five-whys analysis, blameless culture
- **Pattern library**: Off-by-one, null dereference, resource leaks, integer overflow, logic inversion
- **Monitoring**: Add metrics/alerts at failure point to detect recurrence
- **Code hardening**: Input validation, defensive assertions, structured error handling

## Workflow

1. **Reproduce**: Confirm issue is reproducible; document conditions, environment, steps
2. **Hypothesize**: Form ranked hypotheses based on symptoms, recent changes, system knowledge
3. **Isolate**: Use binary search / component isolation to narrow fault domain; collect concrete evidence
4. **Fix & Validate**: Implement minimal targeted fix; verify resolution without side effects; add regression test

## Key Principles

1. **Reproduce before investigating** — unreproducible bugs are guesswork
2. **Scientific method** — each step is an experiment with predicted outcome; document results
3. **Follow the data** — logs, metrics, stack traces beat intuition
4. **Simplify ruthlessly** — strip away unrelated code until only the bug remains
5. **Check recent changes** — `git log --since="3 days ago"` is often fastest path to root cause
6. **Fix the cause, not the symptom** — workarounds are technical debt with an expiry date
7. **Leave it better** — every fix includes regression test and monitoring addition

## Key Examples

### Race Condition Debugging Pattern
```python
# Reproduce: concurrent load test exposes the race
import threading, time

def concurrent_write_read(i):
    cache.set(f"key_{i}", f"value_{i}")
    time.sleep(0.001)           # simulate jitter
    val = cache.get(f"key_{i}")
    if val != f"value_{i}":
        errors.append((i, val))

threads = [threading.Thread(target=concurrent_write_read, args=(i,)) for i in range(100)]
[t.start() for t in threads]; [t.join() for t in threads]

# Fix: serialize critical section with lock
_lock = threading.Lock()
def update_counter_safe(key):
    with _lock:
        count = cache.get(key) or 0
        count += 1
        cache.set(key, count)
# Add regression test: 50 threads, assert final count == 50
```

### Memory Leak Detection Pattern
```python
import tracemalloc

tracemalloc.start(10)
# ... run workload ...

snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:10]:
    print(stat)  # reveals top allocating file:line

# Compare snapshots to find growth:
# snapshot2.compare_to(snapshot1, "lineno") — positive size_diff = leak

# Common culprits: global list/dict accumulation, unregistered callbacks,
# circular references preventing GC, unbounded thread-local storage
```
