"""
Update installed components.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..config import Config
from ..utils.copy import CopyManager
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
@click.option(
    "--inherit-model",
    is_flag=True,
    help="Remove model selectors so components inherit the active session model",
)
def update(component_id: str, all: bool, dry_run: bool, inherit_model: bool):
    """Update installed components to latest available versions.

    Re-copies the registry package when updates are found, applying configured tiers unless inheritance is requested.

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

    # Get all installed components from database
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

    # Detect what's actually on disk
    target_dir = Path(config.target_dir).expanduser()
    copy_manager = CopyManager(registry_path, target_dir, config)
    detected = copy_manager.detect_installed_components()

    # Build set of component IDs actually present on disk
    on_disk = set()
    for comp_type, comp_ids in detected.items():
        on_disk.update(comp_ids)

    # Check for missing components (in DB but not on disk)
    missing_components = []
    for component in installed:
        comp_id = component["id"]
        if comp_id not in on_disk:
            missing_components.append(
                {
                    "id": comp_id,
                    "type": component["type"],
                    "reason": "missing from disk",
                }
            )

    # Check for version updates
    updates_available = []

    for component in installed:
        comp_id = component["id"]
        comp_type = component["type"]
        installed_version = component.get("version", "unknown")
        if comp_id not in on_disk:
            continue

        # Find component in registry and get available version
        available_version = None
        manifest = None

        if comp_type == "agent":
            agent_file = opencode_dir / "agents" / f"{comp_id}.md"
            if agent_file.exists():
                manifest = ManifestParser.create_from_md(agent_file, "agent")
                available_version = manifest.version

        elif comp_type == "subagent":
            subagent_file = opencode_dir / "agents" / "subagents" / f"{comp_id}.md"
            if subagent_file.exists():
                manifest = ManifestParser.create_from_md(subagent_file, "subagent")
                available_version = manifest.version

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

        version_changed = False
        if (
            available_version
            and installed_version
            and installed_version != "N/A"
            and available_version != "N/A"
        ):
            try:
                version_changed = is_newer_version(available_version, installed_version)
            except (AttributeError, TypeError, ValueError) as error:
                console.print(
                    f"[yellow]Warning:[/yellow] Could not compare versions for {comp_id}: {error}"
                )

        source_fingerprint = copy_manager.get_component_fingerprint(comp_type, comp_id)
        installed_fingerprint = component.get("sourceFingerprint")
        source_changed = bool(source_fingerprint) and source_fingerprint != installed_fingerprint
        if version_changed or source_changed:
            updates_available.append(
                {
                    "id": comp_id,
                    "type": comp_type,
                    "installed": installed_version,
                    "available": available_version or "N/A",
                    "source_changed": source_changed,
                }
            )

    # Display results
    total_changes = len(missing_components) + len(updates_available)

    if total_changes == 0:
        console.print("[green]✓[/green] All components are up to date and present!")
        return

    # Show missing components
    if missing_components:
        console.print(f"[yellow]Missing Components ({len(missing_components)}):[/yellow]")
        for m in missing_components:
            console.print(f"  • {m['id']} ([dim]{m['type']}[/dim]) - {m['reason']}")
        console.print()

    # Show version updates
    if updates_available:
        table = Table(title=f"Updates Available ({len(updates_available)})")
        table.add_column("Component", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Installed", style="yellow")
        table.add_column("Available", style="green")

        for u in updates_available:
            table.add_row(u["id"], u["type"], u["installed"], u["available"])

        console.print(table)
        console.print()

    if dry_run:
        console.print("[yellow]Dry run complete. No changes made.[/yellow]")
        return

    # Perform update — re-copy and re-apply model tiers
    console.print("[cyan]Updating components...[/cyan]")
    if inherit_model:
        console.print("[dim]Model selectors will be removed for this update[/dim]\n")
    else:
        console.print("[dim]Model tiers will be re-applied from current configuration[/dim]\n")

    target_dir = Path(config.target_dir).expanduser()
    copy_manager = CopyManager(registry_path, target_dir, config)

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task("Updating...", total=None)

        # Uninstall then reinstall to pick up registry changes + re-apply model tiers
        copy_manager.uninstall_package("opencode", dry_run=False)
        success = copy_manager.install_package(
            "opencode", dry_run=False, inherit_model=inherit_model
        )

        if success:
            detected_after = copy_manager.detect_installed_components()

            # Collect component versions from registry
            component_versions = {}
            for comp_type_key, comp_ids in detected_after.items():
                comp_type = comp_type_key.rstrip("s")
                for cid in comp_ids:
                    if comp_type == "agent":
                        f = opencode_dir / "agents" / f"{cid}.md"
                        if f.exists():
                            component_versions[cid] = ManifestParser.create_from_md(
                                f, "agent"
                            ).version
                    elif comp_type == "subagent":
                        f = opencode_dir / "agents" / "subagents" / f"{cid}.md"
                        if f.exists():
                            component_versions[cid] = ManifestParser.create_from_md(
                                f, "subagent"
                            ).version
                    elif comp_type == "skill":
                        f = opencode_dir / "skills" / cid / "SKILL.md"
                        if f.exists():
                            component_versions[cid] = ManifestParser.create_from_md(
                                f, "skill"
                            ).version
                    elif comp_type == "command":
                        f = opencode_dir / "commands" / f"{cid}.md"
                        if f.exists():
                            component_versions[cid] = ManifestParser.create_from_md(
                                f, "command"
                            ).version

            db.sync_from_detected(
                detected_after,
                "copy",
                component_versions,
                component_fingerprints=copy_manager.get_component_fingerprints(detected_after),
            )

            # Log all affected components
            affected = [m["id"] for m in missing_components] + [u["id"] for u in updates_available]
            db.log_action("update", affected, "copy", "success")

    if success:
        parts = []
        if missing_components:
            parts.append(f"restored {len(missing_components)} missing")
        if updates_available:
            parts.append(f"updated {len(updates_available)}")

        summary = " and ".join(parts) if parts else "updated 0"
        console.print(f"[green]✓[/green] Successfully {summary} component(s)!")
    else:
        console.print("[red]✗[/red] Update failed")
