"""
OpenCode Registry CLI - Manage OpenCode components with ease.
"""

import click
from rich.console import Console

from .commands import install, list_cmd, status, info, uninstall, config, sync, update, models

console = Console()

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="0.2.0", prog_name="opencode-config")
def main():
    """
    OpenCode Registry - Component management for OpenCode agents, skills, and commands.

    Manage installation, updates, and creation of OpenCode components.
    """
    pass


# Register commands
main.add_command(install.install)
main.add_command(list_cmd.list_components)
main.add_command(status.status)
main.add_command(info.info)
main.add_command(uninstall.uninstall)
main.add_command(update.update)
main.add_command(sync.sync)
main.add_command(config.config)
main.add_command(models.models)


if __name__ == "__main__":
    main()
