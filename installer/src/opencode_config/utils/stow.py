"""
Stow integration and fallback symlink management.
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()


class StowManager:
    """Manage installation using GNU Stow or fallback to symlinks."""

    def __init__(self, registry_path: Path, target_dir: Path):
        self.registry_path = registry_path
        self.target_dir = target_dir
        self.has_stow = self._check_stow()

    def _check_stow(self) -> bool:
        """Check if GNU Stow is available."""
        return shutil.which("stow") is not None

    def get_method(self) -> str:
        """Get installation method being used."""
        return "stow" if self.has_stow else "symlink"

    def install_package(self, package_name: str, dry_run: bool = False) -> bool:
        """
        Install a package using stow or symlinks.

        Args:
            package_name: Name of package directory (e.g., 'opencode')
            dry_run: If True, simulate without making changes

        Returns:
            True if successful, False otherwise
        """
        if self.has_stow:
            return self._install_with_stow(package_name, dry_run)
        else:
            return self._install_with_symlinks(package_name, dry_run)

    def uninstall_package(self, package_name: str, dry_run: bool = False) -> bool:
        """Uninstall a package using stow or symlinks."""
        if self.has_stow:
            return self._uninstall_with_stow(package_name, dry_run)
        else:
            return self._uninstall_with_symlinks(package_name, dry_run)

    def _install_with_stow(self, package_name: str, dry_run: bool = False) -> bool:
        """Install using GNU Stow."""
        # Ensure base directories exist in target before stowing
        if not dry_run:
            base_dirs = ["agents", "skills", "commands"]
            for base_dir in base_dirs:
                (self.target_dir / base_dir).mkdir(parents=True, exist_ok=True)

        try:
            cmd = [
                "stow",
                "--dir",
                str(self.registry_path),
                "--target",
                str(self.target_dir),
                package_name,
            ]

            if dry_run:
                cmd.append("--simulate")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if dry_run:
                console.print(f"[yellow]Dry run:[/yellow] Would stow {package_name}")
                if result.stdout if "result" in locals() else "":
                    console.print(result.stdout)

            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error using stow:[/red] {e.stderr}")
            return False

    def _uninstall_with_stow(self, package_name: str, dry_run: bool = False) -> bool:
        """Uninstall using GNU Stow."""
        try:
            cmd = [
                "stow",
                "--dir",
                str(self.registry_path),
                "--target",
                str(self.target_dir),
                "-D",  # Delete
                package_name,
            ]

            if dry_run:
                cmd.append("--simulate")

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            if dry_run:
                console.print(f"[yellow]Dry run:[/yellow] Would unstow {package_name}")

            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error using stow:[/red] {e.stderr}")
            return False

    def _install_with_symlinks(self, package_name: str, dry_run: bool = False) -> bool:
        """Fallback: Install using manual symlinks."""
        package_path = self.registry_path / package_name

        if not package_path.exists():
            console.print(f"[red]Error:[/red] Package directory not found: {package_path}")
            return False

        # Create target directory and base component directories
        if not dry_run:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            # Ensure base directories exist
            base_dirs = ["agents", "skills", "commands"]
            for base_dir in base_dirs:
                (self.target_dir / base_dir).mkdir(parents=True, exist_ok=True)

        # Walk through package directory and create symlinks
        success = True
        for item in package_path.rglob("*"):
            if item.is_file():
                # Calculate relative path from package root
                rel_path = item.relative_to(package_path)
                target_path = self.target_dir / rel_path

                if dry_run:
                    console.print(f"[yellow]Would link:[/yellow] {target_path} -> {item}")
                else:
                    # Create parent directories
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Check for conflicts
                    if target_path.exists() and not target_path.is_symlink():
                        console.print(
                            f"[yellow]Warning:[/yellow] {target_path} exists and is not a symlink, skipping"
                        )
                        continue

                    # Create symlink
                    if target_path.is_symlink():
                        target_path.unlink()
                    target_path.symlink_to(item)

        return success

    def _uninstall_with_symlinks(self, package_name: str, dry_run: bool = False) -> bool:
        """Fallback: Uninstall using manual symlink removal."""
        package_path = self.registry_path / package_name

        if not package_path.exists():
            console.print(f"[yellow]Warning:[/yellow] Package directory not found: {package_path}")
            return True

        # Find and remove symlinks that point to this package
        for item in package_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(package_path)
                target_path = self.target_dir / rel_path

                if target_path.is_symlink() and target_path.resolve() == item.resolve():
                    if dry_run:
                        console.print(f"[yellow]Would remove:[/yellow] {target_path}")
                    else:
                        target_path.unlink()
                        console.print(f"Removed: {target_path}")

        return True

    def verify_symlinks(self) -> List[Path]:
        """Find broken symlinks in target directory."""
        broken = []

        if not self.target_dir.exists():
            return broken

        for item in self.target_dir.rglob("*"):
            if item.is_symlink() and not item.exists():
                broken.append(item)

        return broken

    def clean_broken_symlinks(self, dry_run: bool = False) -> int:
        """Remove broken symlinks."""
        broken = self.verify_symlinks()

        if dry_run:
            for link in broken:
                console.print(f"[yellow]Would remove:[/yellow] {link}")
        else:
            for link in broken:
                link.unlink()
                console.print(f"Removed broken link: {link}")

        return len(broken)

    def detect_installed_components(self) -> Dict[str, List[str]]:
        """
        Detect installed components by scanning symlinks in target directory.

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
                if item.is_symlink() and item.suffix == ".md" and not item.name.startswith("."):
                    # Primary agent
                    component_id = item.stem
                    installed["agents"].append(component_id)

            # Check for subagents directory
            subagent_dir = agent_dir / "subagents"
            if subagent_dir.exists() and subagent_dir.is_symlink():
                # Subagents directory is symlinked, find all subagents
                try:
                    target = subagent_dir.resolve()
                    for category_dir in target.iterdir():
                        if category_dir.is_dir():
                            for subagent_file in category_dir.glob("*.md"):
                                if not subagent_file.name.startswith("."):
                                    installed["subagents"].append(subagent_file.stem)
                except Exception:
                    pass

        # Check skill directory
        skill_dir = self.target_dir / "skills"
        if skill_dir.exists():
            for item in skill_dir.iterdir():
                if item.is_symlink() and item.is_dir():
                    # Skill directory
                    installed["skills"].append(item.name)

        # Check command directory
        command_dir = self.target_dir / "commands"
        if command_dir.exists():
            if command_dir.is_symlink():
                # Entire command directory is symlinked
                try:
                    target = command_dir.resolve()
                    for cmd_file in target.glob("*.md"):
                        if not cmd_file.name.startswith("."):
                            installed["commands"].append(cmd_file.stem)
                except Exception:
                    pass
            else:
                # Individual command files are symlinked
                for item in command_dir.iterdir():
                    if item.is_symlink() and item.suffix == ".md" and not item.name.startswith("."):
                        installed["commands"].append(item.stem)

        return installed
