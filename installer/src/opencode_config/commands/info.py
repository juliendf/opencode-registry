"""
Show component information.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from ..config import Config
from ..utils.manifest import ManifestParser
from ..utils.installed_db import InstalledDB

console = Console()


@click.command()
@click.argument("component_id", required=False)
def info(component_id: str):
    """Show detailed information about a component.

    COMPONENT_ID is the unique identifier for the component (e.g., build-general, mcp-builder).
    """
    config = Config()
    db = InstalledDB()

    # If no component_id provided, show helpful message
    if not component_id:
        console.print("[red]Error:[/red] Missing component ID\n")
        console.print("[cyan]Usage:[/cyan]")
        console.print("  opencode-config info <component-id>\n")
        console.print("[cyan]Examples:[/cyan]")
        console.print("  opencode-config info build-general")
        console.print("  opencode-config info mcp-builder")
        console.print("  opencode-config info terraform-expert\n")
        console.print(
            "[dim]Tip: Run 'opencode-config list' to see all available component IDs[/dim]"
        )
        return

    # Detect or get registry path
    registry_path = config.registry_path or config.detect_registry_path()

    if not registry_path:
        console.print("[red]Error:[/red] Could not find registry.")
        return

    opencode_dir = registry_path / "opencode"

    # Search for component
    manifest = None
    component_path = None

    # Check agents
    agent_file = opencode_dir / "agents" / f"{component_id}.md"
    if agent_file.exists():
        manifest = ManifestParser.create_from_md(agent_file, "agent")
        component_path = agent_file

    # Check subagents
    if not manifest:
        subagent_dir = opencode_dir / "agents" / "subagents"
        for category_dir in subagent_dir.glob("*/"):
            subagent_file = category_dir / f"{component_id}.md"
            if subagent_file.exists():
                manifest = ManifestParser.create_from_md(subagent_file, "subagent")
                component_path = subagent_file
                break

    # Check skills
    if not manifest:
        skill_path = opencode_dir / "skills" / component_id / "SKILL.md"
        if skill_path.exists():
            manifest = ManifestParser.create_from_md(skill_path, "skill")
            component_path = skill_path

    # Check commands
    if not manifest:
        command_file = opencode_dir / "commands" / f"{component_id}.md"
        if command_file.exists():
            manifest = ManifestParser.create_from_md(command_file, "command")
            component_path = command_file

    if not manifest:
        console.print(f"[red]Error:[/red] Component '{component_id}' not found")
        return

    # Check if installed
    is_installed = db.is_installed(component_id)

    # Display information
    info_text = f"""
# {manifest.name}

**ID:** {manifest.id}
**Type:** {manifest.type}
**Version:** {manifest.version}
**Author:** {manifest.author or 'Unknown'}
**Installed:** {'✓ Yes' if is_installed else '✗ No'}

## Description

{manifest.description}

## Tags

{', '.join(manifest.tags) if manifest.tags else 'None'}

## Location

`{component_path}`

## Installation

```bash
opencode-config install {manifest.id}
```
"""

    console.print(
        Panel(Markdown(info_text), title=f"Component Info: {component_id}", border_style="blue")
    )
