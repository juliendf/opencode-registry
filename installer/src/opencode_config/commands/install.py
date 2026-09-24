"""
Install components.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import Config
from ..utils.copy import CopyManager
from ..utils.installed_db import InstalledDB
from .models import run_wizard

console = Console()

TIERS = ["high", "medium", "low", "free"]


def _check_model_tiers(config: Config, db: InstalledDB):
    """
    Ensure model tiers are configured before installing (advisory only).

    - First run: launch wizard automatically but never block install.
    - Subsequent runs with missing tiers: print notice, proceed anyway.
    - Unconfigured tiers: model_tier line removed at install, inherits caller model.
    """
    missing = [t for t in TIERS if not config.get_model_for_tier(t)]
    if not missing:
        return

    is_first_run = not db.get_all_installed()

    if is_first_run:
        console.print(
            "[cyan]Welcome![/cyan] Model tiers are optional. "
            "Configure now or skip — components will inherit the calling agent's model.\n"
        )
        run_wizard(config)
        # Re-check after wizard
        missing = [t for t in TIERS if not config.get_model_for_tier(t)]
        if not missing:
            console.print()
            return

    console.print(
        "[dim]Some model tiers not configured. "
        "Components will inherit the calling agent's model. "
        "Run 'opencode-config models --wizard' to configure later.[/dim]\n"
    )


@click.command()
@click.argument("component_id", required=False)
@click.option("--group", "-g", help="Install a bundle/group (e.g., basic, intermediate)")
@click.option("--dry-run", "-n", is_flag=True, help="Preview changes without installing")
@click.option("--target", "-t", help="Custom installation target directory")
@click.option("--model", "-m", help="Override model for component installation")
@click.option(
    "--inherit-model",
    is_flag=True,
    help="Remove model selectors so components inherit the active session model",
)
def install(
    component_id: str,
    group: str,
    dry_run: bool,
    target: str,
    model: str,
    inherit_model: bool,
):
    """Install a component or bundle."""
    if model and inherit_model:
        raise click.UsageError("--model cannot be used with --inherit-model")

    config = Config()
    db = InstalledDB()

    # Detect or get registry path
    # If user has explicitly set registry_path in config, use it
    # Otherwise, auto-detect from current directory (don't save)
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print("[red]Error:[/red] Could not find registry. Run from registry directory.")
        console.print(
            "[dim]Tip: Set registry path with 'opencode-config config --registry /path/to/registry'[/dim]"
        )
        return

    # Model tiers are optional — wizard runs on first install but never blocks
    if not model and not inherit_model and not dry_run:
        _check_model_tiers(config, db)

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
    if inherit_model:
        console.print(
            "[dim]Model selectors will be removed; components inherit the active session model[/dim]"
        )
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

            success = copy_manager.install_package(
                "opencode",
                dry_run=dry_run,
                model_override=model,
                inherit_model=inherit_model,
            )

            if success and not dry_run:
                db.set_install_method(install_method)
                db.set_target_directory(str(target_dir))
                db.set_registry_path(str(registry_path))
                db.add_bundle(group, components)

                # Detect and sync actual installed components
                detected = copy_manager.detect_installed_components()
                db.sync_from_detected(
                    detected,
                    install_method,
                    component_fingerprints=copy_manager.get_component_fingerprints(detected),
                )

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

        success = copy_manager.install_package(
            "opencode",
            dry_run=dry_run,
            model_override=model,
            inherit_model=inherit_model,
        )

        if success and not dry_run:
            db.set_install_method(install_method)
            db.set_target_directory(str(target_dir))
            db.set_registry_path(str(registry_path))

            # Detect and sync actual installed components
            detected = copy_manager.detect_installed_components()
            db.sync_from_detected(
                detected,
                install_method,
                component_fingerprints=copy_manager.get_component_fingerprints(detected),
            )

            db.log_action("install", [component_id], install_method, "success")

    # Print result after spinner has stopped
    if success:
        console.print(f"[green]✓[/green] Component '{component_id}' installed successfully!")
        console.print(f"[dim]Installed to: {target_dir}[/dim]")
    else:
        console.print(f"[red]✗[/red] Failed to install component '{component_id}'")
