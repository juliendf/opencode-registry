"""
Show installation status.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from ..config import Config
from ..utils.installed_db import InstalledDB
from ..utils.stow import StowManager

console = Console()


@click.command()
@click.option("--details", "-d", is_flag=True, help="Show detailed information")
def status(details: bool):
    """Show installation status and installed components."""
    config = Config()
    db = InstalledDB()

    # Get configuration
    target_dir = config.target_dir
    registry_path = config.registry_path or config.detect_registry_path()

    # Display system info
    info_text = f"""
**Installation Method:** {db.data.get('installMethod', 'unknown')}
**Target Directory:** {db.data.get('targetDirectory', 'unknown')}
**Registry Path:** {db.data.get('registry', {}).get('path', 'unknown')}
**Last Updated:** {db.data.get('lastUpdated', 'unknown')}
"""

    console.print(Panel(info_text.strip(), title="Installation Info", border_style="blue"))

    # Get installed components
    installed = db.get_all_installed()

    if not installed:
        console.print("\n[yellow]No components installed yet.[/yellow]")
        console.print("\n[dim]Use 'opencode-config install <component>' to get started[/dim]")
        return

    # Create table
    table = Table(title=f"\nInstalled Components ({len(installed)})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Version", style="green")
    table.add_column("Installed", style="yellow")

    if details:
        table.add_column("Method", style="blue")

    for comp in sorted(installed, key=lambda x: (x.get("type", ""), x.get("id", ""))):
        row = [
            comp.get("id", "unknown"),
            comp.get("type", "unknown"),
            comp.get("version", "unknown"),
            comp.get("installedAt", "unknown")[:10] if comp.get("installedAt") else "unknown",
        ]

        if details:
            row.append(comp.get("installMethod", "unknown"))

        table.add_row(*row)

    console.print(table)

    # Show bundles if any
    bundles = db.data.get("bundles", {})
    if bundles:
        console.print("\n[bold]Installed Bundles:[/bold]")
        for bundle_name, bundle_info in bundles.items():
            console.print(
                f"  • {bundle_name} ({len(bundle_info.get('components', []))} components)"
            )

    # Verify symlinks if registry path is available
    if registry_path and target_dir.exists():
        stow_manager = StowManager(registry_path, target_dir)
        broken = stow_manager.verify_symlinks()

        if broken:
            console.print(f"\n[yellow]⚠ Warning:[/yellow] {len(broken)} broken symlink(s) found")
            console.print("[dim]Run 'opencode-config clean' to remove them[/dim]")

    console.print("\n[dim]Use 'opencode-config list' to see available components[/dim]")
