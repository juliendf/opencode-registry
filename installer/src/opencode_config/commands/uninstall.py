"""
Uninstall components.
"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..config import Config
from ..utils.copy import CopyManager
from ..utils.installed_db import InstalledDB

console = Console()


@click.command()
@click.argument("component_id", required=False)
@click.option("--group", "-g", help="Uninstall a bundle/group")
@click.option("--all", "-a", "uninstall_all", is_flag=True, help="Uninstall everything")
@click.option("--dry-run", "-n", is_flag=True, help="Preview changes without uninstalling")
def uninstall(component_id: str, group: str, uninstall_all: bool, dry_run: bool):
    """Uninstall a component, bundle, or everything."""
    config = Config()
    db = InstalledDB()

    # Detect or get registry path
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print("[red]Error:[/red] Could not find registry.")
        return

    # Determine target directory
    target_dir = config.target_dir

    # Initialize CopyManager
    copy_manager = CopyManager(registry_path, target_dir, config)

    console.print(f"[dim]Target directory: {target_dir}[/dim]")
    console.print(f"[dim]Registry path: {registry_path}[/dim]\n")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    # Handle uninstall all
    if uninstall_all:
        console.print("[yellow]⚠ Warning:[/yellow] This will uninstall ALL registry components")

        if not dry_run:
            confirm = console.input("[bold]Are you sure? (yes/no): [/bold]")
            if confirm.lower() not in ["yes", "y"]:
                console.print("[yellow]Cancelled[/yellow]")
                return

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            progress.add_task("Uninstalling all components...", total=None)

            success = copy_manager.uninstall_package("opencode", dry_run=dry_run)

            if success and not dry_run:
                db.data["installed"] = {
                    "agents": {},
                    "subagents": {},
                    "skills": {},
                    "commands": {},
                }
                db.data["bundles"] = {}
                db.log_action("uninstall", ["all"], "copy", "success")
                db.save()

        if success:
            console.print("[green]✓[/green] All components uninstalled successfully!")
        else:
            console.print("[red]✗[/red] Failed to uninstall components")

        return

    # Handle bundle uninstall
    if group:
        bundle_file = registry_path / "bundles" / f"{group}.yaml"
        if not bundle_file.exists():
            console.print(f"[red]Error:[/red] Bundle '{group}' not found")
            return

        console.print(
            "[yellow]Note:[/yellow] Uninstalling a bundle will uninstall ALL registry components"
        )
        console.print("[dim]Individual component uninstall not yet supported[/dim]\n")

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            progress.add_task(f"Uninstalling bundle '{group}'...", total=None)

            success = copy_manager.uninstall_package("opencode", dry_run=dry_run)

            if success and not dry_run:
                db.data["bundles"].pop(group, None)
                db.log_action("uninstall", [group], "copy", "success")
                db.save()

        if success:
            console.print(f"[green]✓[/green] Bundle '{group}' uninstalled successfully!")
        else:
            console.print(f"[red]✗[/red] Failed to uninstall bundle '{group}'")

        return

    # Handle single component uninstall
    if component_id:
        console.print("[yellow]Note:[/yellow] Individual component uninstall not yet supported")
        console.print("[dim]This would uninstall ALL registry components[/dim]\n")
        console.print("Use 'opencode-config uninstall --all' to uninstall everything")
        return

    # No arguments provided
    console.print("[red]Error:[/red] Please specify what to uninstall:")
    console.print("  opencode-config uninstall --all          # Uninstall everything")
    console.print("  opencode-config uninstall --group basic  # Uninstall a bundle")
    console.print("  opencode-config uninstall <component>    # (Not yet supported)")
