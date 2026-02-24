# OpenCode Registry - Quick Reference

**One-page command reference for OpenCode Registry CLI**

## 🚀 Installation

```bash
# Clone the registry
git clone https://github.com/yourusername/opencode-registry.git
cd opencode-registry

# Install the CLI (must run from installer/ directory where pyproject.toml lives)
cd installer
pip install -e .
```

## 📋 Essential Commands

### Browse Components

```bash
# List all components
opencode-config list

# Filter by type
opencode-config list --type agent
opencode-config list --type subagent
opencode-config list --type skill

# Show component details
opencode-config info plan-design
opencode-config info kubernetes-expert
```

### Install Components

```bash
# Preview installation (dry-run)
opencode-config install --group basic --dry-run

# Install a bundle
opencode-config install --group basic
opencode-config install --group intermediate
opencode-config install --group advanced

# Install to custom location
opencode-config install --group basic --target /custom/path

# Install with explicit model override (all components use this model)
opencode-config install --group basic --model "github-copilot/claude-sonnet-4.5"
```

### Model Tiers

```bash
# Show current tier configuration
opencode-config models --list

# Set a specific tier
opencode-config models --set high "github-copilot/claude-sonnet-4.5"
opencode-config models --set medium "github-copilot/claude-sonnet-4"
opencode-config models --set low "github-copilot/claude-haiku-4.5"

# Interactive wizard
opencode-config models --wizard

# Reset to defaults
opencode-config models --reset
```

### Check Status & Updates

```bash
# Show installation status
opencode-config status

# Show detailed status with installation method
opencode-config status --details

# Check for updates (safe preview)
opencode-config update --all --dry-run

# Update all components
opencode-config update --all

# Update specific component
    opencode-config update build-code

# Sync database from disk
opencode-config sync

# Preview sync
opencode-config sync --dry-run
```

### Uninstall

```bash
# Preview uninstall
opencode-config uninstall --all --dry-run

# Uninstall everything
opencode-config uninstall --all

# Uninstall a bundle (currently removes all components)
opencode-config uninstall --group basic
```

### Configuration

```bash
# View configuration
opencode-config config --list

# Set custom target directory
opencode-config config --target ~/.config/opencode

# Set registry path
opencode-config config --registry /path/to/registry
```

## 📦 Available Bundles

| Bundle | Components | Description |
|--------|-----------|-------------|
| `basic` | 4 | Essential agents and skills for getting started |
| `intermediate` | 10+ | Extended collection for common workflows |
| `advanced` | 55 | Complete ecosystem with all components |

**Note:** Individual component installation is planned for a future release. Currently, use bundles to install components.

## 🎯 Common Workflows

### First-Time Setup

```bash
# 1. List available components
opencode-config list

# 2. Preview installation
opencode-config install --group basic --dry-run

# 3. Install bundle
opencode-config install --group basic

# 4. Verify installation
opencode-config status
```

### Check What's Installed

```bash
# Quick status
opencode-config status

# Detailed view
opencode-config status --details

# Sync if needed
opencode-config sync
```

### Browse and Install More

```bash
# See what's available
opencode-config list --type subagent

# Get details
opencode-config info kubernetes-expert

# Install more components
opencode-config install --group intermediate
```

### Clean Uninstall

```bash
# Preview what will be removed
opencode-config uninstall --all --dry-run

# Uninstall
opencode-config uninstall --all

# Verify
opencode-config status
```

### Troubleshooting

```bash
# Sync database if status looks wrong
opencode-config sync

# View configuration
opencode-config config --list

# Re-install if needed
opencode-config uninstall --all
opencode-config install --group basic
```

## 📂 File Locations

| Item | Location |
|------|----------|
| **Installed components** | `~/.config/opencode/` |
| **Configuration** | `~/.config/opencode/opencode-registry-config.json` |
| **Installation database** | `~/.config/opencode/opencode-registry-installed.json` |
| **Registry path** | Auto-detected or set via config |

## 🔧 Component Types

| Type | Count | Location |
|------|-------|----------|
| **Primary Agents** | 7 | `agents/*.md` |
| **Subagents** | 43 | `agents/subagents/**/*.md` |
| **Skills** | 3 | `skills/*/` |
| **Commands** | 2 | `commands/*.md` |
| **Total** | **55** | — |

## ⚠️ Important Notes

1. **Copy-based installation:** Files are copied (not symlinked) into `~/.config/opencode/` from the registry

2. **Model tiers:** Configure once with `opencode-config models --wizard`, then every install/update applies the right model automatically

3. **Live updates:** Re-run `opencode-config update --all` after changing tier config to update all installed files

4. **Dry-run first:** Always use `--dry-run` to preview changes before installing/uninstalling

5. **Sync available:** If database gets out of sync, run `opencode-config sync` to rebuild it

## 🆘 Help

```bash
# Main help
opencode-config --help

# Command help
opencode-config list --help
opencode-config install --help
opencode-config status --help
```

## 🎓 Tips

- Use `--dry-run` liberally - it's safe and shows what would happen
- Install `basic` bundle first to get essentials
- Check `status --details` to see installation method and timestamps
- Run `sync` after manual changes to keep database accurate
- Browse with `list` and `info` before installing

## 📚 Learn More

- [Full Documentation](../README.md)
- [Versioning Guide](VERSIONING.md)
- [Architecture](ARCHITECTURE.md)
- [Permissions & Tools Guide](PERMISSIONS.md)
- [Changelog](../CHANGELOG.md)
- [Contributing](../CONTRIBUTING.md)
- [Testing Guide](../installer/tests/README.md)

---

**Quick Example:**

```bash
# Complete workflow
opencode-config list                           # Browse components
opencode-config install --group basic          # Install essentials
opencode-config status                         # Verify installation
opencode-config info kubernetes-expert         # Learn about a component
```
