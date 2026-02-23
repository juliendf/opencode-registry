"""
Manifest parsing and validation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ComponentManifest:
    """Component manifest data."""

    id: str
    type: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = None
    dependencies: List[str] = None
    sources: List[Dict[str, str]] = None
    model_tier: Optional[str] = None  # high, medium, low
    model: Optional[str] = None       # resolved model string

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.sources is None:
            self.sources = []


class ManifestParser:
    """Parse and validate component manifests."""

    @staticmethod
    def parse_file(manifest_path: Path) -> ComponentManifest:
        """Parse a manifest.yaml file."""
        with open(manifest_path, "r") as f:
            data = yaml.safe_load(f)

        return ComponentManifest(
            id=data.get("id"),
            type=data.get("type"),
            name=data.get("name"),
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            sources=data.get("sources", []),
        )

    @staticmethod
    def parse_frontmatter(md_file: Path) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from markdown file."""
        with open(md_file, "r") as f:
            content = f.read()

        # Check for frontmatter
        if not content.startswith("---"):
            return None

        # Extract frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        frontmatter = parts[1].strip()
        return yaml.safe_load(frontmatter)

    @staticmethod
    def _extract_version(frontmatter: Dict[str, Any], component_type: str) -> str:
        """Extract version from frontmatter.

        For skills: check metadata.version
        For others: check top-level version field
        """
        if component_type == "skill":
            # Skills store version in metadata
            metadata = frontmatter.get("metadata", {})
            if isinstance(metadata, dict):
                return metadata.get("version", "1.0.0")
            return "1.0.0"
        else:
            # Agents, subagents, commands use top-level version field
            return frontmatter.get("version", "1.0.0")

    @staticmethod
    def validate(manifest: ComponentManifest) -> List[str]:
        """Validate a manifest and return list of errors."""
        errors = []

        if not manifest.id:
            errors.append("Missing required field: id")
        if not manifest.type:
            errors.append("Missing required field: type")
        if manifest.type not in ["agent", "subagent", "skill", "command"]:
            errors.append(
                f"Invalid type: {manifest.type}. Must be agent, subagent, skill, or command"
            )
        if not manifest.name:
            errors.append("Missing required field: name")
        if not manifest.description:
            errors.append("Missing required field: description")

        return errors

    @staticmethod
    def create_from_md(md_file: Path, component_type: str) -> ComponentManifest:
        """Create a manifest from a markdown file with frontmatter."""
        frontmatter = ManifestParser.parse_frontmatter(md_file)
        
        # For skills, use parent directory name as ID; for others use file stem
        if component_type == "skill":
            component_id = md_file.parent.name
        else:
            component_id = md_file.stem

        if frontmatter:
            return ComponentManifest(
                id=component_id,
                type=component_type,
                name=frontmatter.get("name", component_id.replace("-", " ").title()),
                description=frontmatter.get("description", ""),
                version=ManifestParser._extract_version(frontmatter, component_type),
                author=frontmatter.get("author", ""),
                tags=frontmatter.get("tags", []),
                dependencies=frontmatter.get("dependencies", []),
                sources=[{"path": str(md_file.name), "dest": f"{component_type}s/{md_file.name}"}],
                model_tier=frontmatter.get("model_tier"),
                model=frontmatter.get("model"),
            )
        else:
            # Create basic manifest if no frontmatter
            return ComponentManifest(
                id=component_id,
                type=component_type,
                name=component_id.replace("-", " ").title(),
                description=f"OpenCode {component_type}",
                sources=[{"path": str(md_file.name), "dest": f"{component_type}s/{md_file.name}"}],
            )
