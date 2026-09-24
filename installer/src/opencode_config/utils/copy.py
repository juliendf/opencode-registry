"""
File copying with template processing for component installation.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path
from typing import Any

from rich.console import Console

from ..config import Config
from .manifest import ManifestParser
from .template import TemplateEngine

console = Console()


class CopyManager:
    """Manage file copying with template processing."""

    def __init__(self, registry_path: Path, target_dir: Path, config: Config):
        """
        Initialize copy manager.

        Args:
            registry_path: Path to registry root
            target_dir: Target installation directory
            config: Config instance
        """
        self.registry_path = registry_path
        self.target_dir = target_dir
        self.config = config
        self.template_engine = TemplateEngine(config)

    def install_package(
        self,
        package_name: str,
        dry_run: bool = False,
        model_override: str | None = None,
        inherit_model: bool = False,
    ) -> bool:
        """
        Copy package files, processing templates.

        Args:
            package_name: Name of package directory (e.g., 'opencode')
            dry_run: If True, simulate without making changes
            model_override: Optional model to override tier resolution
            inherit_model: Remove selectors from agent and command frontmatter

        Returns:
            True if successful, False otherwise
        """
        package_path = self.registry_path / package_name

        if model_override and inherit_model:
            raise ValueError("model_override cannot be used with inherit_model")

        if not package_path.exists():
            console.print(f"[red]Error:[/red] Package directory not found: {package_path}")
            return False

        # Ensure base directories exist
        if not dry_run:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            base_dirs = ["agents", "skills", "commands"]
            for base_dir in base_dirs:
                (self.target_dir / base_dir).mkdir(parents=True, exist_ok=True)

        # Walk through package directory and copy files
        success = True
        copied_count = 0

        for item in package_path.rglob("*"):
            if item.is_file():
                # Skip hidden files and cache
                if any(part.startswith(".") or part == "__pycache__" for part in item.parts):
                    continue

                # Calculate relative path from package root
                rel_path = item.relative_to(package_path)
                target_path = self.target_dir / rel_path

                if dry_run:
                    console.print(f"[yellow]Would copy:[/yellow] {rel_path}")
                    copied_count += 1
                else:
                    # Create parent directories
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Check for conflicts
                    if target_path.exists() and not self._can_overwrite(target_path):
                        console.print(f"[yellow]Warning:[/yellow] {target_path} exists, skipping")
                        continue

                    # Process file
                    try:
                        self._copy_and_process_file(
                            item,
                            target_path,
                            model_override,
                            inherit_model=inherit_model,
                            relative_path=rel_path,
                        )
                        copied_count += 1
                    except (OSError, TypeError, ValueError) as e:
                        console.print(f"[red]Error copying {rel_path}:[/red] {e}")
                        success = False

        if dry_run:
            console.print(f"\n[dim]Would copy {copied_count} files[/dim]")
        else:
            console.print(f"[dim]Copied {copied_count} files[/dim]")

        return success

    def uninstall_package(self, package_name: str, dry_run: bool = False) -> bool:
        """
        Remove copied files.

        Args:
            package_name: Name of package directory
            dry_run: If True, simulate without making changes

        Returns:
            True if successful
        """
        package_path = self.registry_path / package_name

        if not package_path.exists():
            console.print(f"[yellow]Warning:[/yellow] Package directory not found: {package_path}")
            return True

        # Find and remove files that exist in both registry and target
        removed_count = 0

        for item in package_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(package_path)
                target_path = self.target_dir / rel_path

                if target_path.exists():
                    if dry_run:
                        console.print(f"[yellow]Would remove:[/yellow] {rel_path}")
                        removed_count += 1
                    else:
                        target_path.unlink()
                        removed_count += 1

        if dry_run:
            console.print(f"\n[dim]Would remove {removed_count} files[/dim]")
        else:
            console.print(f"[dim]Removed {removed_count} files[/dim]")

        return True

    def detect_installed_components(self) -> dict[str, list[str]]:
        """
        Detect installed components by scanning target directory.

        Returns:
            Dictionary mapping component types to lists of component IDs
        """
        installed = {"agents": [], "subagents": [], "skills": [], "commands": []}

        if not self.target_dir.exists():
            return installed

        # Check agent directory for primary agents
        agent_dir = self.target_dir / "agents"
        if agent_dir.exists():
            for item in agent_dir.iterdir():
                # Skip special directories like _shared, subagents, and hidden files
                if item.name.startswith("_") or item.name == "subagents":
                    continue
                if item.is_file() and item.suffix == ".md":
                    installed["agents"].append(item.stem)

            # Check for subagents directory (flat structure)
            subagent_dir = agent_dir / "subagents"
            if subagent_dir.exists() and subagent_dir.is_dir():
                for subagent_file in subagent_dir.glob("*.md"):
                    if not subagent_file.name.startswith("."):
                        installed["subagents"].append(subagent_file.stem)

        # Check skill directory
        skill_dir = self.target_dir / "skills"
        if skill_dir.exists():
            for item in skill_dir.iterdir():
                if item.is_dir() and not item.name.startswith(".") and (item / "SKILL.md").exists():
                    installed["skills"].append(item.name)

        # Check command directory
        command_dir = self.target_dir / "commands"
        if command_dir.exists():
            for item in command_dir.iterdir():
                if item.is_file() and item.suffix == ".md" and not item.name.startswith("."):
                    installed["commands"].append(item.stem)

        return installed

    def get_component_fingerprint(
        self, component_type: str, component_id: str, package_name: str = "opencode"
    ) -> str | None:
        """Hash registry source files and model-tier resolution for one component."""
        package_path = self.registry_path / package_name
        if component_type == "agent":
            component_path = package_path / "agents" / f"{component_id}.md"
            files = [component_path] if component_path.is_file() else []
            fingerprint_root = package_path
        elif component_type == "subagent":
            component_path = package_path / "agents" / "subagents" / f"{component_id}.md"
            files = [component_path] if component_path.is_file() else []
            fingerprint_root = package_path
        elif component_type == "skill":
            component_path = package_path / "skills" / component_id
            files = (
                sorted(
                    path
                    for path in component_path.rglob("*")
                    if path.is_file()
                    and not any(
                        part.startswith(".") or part == "__pycache__" for part in path.parts
                    )
                )
                if component_path.is_dir()
                else []
            )
            fingerprint_root = component_path
        elif component_type == "command":
            component_path = package_path / "commands" / f"{component_id}.md"
            files = [component_path] if component_path.is_file() else []
            fingerprint_root = package_path
        else:
            return None

        if not files:
            return None

        digest = hashlib.sha256()
        for path in files:
            digest.update(path.relative_to(fingerprint_root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")

        if component_type != "skill":
            frontmatter = ManifestParser.parse_frontmatter(component_path)
            tier = frontmatter.get("model_tier") if isinstance(frontmatter, dict) else None
            if tier:
                configured_model = self.config.get_model_for_tier(tier) or "<inherit>"
                digest.update(f"tier:{tier}:{configured_model}".encode())

        return digest.hexdigest()

    def get_component_fingerprints(
        self, detected_components: dict[str, list[str]], package_name: str = "opencode"
    ) -> dict[str, str]:
        """Return source fingerprints keyed by singular type and component ID."""
        fingerprints = {}
        for component_type_plural, component_ids in detected_components.items():
            component_type = component_type_plural.rstrip("s")
            for component_id in component_ids:
                fingerprint = self.get_component_fingerprint(
                    component_type, component_id, package_name
                )
                if fingerprint:
                    fingerprints[f"{component_type}:{component_id}"] = fingerprint
        return fingerprints

    def get_installed_metadata(self, component_path: Path) -> dict[str, Any]:
        """
        Extract metadata from installed component.

        Args:
            component_path: Path to component file

        Returns:
            Dictionary with component metadata
        """
        if not component_path.exists():
            return {}

        frontmatter = ManifestParser.parse_frontmatter(component_path)
        if frontmatter:
            return frontmatter

        return {}

    def _tier_configured(self, tier: str) -> bool:
        """
        Check if a model tier has been explicitly configured by the user.

        Args:
            tier: Tier name (high, medium, low, free)

        Returns:
            True if the tier has a configured model, False otherwise
        """
        return self.template_engine.config.get_model_for_tier(tier) is not None

    def _copy_and_process_file(
        self,
        source: Path,
        dest: Path,
        model_override: str | None = None,
        inherit_model: bool = False,
        relative_path: Path | None = None,
    ) -> None:
        """
        Copy file and process templates if applicable.

        Model-aware markdown files can use ``model_tier`` as a placeholder.
        During install:
        - If ``model_override`` is provided: replace with ``model: <override>``
        - If the tier IS configured: resolve to ``model: <resolved>``
        - If the tier is NOT configured: remove the line entirely (inherit model)

        Args:
            source: Source file path
            dest: Destination file path
            model_override: Optional literal model string; skips tier resolution
            inherit_model: Strip selectors from agent and command frontmatter
            relative_path: Source path relative to the installed package
        """
        if not self.template_engine.should_process_file(str(source)):
            shutil.copy2(source, dest)
            return

        with open(source, "r", encoding="utf-8") as f:
            content = f.read()

        if (
            inherit_model
            and relative_path
            and relative_path.parts
            and relative_path.parts[0] in {"agents", "commands"}
        ):
            content = self._remove_model_selectors(content)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            return

        tier_pattern = re.compile(r'^model_tier:\s*["\']?(\w+)["\']?\s*$', re.MULTILINE)

        if model_override:
            # Explicit override: replace model_tier: with model: <override>
            # or inject if not present
            if tier_pattern.search(content):
                content = tier_pattern.sub(f"model: {model_override}", content)
            else:
                content = content.replace("---\n", f"---\nmodel: {model_override}\n", 1)
        else:
            # Resolve model_tier → model via configured tiers.
            # When tier not configured: remove line (inherit caller model)
            def resolve_tier(match: re.Match) -> str:
                tier = match.group(1)
                if self._tier_configured(tier):
                    resolved = self.template_engine.resolve_model(tier)
                    return f"model: {resolved}"
                else:
                    return ""  # Remove the line — model inheritance

            content = tier_pattern.sub(resolve_tier, content)

        # Process any remaining {{tier:X}} / {{model:X}} templates
        try:
            content = self.template_engine.process_content(content)
        except ValueError as e:
            console.print(f"[yellow]Warning processing {source}:[/yellow] {e}")

        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def _remove_model_selectors(content: str) -> str:
        """Remove top-level model selector keys while preserving body and nested metadata."""
        opening = re.match(r"\A---\r?\n", content)
        if opening is None:
            return content

        closing = re.search(r"(?m)^---[ \t]*\r?$", content[opening.end() :])
        if closing is None:
            return content

        frontmatter_end = opening.end() + closing.start()
        frontmatter = content[opening.end() : frontmatter_end]
        selector_fields = {"model", "model_tier", "variant"}
        cleaned_lines = []
        skip_nested_value = False
        for line in frontmatter.splitlines(keepends=True):
            if not line.strip():
                if not skip_nested_value:
                    cleaned_lines.append(line)
                continue
            if line[0].isspace():
                if not skip_nested_value:
                    cleaned_lines.append(line)
                continue

            key, separator, _ = line.partition(":")
            normalized_key = key.strip().strip("\"'")
            skip_nested_value = bool(separator) and normalized_key in selector_fields
            if not skip_nested_value:
                cleaned_lines.append(line)

        cleaned_frontmatter = "".join(cleaned_lines)
        return content[: opening.end()] + cleaned_frontmatter + content[frontmatter_end:]

    def _can_overwrite(self, path: Path) -> bool:
        """
        Check if file can be safely overwritten.

        Args:
            path: File path to check

        Returns:
            True if file can be overwritten
        """
        # For now, allow overwrite (user should backup if needed)
        # Future: could check if file was modified by user
        return True
