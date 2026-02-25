#!/usr/bin/env python3
"""
OpenCode Agentic Delegation Test Suite
Tests that primary agents correctly delegate to specialist subagents.

One test case per primary agent:
  - ask-me-anything
  - review
  - debug
  - build-code
  - build-infrastructure
  - plan-architecture
  - plan-design  (output-based: validates spec sections, no subagent delegation)

Usage:
    python test_delegation.py                  # Interactive test selection
    python test_delegation.py -v               # Show agent response + task call details
    python test_delegation.py -t "Test 1"      # Run a specific test by name
    python test_delegation.py --list           # List all test cases

How it works:
    1. Runs `opencode run --agent <agent> --format json "<prompt>"`
    2. Parses the JSON event stream for `tool_use` events where tool == "task"
    3. Extracts `subagent_type` from each task call
    4. Asserts that all expected subagents were called (delegation tests)
       OR that all expected keywords appear in the agent's text response (output tests)
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Optional


# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


@dataclass
class TestCase:
    name: str
    agent: str
    prompt: str
    description: str = ""
    # Delegation test: assert these subagents were called via task()
    expected_subagents: list[str] = field(default_factory=list)
    # Output test: assert these keywords appear in the agent's text response
    expected_output_keywords: list[str] = field(default_factory=list)


@dataclass
class TestResult:
    test: TestCase
    passed: bool
    called_subagents: list[str] = field(default_factory=list)
    missing_subagents: list[str] = field(default_factory=list)
    unexpected_subagents: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    error: Optional[str] = None
    duration: float = 0.0
    raw_output: str = ""
    agent_response: str = ""  # final text output from the agent


# ---------------------------------------------------------------------------
# Test Cases — one per primary agent
# ---------------------------------------------------------------------------

TEST_CASES = [
    # -------------------------------------------------------------------------
    # Test 1 — ask-me-anything
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 1: ask-me-anything — Multi-Cloud Architecture Strategy",
        agent="ask-me-anything",
        description="Triggers aws-specialist + microservices-architect + terraform-expert in parallel",
        prompt=(
            "I am designing a new distributed system from scratch using microservices. "
            "I need advice on: 1) microservices patterns like service discovery, circuit breaker, "
            "and saga pattern for distributed transactions, 2) whether to use AWS EKS or ECS "
            "for deployment, and 3) how to structure Terraform modules and tfstate backend "
            "for a multi-environment setup."
        ),
        expected_subagents=[
            "subagents/03-infrastructure/aws-specialist",
            "subagents/01-core/microservices-architect",
            "subagents/03-infrastructure/terraform-expert",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 2 — review
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 2: review — Inline Code Security Review",
        agent="review",
        description="Triggers python-pro + security-auditor + sql-pro from an inline snippet",
        prompt=(
            "Please review this hypothetical snippet for OWASP vulnerabilities, async "
            "Python best practices, and SQL query issues:\n\n"
            "```python\n"
            "import sqlite3\n"
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
            "@app.get('/user')\n"
            "async def get_user(name: str):\n"
            "    conn = sqlite3.connect('users.db')\n"
            "    cursor = conn.cursor()\n"
            "    cursor.execute(f'SELECT * FROM users WHERE username = \"{name}\"')\n"
            "    return cursor.fetchall()\n"
            "```\n\n"
            "Specifically: 1) security vulnerabilities in the FastAPI endpoint, "
            "2) async Python correctness, "
            "3) rewrite the SQL query using proper parameterized queries, CTEs, and window functions."
        ),
        expected_subagents=[
            "subagents/02-languages/python-pro",
            "subagents/04-quality-and-security/security-auditor",
            "subagents/02-languages/sql-pro",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 3 — debug
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 3: debug — Cross-Stack Performance Debugging",
        agent="debug",
        description="Triggers database-optimizer + react-specialist for a N+1 + rendering scenario",
        prompt=(
            "I need expert help fixing two production bugs: "
            "1) PostgreSQL N+1 query issue causing slow API responses, "
            "2) React components rendering bottleneck on the dashboard page."
        ),
        expected_subagents=[
            "subagents/05-data-ai/database-optimizer",
            "subagents/02-languages/react-specialist",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 4 — build-code
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 4: build-code — Full-Stack Auth Feature",
        agent="build-code",
        description="Triggers react-specialist + python-pro + security-auditor for a JWT login page",
        prompt=(
            "We need a new authentication system. Please provide implementation guidance for all three domains: "
            "1) React login page with JWT token handling (React specialist), "
            "2) Python backend with FastAPI, async/await, pydantic validation (Python expert), "
            "3) OWASP security best practices for the full stack (security auditor). "
            "Include Python-specific patterns, async handler design, and security integration."
        ),
        expected_subagents=[
            "subagents/02-languages/react-specialist",
            "subagents/02-languages/python-pro",
            "subagents/04-quality-and-security/security-auditor",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 5 — build-infrastructure
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 5: build-infrastructure — EKS Cluster with Monitoring",
        agent="build-infrastructure",
        description="Triggers terraform-expert + kubernetes-expert + observability-engineer",
        prompt=(
            "Set up a production-ready EKS cluster using Terraform modules. The cluster "
            "needs autoscaling node groups, and we want Prometheus and Grafana deployed "
            "via Helm for monitoring and alerting."
        ),
        expected_subagents=[
            "subagents/03-infrastructure/terraform-expert",
            "subagents/03-infrastructure/kubernetes-expert",
            "subagents/03-infrastructure/observability-engineer",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 6 — plan-architecture
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 6: plan-architecture — E-Commerce Platform Design",
        agent="plan-architecture",
        description="Triggers microservices-architect + database-optimizer + aws-specialist",
        prompt=(
            "Design the architecture for a new e-commerce platform. It needs to handle "
            "high traffic with a microservices backend, a PostgreSQL database with "
            "optimized query patterns, and should be deployed on AWS. Provide technology "
            "choices with trade-off analysis."
        ),
        expected_subagents=[
            "subagents/01-core/microservices-architect",
            "subagents/05-data-ai/database-optimizer",
            "subagents/03-infrastructure/aws-specialist",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 7 — plan-design  (output-based — no subagent delegation expected)
    # -------------------------------------------------------------------------
    TestCase(
        name="Test 7: plan-design — Order Tracking Functional Spec",
        agent="plan-design",
        description="Output-based: validates spec sections present in response (no delegation)",
        prompt=(
            "Please write a complete functional specification for the following feature. "
            "All context you need is provided below — skip clarifying questions and go "
            "straight to writing the spec.\n\n"
            "Feature: Real-time order tracking for customers.\n"
            "Users: End consumers shopping on our e-commerce site.\n"
            "Goal: Customers should be able to see the current status of each order, "
            "get notified by email when the status changes, and view a full order history.\n"
            "Out of scope: payment processing, returns, and admin dashboards.\n"
            "Constraints: must work on mobile browsers; no native app required.\n"
            "Success metric: 80% of customers check order status without contacting support.\n\n"
            "Produce the full spec now with all required sections: Goal, Users & Context, "
            "User Stories, Functional Requirements, Acceptance Criteria, Out of Scope, "
            "Open Questions, and Assumptions."
        ),
        expected_output_keywords=[
            "Goal",
            "User Stories",
            "Functional Requirements",
            "Acceptance Criteria",
            "Out of Scope",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run_opencode(agent: str, prompt: str, timeout: int = 300) -> tuple[str, int]:
    """Invoke opencode run and return (raw_output, returncode)."""
    cmd = [
        "opencode", "run",
        "--agent", agent,
        "--format", "json",
        prompt,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired as e:
        output = (e.stdout or b"").decode("utf-8", errors="replace")
        output += (e.stderr or b"").decode("utf-8", errors="replace")
        return output, 1


def parse_task_calls(raw_output: str) -> list[str]:
    """Parse JSON event stream and return list of subagent_type values from task tool calls."""
    called = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        part = event.get("part", {})
        if part.get("type") == "tool" and part.get("tool") == "task":
            state = part.get("state", {})
            subagent = state.get("input", {}).get("subagent_type")
            if subagent:
                called.append(subagent)

    return called


def parse_agent_response(raw_output: str) -> str:
    """Concatenate all text parts from the JSON event stream into the agent's final response."""
    chunks = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "text":
            text = event.get("part", {}).get("text", "")
            if text:
                chunks.append(text)
    return "".join(chunks)


def run_test(test: TestCase, verbose: bool = False) -> TestResult:
    """Execute a single test case and return its result."""
    start = time.time()
    raw_output, _ = run_opencode(test.agent, test.prompt)
    duration = time.time() - start

    agent_response = parse_agent_response(raw_output)

    # --- Delegation test ---
    if test.expected_subagents:
        called = parse_task_calls(raw_output)
        expected_set = set(test.expected_subagents)
        called_set = set(called)
        missing = sorted(expected_set - called_set)
        unexpected = sorted(called_set - expected_set)
        passed = len(missing) == 0
        return TestResult(
            test=test,
            passed=passed,
            called_subagents=sorted(called_set),
            missing_subagents=missing,
            unexpected_subagents=unexpected,
            duration=duration,
            raw_output=raw_output if verbose else "",
            agent_response=agent_response if verbose else "",
        )

    # --- Output test ---
    if test.expected_output_keywords:
        response_lower = agent_response.lower()
        missing_kw = [kw for kw in test.expected_output_keywords if kw.lower() not in response_lower]
        passed = len(missing_kw) == 0
        return TestResult(
            test=test,
            passed=passed,
            missing_keywords=missing_kw,
            duration=duration,
            raw_output=raw_output if verbose else "",
            agent_response=agent_response if verbose else "",
        )

    # No assertions defined — trivially pass
    return TestResult(test=test, passed=True, duration=duration)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_header():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  OpenCode Agentic Delegation Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


def print_test_start(test: TestCase, index: int, total: int):
    mode = "output" if test.expected_output_keywords else "delegation"
    print(f"{CYAN}{BOLD}[{index}/{total}] {test.name}{RESET}")
    print(f"  {DIM}Agent : {test.agent}  [{mode}]{RESET}")
    if test.expected_subagents:
        print(f"  {DIM}Expect: {', '.join(test.expected_subagents)}{RESET}")
    else:
        print(f"  {DIM}Expect: keywords → {', '.join(test.expected_output_keywords)}{RESET}")
    print(f"  {DIM}Running...{RESET}", end="", flush=True)


def print_test_result(result: TestResult, verbose: bool = False):
    duration_str = f"{result.duration:.1f}s"

    if result.error:
        print(f"\r  {RED}ERROR{RESET} ({duration_str}): {result.error}")
        print()
        return

    status = f"{GREEN}PASSED{RESET}" if result.passed else f"{RED}FAILED{RESET}"
    print(f"\r  {status} ({duration_str})")

    # Always show which subagents were actually called for delegation tests
    if result.test.expected_subagents:
        for s in result.called_subagents:
            marker = GREEN + "✓" + RESET if s in result.test.expected_subagents else YELLOW + "~" + RESET
            print(f"    {marker} {s}")
        for s in result.missing_subagents:
            print(f"    {RED}✗{RESET} {s}  {DIM}(not called){RESET}")

    if not result.passed:
        if result.missing_keywords:
            print(f"  {RED}Missing keywords in response:{RESET}")
            for kw in result.missing_keywords:
                print(f"    {RED}✗{RESET} {kw!r}")

    if verbose and result.raw_output:
        if result.agent_response:
            print(f"\n  {CYAN}--- Agent response ---{RESET}")
            for line in result.agent_response.splitlines():
                print(f"  {line}")

        if result.test.expected_subagents:
            print(f"\n  {DIM}--- Task calls ---{RESET}")
            task_calls_found = False
            for line in result.raw_output.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    part = event.get("part", {})
                    if part.get("tool") == "task":
                        tool_input = part.get("state", {}).get("input", {})
                        print(f"  {DIM}task({json.dumps(tool_input, indent=4)}){RESET}")
                        task_calls_found = True
                except json.JSONDecodeError:
                    pass
            if not task_calls_found:
                print(f"  {DIM}(no task calls made){RESET}")

    print()


def print_summary(results: list[TestResult]):
    passed_tests = sum(1 for r in results if r.passed)
    total_tests = len(results)
    total_time = sum(r.duration for r in results)

    # --- Delegation summary ---
    delegation_results = [r for r in results if r.test.expected_subagents]
    all_expected: list[tuple[str, str]] = []
    for r in delegation_results:
        for s in r.test.expected_subagents:
            all_expected.append((s, r.test.name))

    called_map: dict[str, set[str]] = {r.test.name: set(r.called_subagents) for r in delegation_results}
    unexpected_map: dict[str, list[str]] = {r.test.name: r.unexpected_subagents for r in delegation_results}

    properly_called = [(s, t) for s, t in all_expected if s in called_map.get(t, set())]
    not_called      = [(s, t) for s, t in all_expected if s not in called_map.get(t, set())]
    extra_called    = [(s, t) for t, extras in unexpected_map.items() for s in extras]

    # --- Output summary ---
    output_results = [r for r in results if r.test.expected_output_keywords]

    col = 52

    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  {passed_tests}/{total_tests} tests passed{RESET}  ({total_time:.1f}s total)")
    print()

    if delegation_results:
        print(f"  {GREEN}{BOLD}Subagents properly called ({len(properly_called)}/{len(all_expected)}){RESET}")
        if properly_called:
            for s, t in properly_called:
                print(f"    {GREEN}✓{RESET}  {s:<{col}}  {DIM}{t}{RESET}")
        else:
            print(f"    {DIM}(none){RESET}")
        print()

        print(f"  {RED}{BOLD}Subagents not called ({len(not_called)}/{len(all_expected)}){RESET}")
        if not_called:
            for s, t in not_called:
                print(f"    {RED}✗{RESET}  {s:<{col}}  {DIM}{t}{RESET}")
        else:
            print(f"    {DIM}(none){RESET}")
        print()

        print(f"  {YELLOW}{BOLD}Unexpected subagents called ({len(extra_called)}){RESET}")
        if extra_called:
            for s, t in extra_called:
                print(f"    {YELLOW}~{RESET}  {s:<{col}}  {DIM}{t}{RESET}")
        else:
            print(f"    {DIM}(none){RESET}")
        print()

    if output_results:
        print(f"  {CYAN}{BOLD}Output keyword checks{RESET}")
        for r in output_results:
            status = f"{GREEN}✓{RESET}" if r.passed else f"{RED}✗{RESET}"
            print(f"    {status}  {r.test.name}")
            if not r.passed:
                for kw in r.missing_keywords:
                    print(f"         {RED}missing:{RESET} {kw!r}")
        print()

    print(f"{BOLD}{'='*60}{RESET}\n")


# ---------------------------------------------------------------------------
# Interactive test selection
# ---------------------------------------------------------------------------

def prompt_select_tests() -> list[TestCase]:
    """Interactively prompt the user to select which tests to run."""
    print(f"\n{BOLD}Select tests to run:{RESET}")
    print(f"  {DIM}0. All tests{RESET}")
    for i, t in enumerate(TEST_CASES, 1):
        mode = "[output]" if t.expected_output_keywords else "[delegation]"
        print(f"  {i}. {t.name}  {DIM}{mode}{RESET}")
        print(f"     {DIM}{t.description}{RESET}")

    print(f"\n  {DIM}Enter numbers separated by spaces/commas, or 0 for all (default: 0):{RESET} ", end="", flush=True)
    try:
        raw = input().strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

    if not raw or raw == "0":
        return TEST_CASES

    selected = []
    for token in raw.replace(",", " ").split():
        try:
            idx = int(token)
            if 1 <= idx <= len(TEST_CASES):
                selected.append(TEST_CASES[idx - 1])
            else:
                print(f"{YELLOW}Ignoring out-of-range index: {idx}{RESET}")
        except ValueError:
            print(f"{YELLOW}Ignoring invalid input: {token!r}{RESET}")

    if not selected:
        print(f"{RED}No valid tests selected, running all.{RESET}")
        return TEST_CASES

    return selected


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Test OpenCode agentic delegation workflow"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show agent response text and raw task() call details",
    )
    parser.add_argument(
        "-t", "--test",
        metavar="NAME",
        help="Run a specific test (partial name match)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all test cases and exit",
    )
    args = parser.parse_args()

    if args.list:
        print(f"\n{BOLD}Available test cases:{RESET}")
        for i, t in enumerate(TEST_CASES, 1):
            mode = "[output]" if t.expected_output_keywords else "[delegation]"
            print(f"  {i}. {t.name}  {DIM}{mode}{RESET}")
            print(f"     {DIM}Agent: {t.agent}{RESET}")
            print(f"     {DIM}{t.description}{RESET}")
        print()
        return

    # Filter tests if requested
    tests_to_run = TEST_CASES
    if args.test:
        tests_to_run = [t for t in TEST_CASES if args.test.lower() in t.name.lower()]
        if not tests_to_run:
            print(f"{RED}No tests matching '{args.test}'{RESET}")
            sys.exit(1)
    elif sys.stdin.isatty():
        tests_to_run = prompt_select_tests()

    print_header()
    results = []
    for i, test in enumerate(tests_to_run, 1):
        print_test_start(test, i, len(tests_to_run))
        result = run_test(test, verbose=args.verbose)
        results.append(result)
        print_test_result(result, verbose=args.verbose)

    print_summary(results)

    if not all(r.passed for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
