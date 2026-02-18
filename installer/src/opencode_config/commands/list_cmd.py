"""
List available components.
"""

import click
from rich.console import Console
from rich.table import Table
from ..config import Config
from ..utils.manifest import ManifestParser

console = Console()


@click.command(name="list")
@click.option("--type", "-t", help="Filter by type (agent, subagent, skill, command)")
@click.option("--tag", help="Filter by tag")
@click.option("--installed", "-i", is_flag=True, help="Show only installed components")
def list_components(type: str, tag: str, installed: bool):
    """List all available components in the registry."""
    from ..utils.installed_db import InstalledDB

    config = Config()
    db = InstalledDB()

    # Detect or get registry path
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print(
            "[red]Error:[/red] Could not find registry. Run from registry directory or set path with 'opencode-config config --registry <path>'"
        )
        return

    opencode_dir = registry_path / "opencode"
    if not opencode_dir.exists():
        console.print(f"[red]Error:[/red] Registry directory not found: {opencode_dir}")
        return

    # Collect components
    components = []

    # Agents
    agent_dir = opencode_dir / "agents"
    if agent_dir.exists():
        for md_file in agent_dir.glob("*.md"):
            manifest = ManifestParser.create_from_md(md_file, "agent")
            if not type or manifest.type == type:
                if not tag or tag in manifest.tags:
                    components.append(manifest)

    # Subagents
    subagent_dir = opencode_dir / "agents" / "subagents"
    if subagent_dir.exists():
        for category_dir in subagent_dir.iterdir():
            if category_dir.is_dir():
                for md_file in category_dir.glob("*.md"):
                    manifest = ManifestParser.create_from_md(md_file, "subagent")
                    if not type or manifest.type == type:
                        if not tag or tag in manifest.tags:
                            components.append(manifest)

    # Skills
    skill_dir = opencode_dir / "skills"
    if skill_dir.exists():
        for skill_folder in skill_dir.iterdir():
            if skill_folder.is_dir():
                skill_md = skill_folder / "SKILL.md"
                if skill_md.exists():
                    manifest = ManifestParser.create_from_md(skill_md, "skill")
                    if not type or manifest.type == type:
                        if not tag or tag in manifest.tags:
                            components.append(manifest)

    # Commands
    command_dir = opencode_dir / "commands"
    if command_dir.exists():
        for md_file in command_dir.glob("*.md"):
            manifest = ManifestParser.create_from_md(md_file, "command")
            if not type or manifest.type == type:
                if not tag or tag in manifest.tags:
                    components.append(manifest)

    # Display results
    if not components:
        console.print("[yellow]No components found matching filters.[/yellow]")
        return

    # Filter by installed if requested
    if installed:
        installed_ids = set()
        for comp_type in db.data["installed"].values():
            installed_ids.update(comp_type.keys())
        components = [c for c in components if c.id in installed_ids]

        if not components:
            console.print("[yellow]No installed components match the filter.[/yellow]")
            return

    table = Table(title=f"Available Components ({len(components)})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Version", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Description", style="white")

    for comp in sorted(components, key=lambda x: (x.type, x.id)):
        # Check if installed and get installed version
        installed_version = db.get_installed_version(comp.id)
        status_icon = "✓" if installed_version else "○"
        status_text = f"{status_icon} {installed_version}" if installed_version else status_icon

        table.add_row(
            comp.id,
            comp.type,
            comp.version,
            status_text,
            comp.description[:50] + "..." if len(comp.description) > 50 else comp.description,
        )

    console.print(table)
    console.print("\n[dim]Use 'opencode-config info <id>' for more details[/dim]")
    console.print("[dim]Legend: ✓ = installed, ○ = not installed[/dim]")
