#!/usr/bin/env python3
"""
Batch script to add model_tier field to component frontmatter.
Run from repository root: python scripts/add_model_tiers.py
"""

import re
from pathlib import Path

# Tier assignments
# high   = complex reasoning (architecture, design, infrastructure)
# medium = general coding, implementation, specialist work
# low    = simple tasks (docs, commits, Q&A)

PRIMARY_AGENT_TIERS = {
    "plan-design": "high",
    "plan-architecture": "high",
    "build-infrastructure": "high",
    "review": "medium",
    "build-code": "medium",
    "debug": "medium",
    "ask-me-anything": "low",
}

SUBAGENT_TIERS = {
    # 01-core
    "backend-architect": "high",
    "microservices-architect": "high",
    "api-designer": "high",
    "graphql-architect": "high",
    "fullstack-developer": "medium",
    # 02-languages
    "python-pro": "medium",
    "typescript-pro": "medium",
    "golang-pro": "medium",
    "react-specialist": "medium",
    "vue-expert": "medium",
    "bash-expert": "medium",
    "sql-pro": "medium",
    # 03-infrastructure
    "cloud-architect": "high",
    "aws-specialist": "high",
    "gcp-specialist": "high",
    "azure-specialist": "high",
    "kubernetes-expert": "high",
    "terraform-expert": "high",
    "platform-engineer": "high",
    "upbound-crossplane-expert": "high",
    "network-engineer": "medium",
    "deployment-engineer": "medium",
    "gitops-specialist": "medium",
    "sre-engineer": "medium",
    "observability-engineer": "medium",
    # 04-quality-and-security
    "security-auditor": "high",
    "penetration-tester": "high",
    "performance-engineer": "medium",
    "debugger": "medium",
    "test-automator": "medium",
    # 05-data-ai
    "ai-engineer": "high",
    "ml-engineer": "high",
    "mlops-engineer": "high",
    "data-engineer": "medium",
    "database-optimizer": "medium",
    # 06-developer-experience
    "mcp-developer": "medium",
    "cli-developer": "medium",
    "dx-optimizer": "medium",
    # 07-specialized-domains
    "mobile-developer": "medium",
    "payment-integration": "medium",
    "technical-writer": "low",
    # 09-meta-orchestration
    "workflow-orchestrator": "high",
    "context-manager": "medium",
}

COMMAND_TIERS = {
    "commit": "low",
    "documentation": "low",
}

SKILL_TIERS = {
    "mcp-builder": "medium",
    "content-research-writer": "low",
    "project-docs": "low",
    "proofreader": "low",
    "second-opinion": "medium",
    "working-with-helm-templates": "medium",
}


def add_model_tier_to_file(file_path: Path, tier: str) -> bool:
    """
    Add model_tier field to frontmatter of a markdown file.
    Inserts after the model: line if present, otherwise before version:.
    Returns True if file was modified.
    """
    content = file_path.read_text(encoding="utf-8")

    # Skip if model_tier already present
    if re.search(r'^model_tier:', content, re.MULTILINE):
        print(f"  SKIP (already has model_tier): {file_path}")
        return False

    # Insert model_tier after the model: line
    new_content = re.sub(
        r'^(model:\s*.+)$',
        rf'\1\nmodel_tier: "{tier}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    # If no model: line found, insert before version:
    if new_content == content:
        new_content = re.sub(
            r'^(version:\s*.+)$',
            rf'model_tier: "{tier}"\n\1',
            content,
            count=1,
            flags=re.MULTILINE,
        )

    # If still unchanged, insert after the opening ---
    if new_content == content:
        new_content = re.sub(
            r'^(---\n)',
            rf'\1model_tier: "{tier}"\n',
            content,
            count=1,
            flags=re.MULTILINE,
        )

    if new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
        print(f"  OK [{tier:6}]: {file_path}")
        return True

    print(f"  WARN (no insertion point): {file_path}")
    return False


def main():
    root = Path(__file__).parent.parent
    opencode_dir = root / "opencode"
    modified = 0

    print("=== Primary Agents ===")
    for name, tier in PRIMARY_AGENT_TIERS.items():
        f = opencode_dir / "agents" / f"{name}.md"
        if f.exists():
            if add_model_tier_to_file(f, tier):
                modified += 1
        else:
            print(f"  MISSING: {f}")

    print("\n=== Subagents ===")
    for name, tier in SUBAGENT_TIERS.items():
        matches = list((opencode_dir / "agents" / "subagents").rglob(f"{name}.md"))
        if matches:
            if add_model_tier_to_file(matches[0], tier):
                modified += 1
        else:
            print(f"  MISSING: {name}")

    print("\n=== Commands ===")
    for name, tier in COMMAND_TIERS.items():
        f = opencode_dir / "commands" / f"{name}.md"
        if f.exists():
            if add_model_tier_to_file(f, tier):
                modified += 1
        else:
            print(f"  MISSING: {f}")

    print("\n=== Skills ===")
    for name, tier in SKILL_TIERS.items():
        # Skills have SKILL.md inside a directory
        f = opencode_dir / "skills" / name / "SKILL.md"
        if f.exists():
            if add_model_tier_to_file(f, tier):
                modified += 1
        else:
            print(f"  MISSING: {f}")

    print(f"\nDone. Modified {modified} files.")


if __name__ == "__main__":
    main()
