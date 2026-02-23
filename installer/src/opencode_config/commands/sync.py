"""
Sync database with actual installed components.
"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..config import Config
from ..utils.copy import CopyManager
from ..utils.installed_db import InstalledDB

console = Console()


@click.command()
@click.option("--dry-run", "-n", is_flag=True, help="Preview changes without updating database")
def sync(dry_run: bool):
    """Sync database with actual installed components on disk."""
    config = Config()
    db = InstalledDB()

    # Get configuration
    target_dir = config.target_dir
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print("[red]Error:[/red] Could not find registry path")
        return

    if not target_dir.exists():
        console.print(f"[yellow]Warning:[/yellow] Target directory does not exist: {target_dir}")
        console.print("Nothing to sync.")
        return

    console.print(f"[dim]Scanning installed components in {target_dir}...[/dim]\n")

    # Initialize CopyManager and detect components
    copy_manager = CopyManager(registry_path, target_dir, config)

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task("Detecting installed components...", total=None)
        detected = copy_manager.detect_installed_components()

    # Calculate totals
    total_agents = len(detected.get("agents", []))
    total_subagents = len(detected.get("subagents", []))
    total_skills = len(detected.get("skills", []))
    total_commands = len(detected.get("commands", []))
    total_components = total_agents + total_subagents + total_skills + total_commands

    # Display findings
    console.print("[bold]Detected Components:[/bold]")
    console.print(f"  • Agents: {total_agents}")
    console.print(f"  • Subagents: {total_subagents}")
    console.print(f"  • Skills: {total_skills}")
    console.print(f"  • Commands: {total_commands}")
    console.print(f"  [bold]Total: {total_components}[/bold]\n")

    if dry_run:
        console.print("[yellow]DRY RUN:[/yellow] Database would be updated with these components")
        return

    # Sync database
    db.sync_from_detected(detected, "copy")

    console.print("[green]✓[/green] Database synced successfully!")
    console.print("\n[dim]Use 'opencode-config status' to view installation details[/dim]")
