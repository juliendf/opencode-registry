"""
Install components.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..config import Config
from ..utils.copy import CopyManager
from ..utils.installed_db import InstalledDB
from .models import run_wizard

console = Console()

TIERS = ["high", "medium", "low", "free"]


def _check_model_tiers(config: Config, db: InstalledDB) -> bool:
    """
    Ensure all model tiers are configured before installing.

    - First run (nothing installed yet): launch the interactive wizard automatically.
    - Subsequent runs with missing tiers: print the commands to fix it and abort.

    Returns True if all tiers are configured and install can proceed.
    """
    missing = [t for t in TIERS if not config.get_model_for_tier(t)]
    if not missing:
        return True

    is_first_run = not db.get_all_installed()

    if is_first_run:
        console.print(
            "[cyan]Welcome![/cyan] Before installing, let's configure which models "
            "to use for each complexity tier.\n"
        )
        run_wizard(config)
        # Re-check after wizard
        missing = [t for t in TIERS if not config.get_model_for_tier(t)]
        if not missing:
            console.print()
            return True
        # User skipped some — fall through to error below

    console.print("[yellow]Model tiers are not fully configured.[/yellow]")
    console.print(
        "Components use tiers ([cyan]high[/cyan] / [cyan]medium[/cyan] / [cyan]low[/cyan] / [cyan]free[/cyan]) "
        "to select a model. Run the following to configure them:\n"
    )
    console.print("[dim]Browse available models at https://models.dev/ or run 'opencode models'[/dim]\n")
    examples = {
        "high":   "github-copilot/claude-sonnet-4.5",
        "medium": "github-copilot/claude-sonnet-4",
        "low":    "github-copilot/claude-haiku-4.5",
        "free":   "github-copilot/gpt-4o-mini",
    }
    for tier in missing:
        console.print(
            f"  opencode-config models --set {tier} [dim]{examples[tier]}[/dim]"
        )
    console.print(
        "\n[dim]Or configure all tiers at once:[/dim]"
        "\n  opencode-config models --wizard"
    )
    return False


@click.command()
@click.argument("component_id", required=False)
@click.option("--group", "-g", help="Install a bundle/group (e.g., basic, intermediate)")
@click.option("--dry-run", "-n", is_flag=True, help="Preview changes without installing")
@click.option("--target", "-t", help="Custom installation target directory")
@click.option("--model", "-m", help="Override model for component installation")
def install(component_id: str, group: str, dry_run: bool, target: str, model: str):
    """Install a component or bundle."""
    config = Config()
    db = InstalledDB()

    # Detect or get registry path
    # If user has explicitly set registry_path in config, use it
    # Otherwise, auto-detect from current directory (don't save)
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print("[red]Error:[/red] Could not find registry. Run from registry directory.")
        console.print("[dim]Tip: Set registry path with 'opencode-config config --registry /path/to/registry'[/dim]")
        return

    # Check model tiers are configured (skip if user supplies --model override)
    if not model and not dry_run:
        if not _check_model_tiers(config, db):
            return

    # Only save registry path if it was explicitly set by user, not auto-detected
    # This allows auto-detection to work with git worktrees

    # Determine target directory
    target_dir = Path(target) if target else config.target_dir
    target_dir = target_dir.expanduser()

    # Ensure target exists
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    # Initialize CopyManager
    copy_manager = CopyManager(registry_path, target_dir, config)
    install_method = "copy"

    console.print(f"[dim]Installation method: {install_method}[/dim]")
    console.print(f"[dim]Target directory: {target_dir}[/dim]")
    console.print(f"[dim]Registry path: {registry_path}[/dim]")
    if model:
        console.print(f"[dim]Model override: {model}[/dim]")
    console.print()

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    # Handle bundle installation
    if group:
        bundle_file = registry_path / "bundles" / f"{group}.yaml"
        if not bundle_file.exists():
            console.print(f"[red]Error:[/red] Bundle '{group}' not found at {bundle_file}")
            return

        import yaml

        with open(bundle_file, "r") as f:
            bundle_data = yaml.safe_load(f)

        components = bundle_data.get("components", [])
        console.print(f"[cyan]Installing bundle:[/cyan] {bundle_data.get('name', group)}")
        console.print(f"[dim]{bundle_data.get('description', '')}[/dim]\n")
        console.print(f"Components: {', '.join(components)}\n")

        # For now, install entire opencode directory
        # TODO: Implement selective component installation
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}")
        ) as progress:
            progress.add_task(f"Installing bundle '{group}'...", total=None)

            success = copy_manager.install_package("opencode", dry_run=dry_run, model_override=model)

            if success and not dry_run:
                db.set_install_method(install_method)
                db.set_target_directory(str(target_dir))
                db.set_registry_path(str(registry_path))
                db.add_bundle(group, components)

                # Detect and sync actual installed components
                detected = copy_manager.detect_installed_components()
                db.sync_from_detected(detected, install_method)

                db.log_action("install", [group], install_method, "success")

        # Print result after spinner has stopped
        if success:
            console.print(f"[green]✓[/green] Bundle '{group}' installed successfully!")
        else:
            console.print(f"[red]✗[/red] Failed to install bundle '{group}'")

        return

    # Handle single component installation
    if not component_id:
        console.print("[red]Error:[/red] Please specify a component ID or use --group\n")
        console.print("[cyan]Usage examples:[/cyan]")
        console.print("  opencode-config install --group basic")
        console.print("  opencode-config install --group intermediate")
        console.print("  opencode-config install --group advanced")
        console.print("  opencode-config install <component-id>\n")
        console.print("[dim]Available bundles:[/dim]")
        console.print("  • basic         - Essential components (5 components)")
        console.print("  • intermediate  - Common workflow components (10+ components)")
        console.print("  • advanced      - Full component library (63 components)\n")
        console.print("[dim]Tip: Run 'opencode-config list' to see all available components[/dim]")
        return

    # Check if already installed
    if db.is_installed(component_id) and not dry_run:
        console.print(f"[yellow]Warning:[/yellow] Component '{component_id}' is already installed")
        console.print("Use 'opencode-config update' to update it")
        return

    # Find component

    # Search for component (simplified - installs whole opencode dir)
    # TODO: Implement selective installation

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task(f"Installing '{component_id}'...", total=None)

        success = copy_manager.install_package("opencode", dry_run=dry_run, model_override=model)

        if success and not dry_run:
            db.set_install_method(install_method)
            db.set_target_directory(str(target_dir))
            db.set_registry_path(str(registry_path))

            # Detect and sync actual installed components
            detected = copy_manager.detect_installed_components()
            db.sync_from_detected(detected, install_method)

            db.log_action("install", [component_id], install_method, "success")

    # Print result after spinner has stopped
    if success:
        console.print(f"[green]✓[/green] Component '{component_id}' installed successfully!")
        console.print(f"[dim]Installed to: {target_dir}[/dim]")
    else:
        console.print(f"[red]✗[/red] Failed to install component '{component_id}'")
