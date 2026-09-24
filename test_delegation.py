#!/usr/bin/env python3
"""
OpenCode Registry — V2 Delegation Test Suite

Tests that primary agents correctly use V2 subagents and skills and produce expected outputs:
- 5 primary agents (build, plan, debug, review, ask-me-anything)
- 10 subagents (flat structure)
- Skills loaded via the V2 skill tool

Usage:
    python test_delegation.py                  # Interactive test selection
    python test_delegation.py -v               # Show agent response + tool calls
    python test_delegation.py -t "Test 1"      # Run specific test
    python test_delegation.py --list           # List all tests
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field

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
    # Delegation test: assert these subagents were called
    expected_subagents: list[str] = field(default_factory=list)
    # Knowledge test: assert these skills were loaded
    expected_skills: list[str] = field(default_factory=list)
    # Output test: assert these keywords appear in agent's text response
    expected_output_keywords: list[str] = field(default_factory=list)


@dataclass
class TestResult:
    test: TestCase
    passed: bool
    called_subagents: list[str] = field(default_factory=list)
    missing_subagents: list[str] = field(default_factory=list)
    unexpected_subagents: list[str] = field(default_factory=list)
    called_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    error: str | None = None
    duration: float = 0.0
    raw_output: str = ""
    agent_response: str = ""


# ---------------------------------------------------------------------------
# Test Cases — Restructured V2 Architecture
# ---------------------------------------------------------------------------

TEST_CASES = [
    # -------------------------------------------------------------------------
    # Test 1 — build → output-based (infra config generation, no subagent needed)
    # -------------------------------------------------------------------------
    TestCase(
        name="build-infra",
        agent="build",
        description="Generates K8s/Terraform configs using relevant skills",
        prompt=(
            "Create a simple Kubernetes deployment YAML file for a Node.js API "
            "running on port 3000. The deployment should have 3 replicas. "
            "Write the file to k8s-deployment.yaml and show me the contents."
        ),
        expected_output_keywords=[
            "apiVersion",
            "Deployment",
            "replicas",
            "container",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 2 — review → security review (code analysis, no tool execution)
    # -------------------------------------------------------------------------
    TestCase(
        name="review-security",
        agent="review",
        description="Security review of JWT implementation → review agent handles directly",
        prompt=(
            "Review this JWT authentication implementation for security issues:\n\n"
            "```python\n"
            "import jwt\n"
            "from fastapi import FastAPI, HTTPException\n"
            "app = FastAPI()\n"
            "SECRET = 'hardcoded-secret-123'\n\n"
            "@app.post('/login')\n"
            "def login(credentials: dict):\n"
            "    token = jwt.encode({'user': credentials['user']}, SECRET, algorithm='HS256')\n"
            "    return {'token': token}\n\n"
            "@app.get('/protected')\n"
            "def protected(token: str):\n"
            "    payload = jwt.decode(token, SECRET, algorithms=['HS256'])\n"
            "    return {'user': payload['user']}\n"
            "```\n\n"
            "Identify vulnerabilities and suggest fixes."
        ),
        expected_output_keywords=[
            "hardcoded",
            "secret",
            "HS256",
            "vulnerability",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 3 — debug → infrastructure-engineer (K8s pod crash investigation)
    # -------------------------------------------------------------------------
    TestCase(
        name="debug-k8s",
        agent="debug",
        description="Inspect K8s pod crash with infrastructure execution subagent",
        prompt=(
            "The auth-service pod in namespace production keeps crashing with "
            "OOMKilled status. Use kubectl to check logs, describe the pod, "
            "and identify the memory issue. Then fix the deployment manifest."
        ),
        expected_subagents=["subagents/infrastructure-engineer"],
    ),

    # -------------------------------------------------------------------------
    # Test 4 — build → data-engineer (pipeline execution)
    # -------------------------------------------------------------------------
    TestCase(
        name="build-spark",
        agent="build",
        description="Execute Spark job on cluster → needs spark-submit, delegates",
        prompt=(
            "I have a Spark job jar file. Submit it to the YARN cluster using "
            "spark-submit with 4 executors and 2G memory each. Monitor the job "
            "until completion and check the output in HDFS."
        ),
        expected_subagents=["subagents/data-engineer"],
    ),

    # -------------------------------------------------------------------------
    # Test 5 — build → penetration-tester (security scan execution)
    # -------------------------------------------------------------------------
    TestCase(
        name="build-pentest",
        agent="build",
        description="Run authorized penetration test tools via subagent",
        prompt=(
            "Our staging API is at https://staging-api.example.com. "
            "Run nmap to check open ports, then test for SQL injection and "
            "JWT vulnerabilities. Report findings with severity ratings."
        ),
        expected_subagents=["subagents/penetration-tester"],
    ),

    # -------------------------------------------------------------------------
    # Test 6 — plan — Output-based functional spec (no subagent delegation)
    # -------------------------------------------------------------------------
    TestCase(
        name="plan-spec",
        agent="plan",
        description="Output-based: validates functional-spec sections",
        prompt=(
            "Write a functional specification for real-time order tracking. "
            "Include: Goal, Users & Context, User Stories, Functional Requirements, "
            "Acceptance Criteria, Out of Scope, Open Questions, and Assumptions."
        ),
        expected_output_keywords=[
            "Goal",
            "User Stories",
            "Functional Requirements",
            "Acceptance Criteria",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 7 — ask-me-anything → Output-based (no subagent delegation expected)
    # -------------------------------------------------------------------------
    TestCase(
        name="ask-architecture",
        agent="ask-me-anything",
        description="Output-based: compares architectures (read-only)",
        prompt=(
            "Compare AWS Lambda vs Kubernetes for a microservices architecture. "
            "When should I use serverless vs containers?"
        ),
        expected_output_keywords=[
            "Lambda",
            "Kubernetes",
            "serverless",
            "containers",
        ],
    ),

    # -------------------------------------------------------------------------
    # Test 8 — review — Code quality review (output-based)
    # -------------------------------------------------------------------------
    TestCase(
        name="review-code",
        agent="review",
        description="Output-based: security review of Python code",
        prompt=(
            "Review this code for security and quality issues:\n\n"
            "```python\n"
            "import sqlite3\n"
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
            "@app.get('/user')\n"
            "async def get_user(name: str):\n"
            "    conn = sqlite3.connect('users.db')\n"
            "    cursor = conn.cursor()\n"
            '    cursor.execute(f\'SELECT * FROM users WHERE username = "{name}"\')\n'
            "    return cursor.fetchall()\n"
            "```\n\n"
            "Check for: SQL injection, async correctness, error handling."
        ),
        expected_output_keywords=[
            "SQL injection",
            "parameterized",
            "security",
        ],
    ),
    TestCase(
        name="ask-python-skill",
        agent="ask-me-anything",
        description="Loads Python knowledge skill for a read-only typing question",
        prompt=(
            "Do not edit files. Before answering, load the python-pro skill. "
            "Then give one concise recommendation for typing a Python repository API."
        ),
        expected_skills=["python-pro"],
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
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired as e:
        output = (e.stdout or b"").decode("utf-8", errors="replace")
        output += (e.stderr or b"").decode("utf-8", errors="replace")
        return output, 1


def parse_subagent_calls(raw_output: str) -> list[str]:
    """Return child-agent IDs from V2 subagent and compatible V1 task events."""
    called = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict):
            continue

        part = event.get("part", {})
        if not isinstance(part, dict) or part.get("type") != "tool":
            continue

        tool = part.get("tool")
        if tool not in {"subagent", "task"}:
            continue

        state = part.get("state", {})
        call_input = state.get("input", {}) if isinstance(state, dict) else {}
        if not isinstance(call_input, dict):
            continue

        agent_id = call_input.get("agent" if tool == "subagent" else "subagent_type")
        if agent_id:
            called.append(agent_id)

    return called


def parse_task_calls(raw_output: str) -> list[str]:
    """Backward-compatible alias for parsing child-agent tool calls."""
    return parse_subagent_calls(raw_output)


def parse_skill_calls(raw_output: str) -> list[str]:
    """Return skill IDs from V2 skill tool events."""
    called = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict):
            continue

        part = event.get("part", {})
        if not isinstance(part, dict) or part.get("type") != "tool" or part.get("tool") != "skill":
            continue

        state = part.get("state", {})
        call_input = state.get("input", {}) if isinstance(state, dict) else {}
        if not isinstance(call_input, dict):
            continue

        skill_id = call_input.get("id")
        if skill_id:
            called.append(skill_id)

    return called


def parse_agent_response(raw_output: str) -> str:
    """Concatenate all text parts from the JSON event stream."""
    chunks = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == "text":
            text = event.get("part", {}).get("text", "")
            if text:
                chunks.append(text)
    return "".join(chunks)


def run_test(test: TestCase, verbose: bool = False) -> TestResult:
    """Execute a single test case and return its result."""
    start = time.time()
    raw_output, _rc = run_opencode(test.agent, test.prompt)
    duration = time.time() - start

    agent_response = parse_agent_response(raw_output)

    # --- Tool-use tests (subagent and skill calls) ---
    if test.expected_subagents or test.expected_skills:
        called = parse_subagent_calls(raw_output)
        called_skills = parse_skill_calls(raw_output)
        expected_set = set(test.expected_subagents)
        called_set = set(called)
        missing = sorted(expected_set - called_set)
        unexpected = sorted(called_set - expected_set)
        missing_skills = sorted(set(test.expected_skills) - set(called_skills))
        passed = not missing and not missing_skills
        return TestResult(
            test=test,
            passed=passed,
            called_subagents=sorted(called_set),
            missing_subagents=missing,
            unexpected_subagents=unexpected,
            called_skills=sorted(set(called_skills)),
            missing_skills=missing_skills,
            duration=duration,
            raw_output=raw_output if verbose else "",
            agent_response=agent_response if verbose else "",
        )

    # --- Output test (keyword matching) ---
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
    print(f"{BOLD}  OpenCode Registry — V2 Delegation Test Suite{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


def print_test_start(test: TestCase, index: int, total: int):
    mode = "output" if test.expected_output_keywords else "tool-use"
    print(f"{CYAN}{BOLD}[{index}/{total}] {test.name}{RESET}")
    print(f"  {DIM}Agent : {test.agent}  [{mode}]{RESET}")
    if test.expected_subagents or test.expected_skills:
        expected_tools = test.expected_subagents + test.expected_skills
        print(f"  {DIM}Expect: {', '.join(expected_tools)}{RESET}")
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

    # Show subagent calls for delegation tests
    if result.test.expected_subagents:
        for s in result.called_subagents:
            marker = GREEN + "✓" + RESET if s in result.test.expected_subagents else YELLOW + "~" + RESET
            print(f"    {marker} {s}")
        for s in result.missing_subagents:
            print(f"    {RED}✗{RESET} {s}  {DIM}(not called){RESET}")

    if result.test.expected_skills:
        for skill_id in result.called_skills:
            marker = GREEN + "✓" + RESET if skill_id in result.test.expected_skills else YELLOW + "~" + RESET
            print(f"    {marker} skill:{skill_id}")
        for skill_id in result.missing_skills:
            print(f"    {RED}✗{RESET} skill:{skill_id}  {DIM}(not loaded){RESET}")

    if not result.passed and result.missing_keywords:
        print(f"  {RED}Missing keywords in response:{RESET}")
        for kw in result.missing_keywords:
            print(f"    {RED}✗{RESET} {kw!r}")

    if verbose and result.raw_output:
        if result.agent_response:
            print(f"\n  {CYAN}--- Agent response ---{RESET}")
            # Truncate long responses
            lines = result.agent_response.splitlines()
            if len(lines) > 20:
                for line in lines[:10]:
                    print(f"  {line}")
                print(f"  {DIM}... ({len(lines) - 20} lines omitted) ...{RESET}")
                for line in lines[-10:]:
                    print(f"  {line}")
            else:
                for line in lines:
                    print(f"  {line}")

        if result.test.expected_subagents:
            print(f"\n  {DIM}--- Subagent calls ---{RESET}")
            subagent_calls_found = False
            for line in result.raw_output.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        continue
                    part = event.get("part", {})
                    if not isinstance(part, dict):
                        continue
                    if part.get("tool") in {"task", "subagent"}:
                        tool_input = part.get("state", {}).get("input", {})
                        print(f"  {DIM}{part['tool']}({json.dumps(tool_input, indent=4)}){RESET}")
                        subagent_calls_found = True
                except json.JSONDecodeError:
                    pass
            if not subagent_calls_found:
                print(f"  {DIM}(no subagent calls made){RESET}")

        if result.test.expected_skills:
            print(f"\n  {DIM}--- Skill calls ---{RESET}")
            for skill_id in result.called_skills:
                print(f'  {DIM}skill({json.dumps({"id": skill_id})}){RESET}')

    print()


def print_summary(results: list[TestResult]):
    passed_tests = sum(1 for r in results if r.passed)
    total_tests = len(results)
    total_time = sum(r.duration for r in results)

    # --- Delegation summary ---
    delegation_results = [r for r in results if r.test.expected_subagents]
    skill_results = [r for r in results if r.test.expected_skills]
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

    col = 40

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

        print(f"  {YELLOW}{BOLD}Unexpected subagents ({len(extra_called)}){RESET}")
        if extra_called:
            for s, t in extra_called:
                print(f"    {YELLOW}~{RESET}  {s:<{col}}  {DIM}{t}{RESET}")
        else:
            print(f"    {DIM}(none){RESET}")
        print()

    if skill_results:
        expected_skills = [skill for r in skill_results for skill in r.test.expected_skills]
        loaded_skills = [skill for r in skill_results for skill in r.called_skills]
        missing_skills = [skill for r in skill_results for skill in r.missing_skills]
        print(f"  {GREEN}{BOLD}Skills loaded ({len(expected_skills) - len(missing_skills)}/{len(expected_skills)}){RESET}")
        for skill_id in loaded_skills:
            print(f"    {GREEN}✓{RESET}  {skill_id}")
        for skill_id in missing_skills:
            print(f"    {RED}✗{RESET}  {skill_id} (not loaded)")
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
        mode = (
            "[output]"
            if t.expected_output_keywords
            else "[skill]"
            if t.expected_skills
            else "[subagent]"
        )
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
        description="Test OpenCode V2 skill/subagent usage and output quality"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show agent response text and raw subagent/skill call details",
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
            mode = (
                "[output]"
                if t.expected_output_keywords
                else "[skill]"
                if t.expected_skills
                else "[subagent]"
            )
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
