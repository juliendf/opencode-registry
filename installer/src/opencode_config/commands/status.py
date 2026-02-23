"""
Show installation status.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from ..config import Config
from ..utils.installed_db import InstalledDB

console = Console()


@click.command()
@click.option("--details", "-d", is_flag=True, help="Show detailed information")
def status(details: bool):
    """Show installation status and installed components."""
    config = Config()
    db = InstalledDB()

    # Display system info
    info_text = (
        f"**Installation Method:** {db.data.get('installMethod', 'copy')}\n"
        f"**Target Directory:** {db.data.get('targetDirectory', 'unknown')}\n"
        f"**Registry Path:** {db.data.get('registry', {}).get('path', 'unknown')}\n"
        f"**Last Updated:** {db.data.get('lastUpdated', 'unknown')}"
    )

    console.print(Panel(info_text.strip(), title="Installation Info", border_style="blue"))

    # Show model tiers
    tiers = config.list_model_tiers()
    tier_table = Table(title="Model Tiers", show_header=True)
    tier_table.add_column("Tier", style="cyan", width=10)
    tier_table.add_column("Model", style="green")

    for tier in ["high", "medium", "low"]:
        tier_table.add_row(tier, tiers.get(tier, "[dim]not configured[/dim]"))

    console.print(tier_table)

    # Get installed components
    installed = db.get_all_installed()

    if not installed:
        console.print("\n[yellow]No components installed yet.[/yellow]")
        console.print("\n[dim]Use 'opencode-config install --group basic' to get started[/dim]")
        return

    # Create components table
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
            row.append(comp.get("installMethod", "copy"))

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

    console.print("\n[dim]Use 'opencode-config models --list' to configure model tiers[/dim]")
    console.print("[dim]Use 'opencode-config list' to see available components[/dim]")
