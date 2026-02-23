"""
File copying with template processing for component installation.
"""

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console

from ..config import Config
from .template import TemplateEngine
from .manifest import ManifestParser

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
        self, package_name: str, dry_run: bool = False, model_override: Optional[str] = None
    ) -> bool:
        """
        Copy package files, processing templates.

        Args:
            package_name: Name of package directory (e.g., 'opencode')
            dry_run: If True, simulate without making changes
            model_override: Optional model to override tier resolution

        Returns:
            True if successful, False otherwise
        """
        package_path = self.registry_path / package_name

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
                        console.print(
                            f"[yellow]Warning:[/yellow] {target_path} exists, skipping"
                        )
                        continue

                    # Process file
                    try:
                        self._copy_and_process_file(item, target_path, model_override)
                        copied_count += 1
                    except Exception as e:
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

        # Clean up empty directories
        if not dry_run:
            self._cleanup_empty_dirs(self.target_dir)

        if dry_run:
            console.print(f"\n[dim]Would remove {removed_count} files[/dim]")
        else:
            console.print(f"[dim]Removed {removed_count} files[/dim]")

        return True

    def detect_installed_components(self) -> Dict[str, List[str]]:
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

            # Check for subagents directory
            subagent_dir = agent_dir / "subagents"
            if subagent_dir.exists() and subagent_dir.is_dir():
                for category_dir in subagent_dir.iterdir():
                    if category_dir.is_dir():
                        for subagent_file in category_dir.glob("*.md"):
                            if not subagent_file.name.startswith("."):
                                installed["subagents"].append(subagent_file.stem)

        # Check skill directory
        skill_dir = self.target_dir / "skills"
        if skill_dir.exists():
            for item in skill_dir.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    # Check if SKILL.md exists
                    if (item / "SKILL.md").exists():
                        installed["skills"].append(item.name)

        # Check command directory
        command_dir = self.target_dir / "commands"
        if command_dir.exists():
            for item in command_dir.iterdir():
                if item.is_file() and item.suffix == ".md" and not item.name.startswith("."):
                    installed["commands"].append(item.stem)

        return installed

    def get_installed_metadata(self, component_path: Path) -> Dict[str, Any]:
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

    def _copy_and_process_file(
        self, source: Path, dest: Path, model_override: Optional[str] = None
    ):
        """
        Copy file and process templates if applicable.

        Source files use ``model_tier: "high|medium|low"`` as a placeholder.
        During install that line is replaced with ``model: <resolved-value>``
        so the installed file is clean and opencode-compatible.

        Args:
            source: Source file path
            dest: Destination file path
            model_override: Optional literal model string; skips tier resolution
        """
        if not self.template_engine.should_process_file(str(source)):
            shutil.copy2(source, dest)
            return

        import re

        with open(source, "r", encoding="utf-8") as f:
            content = f.read()

        tier_pattern = re.compile(r'^model_tier:\s*["\']?(\w+)["\']?\s*$', re.MULTILINE)

        if model_override:
            # Explicit override: replace model_tier: with model: <override>
            # or inject if not present
            if tier_pattern.search(content):
                content = tier_pattern.sub(f"model: {model_override}", content)
            else:
                content = content.replace("---\n", f"---\nmodel: {model_override}\n", 1)
        else:
            # Resolve model_tier → model via configured tiers
            def resolve_tier(match: re.Match) -> str:
                tier = match.group(1)
                resolved = self.template_engine.resolve_model(tier)
                return f"model: {resolved}"

            content = tier_pattern.sub(resolve_tier, content)

        # Process any remaining {{tier:X}} / {{model:X}} templates
        try:
            content = self.template_engine.process_content(content)
        except ValueError as e:
            console.print(f"[yellow]Warning processing {source}:[/yellow] {e}")

        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

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

    def _cleanup_empty_dirs(self, base_dir: Path):
        """
        Remove empty directories recursively.

        Args:
            base_dir: Base directory to clean
        """
        for dirpath in sorted(base_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                try:
                    dirpath.rmdir()
                except OSError:
                    pass
