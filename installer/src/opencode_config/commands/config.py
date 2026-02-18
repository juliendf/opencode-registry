"""
Manage configuration.
"""

import click
from rich.console import Console
from rich.table import Table
from ..config import Config

console = Console()


@click.command()
@click.option("--list", "-l", "list_config", is_flag=True, help="List current configuration")
@click.option("--target", "-t", help="Set target directory")
@click.option("--registry", "-r", help="Set registry path (use 'auto' to enable auto-detection)")
def config(list_config: bool, target: str, registry: str):
    """Manage opencode-config configuration."""
    cfg = Config()

    if list_config:
        table = Table(title="Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in cfg.data.items():
            display_value = str(value) if value is not None else "[dim]auto-detect[/dim]"
            table.add_row(key, display_value)

        console.print(table)
        return

    if target:
        cfg.set("target", target)
        console.print(f"[green]✓[/green] Target directory set to: {target}")

    if registry is not None:
        if registry.lower() == "auto":
            cfg.set("registry_path", None)
            console.print(f"[green]✓[/green] Registry path set to auto-detect from current directory")
        else:
            cfg.set("registry_path", registry)
            console.print(f"[green]✓[/green] Registry path set to: {registry}")

    if not list_config and not target and registry is None:
        console.print("[yellow]No action specified. Use --help for options[/yellow]")
