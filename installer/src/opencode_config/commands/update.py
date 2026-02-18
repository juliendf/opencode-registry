"""
Update installed components.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..config import Config
from ..utils.stow import StowManager
from ..utils.installed_db import InstalledDB
from ..utils.manifest import ManifestParser
from ..utils.version import is_newer_version

console = Console()


@click.command()
@click.argument("component_id", required=False)
@click.option("--all", "-a", is_flag=True, help="Update all installed components")
@click.option(
    "--dry-run", "-n", is_flag=True, help="Show what would be updated without making changes"
)
def update(component_id: str, all: bool, dry_run: bool):
    """Update installed components to latest available versions.

    COMPONENT_ID is the unique identifier for the component to update.
    """
    config = Config()
    db = InstalledDB()

    # Detect or get registry path
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print("[red]Error:[/red] Could not find registry.")
        return

    opencode_dir = registry_path / "opencode"

    # If no arguments, show help
    if not component_id and not all:
        console.print("[red]Error:[/red] Please specify a component ID or use --all\n")
        console.print("[cyan]Usage:[/cyan]")
        console.print("  opencode-config update <component-id>")
        console.print("  opencode-config update --all\n")
        console.print("[cyan]Examples:[/cyan]")
        console.print("  opencode-config update mcp-builder")
        console.print("  opencode-config update --all --dry-run\n")
        console.print("[dim]Tip: Run 'opencode-config status' to see installed versions[/dim]")
        return

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    # Get all installed components
    installed = db.get_all_installed()

    if not installed:
        console.print("[yellow]No components installed yet.[/yellow]")
        return

    # Filter to specific component if requested
    if component_id:
        installed = [c for c in installed if c["id"] == component_id]
        if not installed:
            console.print(f"[red]Error:[/red] Component '{component_id}' is not installed")
            return

    # Check for updates
    updates_available = []

    for component in installed:
        comp_id = component["id"]
        comp_type = component["type"]
        installed_version = component.get("version", "unknown")

        # Find component in registry and get available version
        available_version = None
        manifest = None

        if comp_type == "agent":
            agent_file = opencode_dir / "agents" / f"{comp_id}.md"
            if agent_file.exists():
                manifest = ManifestParser.create_from_md(agent_file, "agent")
                available_version = manifest.version

        elif comp_type == "subagent":
            # Search in subagent directories
            subagent_dir = opencode_dir / "agents" / "subagents"
            for category_dir in subagent_dir.glob("*/"):
                subagent_file = category_dir / f"{comp_id}.md"
                if subagent_file.exists():
                    manifest = ManifestParser.create_from_md(subagent_file, "subagent")
                    available_version = manifest.version
                    break

        elif comp_type == "skill":
            skill_file = opencode_dir / "skills" / comp_id / "SKILL.md"
            if skill_file.exists():
                manifest = ManifestParser.create_from_md(skill_file, "skill")
                available_version = manifest.version

        elif comp_type == "command":
            command_file = opencode_dir / "commands" / f"{comp_id}.md"
            if command_file.exists():
                manifest = ManifestParser.create_from_md(command_file, "command")
                available_version = manifest.version

        # Check if update available
        if available_version and installed_version != "unknown":
            try:
                if is_newer_version(available_version, installed_version):
                    updates_available.append(
                        {
                            "id": comp_id,
                            "type": comp_type,
                            "installed": installed_version,
                            "available": available_version,
                        }
                    )
            except Exception:
                # Version comparison failed, skip
                pass

    # Display results
    if not updates_available:
        console.print("[green]✓[/green] All components are up to date!")
        return

    # Show updates table
    table = Table(title=f"Updates Available ({len(updates_available)})")
    table.add_column("Component", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Installed", style="yellow")
    table.add_column("Available", style="green")

    for update in updates_available:
        table.add_row(update["id"], update["type"], update["installed"], update["available"])

    console.print(table)
    console.print()

    if dry_run:
        console.print("[yellow]Dry run complete. No changes made.[/yellow]")
        return

    # Perform update (reinstall entire opencode package)
    console.print("[cyan]Updating components...[/cyan]\n")

    target_dir = Path(config.target_dir).expanduser()
    stow_manager = StowManager(registry_path, target_dir)
    install_method = stow_manager.get_method()

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task("Updating...", total=None)

        # Uninstall and reinstall to pick up new versions
        stow_manager.uninstall_package("opencode", dry_run=False)
        success = stow_manager.install_package("opencode", dry_run=False)

        if success:
            # Sync database with new versions
            detected = stow_manager.detect_installed_components()

            # Collect component versions from registry
            component_versions = {}
            for comp_type_key, comp_ids in detected.items():
                comp_type = comp_type_key.rstrip("s")
                for comp_id in comp_ids:
                    # Get version from manifest
                    if comp_type == "agent":
                        agent_file = opencode_dir / "agents" / f"{comp_id}.md"
                        if agent_file.exists():
                            m = ManifestParser.create_from_md(agent_file, "agent")
                            component_versions[comp_id] = m.version
                    elif comp_type == "subagent":
                        subagent_dir = opencode_dir / "agents" / "subagents"
                        for category_dir in subagent_dir.glob("*/"):
                            subagent_file = category_dir / f"{comp_id}.md"
                            if subagent_file.exists():
                                m = ManifestParser.create_from_md(subagent_file, "subagent")
                                component_versions[comp_id] = m.version
                                break
                    elif comp_type == "skill":
                        skill_file = opencode_dir / "skills" / comp_id / "SKILL.md"
                        if skill_file.exists():
                            m = ManifestParser.create_from_md(skill_file, "skill")
                            component_versions[comp_id] = m.version
                    elif comp_type == "command":
                        command_file = opencode_dir / "commands" / f"{comp_id}.md"
                        if command_file.exists():
                            m = ManifestParser.create_from_md(command_file, "command")
                            component_versions[comp_id] = m.version

            db.sync_from_detected(detected, install_method, component_versions)
            db.log_action("update", [u["id"] for u in updates_available], install_method, "success")

            console.print(
                f"\n[green]✓[/green] Successfully updated {len(updates_available)} component(s)!"
            )
        else:
            console.print("\n[red]✗[/red] Update failed")
