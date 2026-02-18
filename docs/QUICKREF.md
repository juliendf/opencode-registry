# OpenCode Registry - Quick Reference

**One-page command reference for OpenCode Registry CLI**

## 🚀 Installation

```bash
# Clone the registry
git clone https://github.com/yourusername/opencode-registry.git
cd opencode-registry

# Install the CLI
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
opencode-config info plan-brainstorm
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
opencode-config update build-general

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
| `advanced` | 62 | Complete ecosystem with all components |

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
| **Configuration** | `~/.opencode-registry/config.json` |
| **Installation database** | `~/.opencode-registry/installed.json` |
| **Registry path** | Auto-detected or set via config |

## 🔧 Component Types

| Type | Count | Location |
|------|-------|----------|
| **Agents** | 8 | `agents/*.md` |
| **Subagents** | 43+ | `agent/subagents/**/*.md` |
| **Skills** | 5+ | `skills/*/` |
| **Commands** | 4 | `commands/*.md` |

## ⚠️ Important Notes

1. **Merge-friendly:** Installation adds to existing `~/.config/opencode/` without overwriting your custom files

2. **Live symlinks:** Installed components are symlinked to the registry, so updates to registry files reflect immediately

3. **Dry-run first:** Always use `--dry-run` to preview changes before installing/uninstalling

4. **Sync available:** If database gets out of sync, run `opencode-config sync` to rebuild it

5. **Stow vs Symlink:** 
   - Stow (preferred): Uses GNU Stow for elegant symlink management
   - Symlink (fallback): Manual symlinks if stow not available

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
