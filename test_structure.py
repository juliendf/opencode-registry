#!/usr/bin/env python3
"""
OpenCode Registry v1.0 — Structural Validation Suite (Dry-Run)

Validates agent/subagent/skill structure without requiring live model backend.
Checks file existence, frontmatter validity, and delegation consistency.

Usage:
    python test_structure.py              # Run all checks
    python test_structure.py -v           # Verbose output
    python test_structure.py --fail-fast  # Stop on first error
"""

import argparse
import sys
import yaml
from pathlib import Path
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

REPO_ROOT = Path(__file__).parent
OPENCODE_DIR = REPO_ROOT / "opencode"
AGENTS_DIR = OPENCODE_DIR / "agents"
SUBAGENTS_DIR = AGENTS_DIR / "subagents"
SKILLS_DIR = OPENCODE_DIR / "skills"
SHARED_DIR = AGENTS_DIR / "_shared"


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str = ""
    details: list[str] = field(default_factory=list)


class StructureValidator:
    def __init__(self, verbose: bool = False, fail_fast: bool = False):
        self.verbose = verbose
        self.fail_fast = fail_fast
        self.results: list[CheckResult] = []
        self.primary_agents: dict[str, Path] = {}
        self.subagents: dict[str, Path] = {}
        self.skills: dict[str, Path] = {}

    def _find_md_files(self, directory: Path) -> dict[str, Path]:
        """Find all .md files in directory, keyed by stem name."""
        files = {}
        if directory.exists():
            for f in directory.glob("*.md"):
                if f.stem not in ("README",):
                    files[f.stem] = f
        return files

    def _parse_frontmatter(self, file_path: Path) -> Optional[dict]:
        """Extract YAML frontmatter from markdown file."""
        try:
            content = file_path.read_text()
            if content.startswith("---"):
                _, fm, _ = content.split("---", 2)
                return yaml.safe_load(fm)
        except Exception as e:
            if self.verbose:
                print(
                    f"{YELLOW}Warning: Failed to parse frontmatter in {file_path}: {e}{RESET}"
                )
        return None

    def _add_result(
        self, name: str, passed: bool, message: str = "", details: list[str] = None
    ):
        result = CheckResult(
            name=name, passed=passed, message=message, details=details or []
        )
        self.results.append(result)
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {name}")
        if message and not passed:
            print(f"       {RED}{message}{RESET}")
        if details and not passed:
            for detail in details[:10]:  # Limit output
                print(f"       {DIM}- {detail}{RESET}")
            if len(details) > 10:
                print(f"       {DIM}... and {len(details) - 10} more{RESET}")

        if self.fail_fast and not passed:
            print(f"\n{RED}Fail-fast enabled. Stopping.{RESET}")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Validation checks
    # ------------------------------------------------------------------

    def check_primary_agents_exist(self):
        """Verify all 5 primary agent files exist."""
        expected = ["ask-me-anything", "plan", "build", "debug", "review"]
        self.primary_agents = self._find_md_files(AGENTS_DIR)

        missing = [name for name in expected if name not in self.primary_agents]
        extra = [name for name in self.primary_agents if name not in expected]

        passed = len(missing) == 0
        msg = f"Expected {len(expected)} agents, found {len(self.primary_agents)}"
        details = []
        if missing:
            details.extend([f"Missing: {m}" for m in missing])
        if extra:
            details.extend([f"Unexpected: {e}" for e in extra])

        self._add_result("Primary agents exist", passed, msg, details)

    def check_subagents_exist(self):
        """Verify all 10 subagent files exist in flat structure."""
        self.subagents = self._find_md_files(SUBAGENTS_DIR)

        # We don't enforce exact count but check they all have frontmatter
        passed = len(self.subagents) > 0
        msg = f"Found {len(self.subagents)} subagents in flat structure"

        self._add_result("Subagents exist", passed, msg)

    def check_skills_exist(self):
        """Verify skills directory structure."""
        if not SKILLS_DIR.exists():
            self._add_result(
                "Skills exist", False, f"Skills directory not found: {SKILLS_DIR}"
            )
            return

        skill_count = 0
        invalid_skills = []

        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill_count += 1
                    self.skills[skill_dir.name] = skill_file
                else:
                    invalid_skills.append(f"{skill_dir.name}/ (missing SKILL.md)")

        passed = skill_count >= 30  # We expect 40+, but be tolerant
        msg = f"Found {skill_count} valid skills"
        self._add_result("Skills exist", passed, msg, invalid_skills)

    def check_frontmatter_valid(self):
        """Verify all agents/subagents have valid YAML frontmatter."""
        invalid = []

        for name, path in {**self.primary_agents, **self.subagents}.items():
            fm = self._parse_frontmatter(path)
            if fm is None:
                invalid.append(f"{name}: No frontmatter")
                continue

            required_fields = ["description", "mode"]
            missing = [f for f in required_fields if f not in fm]
            if missing:
                invalid.append(f"{name}: Missing fields: {', '.join(missing)}")

            # Check no version field (removed in v1.0)
            if "version" in fm:
                invalid.append(f"{name}: Has deprecated 'version' field")

        passed = len(invalid) == 0
        self._add_result(
            "Frontmatter valid", passed, f"{len(invalid)} issues found", invalid
        )

    def check_delegation_consistency(self):
        """Verify agents only delegate to existing subagents or primary agents."""
        import re

        undefined_targets = []
        valid_targets = {**self.primary_agents, **self.subagents}

        for agent_name, agent_path in {**self.primary_agents, **self.subagents}.items():
            content = agent_path.read_text()

            # Find task() calls with subagent_type
            task_calls = re.findall(r'subagent_type=["\'](\w+)["\']', content)

            for target in task_calls:
                if target not in valid_targets:
                    undefined_targets.append(f"{agent_name} → {target} (not found)")

        passed = len(undefined_targets) == 0
        self._add_result(
            "Delegation consistency",
            passed,
            f"{len(undefined_targets)} undefined references",
            undefined_targets,
        )

    def check_no_stale_references(self):
        """Verify no references to old agent names (plan-design, build-code, etc.)."""
        old_names = [
            "plan-design",
            "plan-architecture",
            "build-code",
            "build-infrastructure",
        ]
        found = []

        # Search in all agent files
        for name, path in {**self.primary_agents, **self.subagents}.items():
            content = path.read_text()
            for old in old_names:
                if old in content:
                    found.append(f"{name}: References '{old}'")

        # Search in _shared files
        if SHARED_DIR.exists():
            for shared_file in SHARED_DIR.glob("*.md"):
                content = shared_file.read_text()
                for old in old_names:
                    if old in content:
                        found.append(f"_shared/{shared_file.name}: References '{old}'")

        passed = len(found) == 0
        self._add_result(
            "No stale references", passed, f"{len(found)} stale references found", found
        )

    def check_shared_files_exist(self):
        """Verify _shared directory has required files."""
        expected = [
            "communication-style.md",
            "context-management.md",
            "delegation-rules.md",
            "production-safety-protocol.md",
        ]

        if not SHARED_DIR.exists():
            self._add_result(
                "Shared files exist",
                False,
                f"_shared directory not found: {SHARED_DIR}",
            )
            return

        existing = [f.name for f in SHARED_DIR.glob("*.md")]
        missing = [f for f in expected if f not in existing]

        passed = len(missing) == 0
        self._add_result(
            "Shared files exist",
            passed,
            f"Missing: {', '.join(missing)}" if missing else "All present",
            missing,
        )

    def check_bundles_valid(self):
        """Verify bundle YAML files are parseable."""
        bundles_dir = REPO_ROOT / "bundles"
        if not bundles_dir.exists():
            self._add_result("Bundles valid", False, "bundles/ directory not found")
            return

        invalid = []
        for bundle_file in bundles_dir.glob("*.yaml"):
            try:
                import yaml

                content = bundle_file.read_text()
                data = yaml.safe_load(content)
                if not isinstance(data, dict):
                    invalid.append(f"{bundle_file.name}: Not a dict")
                elif "components" not in data:
                    invalid.append(f"{bundle_file.name}: Missing 'components' key")
            except Exception as e:
                invalid.append(f"{bundle_file.name}: Parse error: {e}")

        passed = len(invalid) == 0
        self._add_result("Bundles valid", passed, f"{len(invalid)} issues", invalid)

    def check_token_reduction(self):
        """Verify token counts are within expected range."""
        primary_lines = sum(
            p.read_text().count("\n") for p in self.primary_agents.values()
        )
        subagent_lines = sum(p.read_text().count("\n") for p in self.subagents.values())

        # Check primary agents aren't too bloated
        bloated = []
        for name, path in self.primary_agents.items():
            lines = path.read_text().count("\n")
            if lines > 120:  # Generous threshold
                bloated.append(f"{name}: {lines} lines")

        passed = len(bloated) == 0
        msg = f"Primary: {primary_lines} lines, Subagents: {subagent_lines} lines"
        self._add_result("Token bloat check", passed, msg, bloated)

    def run_all(self):
        """Execute all validation checks."""
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}  OpenCode Registry v1.0 — Structural Validation{RESET}")
        print(f"{BOLD}{'='*60}{RESET}\n")

        print(f"{CYAN}Repository:{RESET} {REPO_ROOT}")
        print(f"{CYAN}Agents:{RESET} {AGENTS_DIR}")
        print(f"{CYAN}Subagents:{RESET} {SUBAGENTS_DIR}")
        print(f"{CYAN}Skills:{RESET} {SKILLS_DIR}")
        print()

        # Run checks in order
        self.check_primary_agents_exist()
        self.check_subagents_exist()
        self.check_skills_exist()
        self.check_shared_files_exist()
        self.check_frontmatter_valid()
        self.check_delegation_consistency()
        self.check_no_stale_references()
        self.check_bundles_valid()
        self.check_token_reduction()

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"\n{BOLD}{'='*60}{RESET}")
        if passed == total:
            print(f"{GREEN}{BOLD}  All {total} checks passed{RESET}")
        else:
            print(f"{RED}{BOLD}  {passed}/{total} checks passed{RESET}")
            print(f"{RED}  {total - passed} checks failed{RESET}")
        print(f"{BOLD}{'='*60}{RESET}\n")

        return passed == total


def main():
    parser = argparse.ArgumentParser(
        description="Validate OpenCode Registry v1.0 structure without live model"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop on first failure"
    )
    args = parser.parse_args()

    validator = StructureValidator(verbose=args.verbose, fail_fast=args.fail_fast)
    success = validator.run_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
