"""
Manage model tier configuration.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from ..config import Config

console = Console()


@click.command()
@click.option("--list", "-l", "list_tiers", is_flag=True, help="List configured model tiers")
@click.option(
    "--set",
    "set_tier",
    nargs=2,
    type=str,
    metavar="TIER MODEL",
    help="Set tier model (e.g., --set high 'github-copilot/claude-sonnet-4.5')",
)
@click.option("--wizard", "-w", is_flag=True, help="Interactive tier configuration wizard")
@click.option("--reset", is_flag=True, help="Reset to default tier configuration")
def models(list_tiers: bool, set_tier: tuple, wizard: bool, reset: bool):
    """
    Manage model tier configuration.

    Model tiers allow you to configure different models for different complexity levels:
    - high: Complex reasoning tasks (architecture, design planning)
    - medium: General coding tasks (implementation, code review)
    - low: Simple tasks (documentation, commit messages)

    Examples:
      opencode-config models --list
      opencode-config models --set high "github-copilot/claude-sonnet-4.5"
      opencode-config models --wizard
      opencode-config models --reset
    """
    cfg = Config()

    # Handle list
    if list_tiers:
        _display_tiers(cfg)
        return

    # Handle reset
    if reset:
        if Confirm.ask("[yellow]Reset all tiers to defaults (clears configuration)?[/yellow]"):
            from ..config import DEFAULT_CONFIG

            for tier in ["high", "medium", "low"]:
                cfg.set_model_tier(tier, None)
            console.print("[green]✓[/green] Model tiers cleared")
            _display_tiers(cfg)
        else:
            console.print("[dim]Reset cancelled[/dim]")
        return

    # Handle set
    if set_tier:
        tier_name, model = set_tier
        if tier_name not in ["high", "medium", "low"]:
            console.print(
                f"[red]Error:[/red] Invalid tier '{tier_name}'. Must be: high, medium, or low"
            )
            return

        cfg.set_model_tier(tier_name, model)
        console.print(f"[green]✓[/green] Set [cyan]{tier_name}[/cyan] tier to: {model}")
        return

    # Handle wizard
    if wizard:
        run_wizard(cfg)
        return

    # No action specified
    console.print("[yellow]No action specified. Use --help for options[/yellow]")
    console.print("\n[dim]Quick examples:[/dim]")
    console.print("  opencode-config models --list")
    console.print("  opencode-config models --wizard")
    console.print('  opencode-config models --set high "your-model"')


def _display_tiers(cfg: Config):
    """Display current tier configuration."""
    table = Table(title="Model Tier Configuration")
    table.add_column("Tier", style="cyan", width=10)
    table.add_column("Use Case", style="dim")
    table.add_column("Model", style="green")

    tiers = cfg.list_model_tiers()

    tier_descriptions = {
        "high": "Complex reasoning (architecture, design)",
        "medium": "General coding (implementation, review)",
        "low": "Simple tasks (docs, commits)",
    }

    for tier in ["high", "medium", "low"]:
        model = tiers.get(tier, "[dim]not configured[/dim]")
        description = tier_descriptions.get(tier, "")
        table.add_row(tier, description, model)

    console.print(table)


def run_wizard(cfg: Config):
    """Run interactive model tier configuration wizard.

    Public so other commands (e.g. install) can invoke it directly.
    """
    console.print("\n[bold cyan]Model Tier Configuration Wizard[/bold cyan]\n")
    console.print(
        "Configure models for each complexity tier. Press Enter to keep current value.\n"
    )
    console.print("[dim]Browse available models at https://models.dev/ or run 'opencode models'[/dim]\n")

    current_tiers = cfg.list_model_tiers()

    tier_prompts = {
        "high": (
            "High tier   - Complex reasoning (architecture, design planning)",
            current_tiers.get("high") or "",
        ),
        "medium": (
            "Medium tier - General coding (implementation, code review)",
            current_tiers.get("medium") or "",
        ),
        "low": (
            "Low tier    - Simple tasks (documentation, commit messages)",
            current_tiers.get("low") or "",
        ),
    }

    new_config = {}

    for tier, (description, default) in tier_prompts.items():
        console.print(f"\n[cyan]{description}[/cyan]")
        model = Prompt.ask(
            f"  Model for [bold]{tier}[/bold] tier",
            default=default if default else None,
            show_default=bool(default),
        )
        new_config[tier] = model

    # Show summary
    console.print("\n[bold]Summary of changes:[/bold]")
    table = Table(show_header=True)
    table.add_column("Tier", style="cyan")
    table.add_column("Current", style="dim")
    table.add_column("→", justify="center")
    table.add_column("New", style="green")

    for tier in ["high", "medium", "low"]:
        current = current_tiers.get(tier, "[not set]")
        new = new_config[tier]
        changed = "✓" if current != new else ""
        table.add_row(tier, current, changed, new)

    console.print(table)

    # Confirm
    if Confirm.ask("\n[yellow]Apply these changes?[/yellow]", default=True):
        for tier, model in new_config.items():
            cfg.set_model_tier(tier, model)
        console.print("[green]✓[/green] Configuration saved successfully!")
    else:
        console.print("[dim]Configuration cancelled[/dim]")
