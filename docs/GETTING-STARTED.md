# Getting Started with OpenCode Registry

A step-by-step guide to installing and using OpenCode Registry for the first time.

## Prerequisites

Before you begin, ensure you have:

- **OpenCode 1.2.5 or later** - The AI assistant platform
  - [Download from opencode.ai](https://opencode.ai)
  - Or use [OpenCode Zen (cloud version)](https://zen.opencode.ai)
  - See [installation guide](https://opencode.ai/docs/)
  - Check your version: `opencode --version`

- **Python 3.8 or higher** installed
  ```bash
  python --version  # Should show 3.8+
  ```
  
- **Git** installed
  ```bash
  git --version
  ```

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/juliendf/opencode-registry.git

# Navigate into the directory
cd opencode-registry

# Verify structure
ls -la
# You should see: opencode/, installer/, bundles/, docs/, etc.
```

---

## Step 2: Install the CLI Tool

### For Regular Users

```bash
# Navigate to installer directory (contains setup.py/pyproject.toml)
cd installer

# Install the CLI tool
pip install -e .

# Verify installation
opencode-config --version
opencode-config --help

# Navigate back to repository root for next steps
cd ..
```

### For Developers

If you plan to contribute to the codebase:

```bash
# Navigate to installer directory (contains setup.py/pyproject.toml)
cd installer

# Install with development dependencies (pytest, black, ruff, mypy, etc.)
pip install -e ".[dev]"

# Verify installation
opencode-config --version

# Navigate back to repository root
cd ..
```

**Expected output:**
```
opencode-config, version 0.2.0
```

**Troubleshooting:**
- If `command not found`: Ensure pip's bin directory is in your PATH
- If pip fails: Try `python -m pip install -e .` (or `python -m pip install -e ".[dev]"` for developers)
- If permission errors: Don't use `sudo`, use a virtual environment instead
- **Important:** Make sure to run installation from the `installer/` directory

---

## Step 3: Explore Available Components

```bash
# List all components (run from repository root)
opencode-config list

# Filter by type
opencode-config list --type agent      # Show only agents
opencode-config list --type subagent   # Show only subagents
opencode-config list --type skill      # Show only skills
opencode-config list --type command    # Show only commands

# Get details about a specific component
    opencode-config info build-code
opencode-config info mcp-builder
```

**Note:** The CLI automatically detects the registry location when run from the repository directory (including git worktrees).

**What you'll see:**
- 7 primary agents for different development roles
- 43 specialized subagents organized by domain
- 3 skills for complex workflows
- 3 commands for common operations
- **Total: 56 components**

---

## Step 4: Choose a Bundle

OpenCode Registry offers three installation bundles:

| Bundle | Components | Best For |
|--------|-----------|----------|
| **basic** | 4 essential | First-time users, minimal setup |
| **intermediate** | 10+ components | Regular users, common workflows |
| **advanced** | All 56 components | Power users, complete ecosystem |

**Preview a bundle before installing:**

```bash
# Preview what will be installed
opencode-config install --group basic --dry-run
```

---

## Step 5: Install Your First Bundle

### First-Run Experience

When installing for the first time, you'll be guided through model tier configuration:

```bash
# Install the basic bundle
opencode-config install --group basic

# You'll see:
# Welcome! Before installing, let's configure which models to use for each 
# complexity tier.
#
# Model Tier Configuration Wizard
# ...
```

The wizard helps you configure which model to use for each complexity tier:
- **High tier** - Complex reasoning (architecture, design planning)
- **Medium tier** - General coding (implementation, code review)
- **Low tier** - Simple tasks (documentation, commit messages)

**What just happened?**
- Model tiers were configured in `~/.config/opencode/opencode-registry-config.json`
- Component files were **copied** to `~/.config/opencode/` with your model tier configuration applied
- Each component's `model_tier:` frontmatter was resolved to the correct `model:` for your setup
- Installation was tracked in `~/.config/opencode/opencode-registry-installed.json`
- You can now use these components with OpenCode

---

## Step 6: Verify Installation

```bash
# Check what's installed
opencode-config status

# Show detailed information
opencode-config status --details

# List only installed components
opencode-config list --installed

# Verify files on disk
ls ~/.config/opencode/agents/
ls ~/.config/opencode/skills/
```

**You should see:**
- Copied `.md` files with correct `model:` values written in
- Components marked as installed with timestamps

---

## Step 7: Configure Model Tiers (Optional)

If you skipped the wizard or want to change models later:

```bash
# Interactive wizard - configure all three tiers
opencode-config models --wizard

# Or set individually
opencode-config models --set high "github-copilot/claude-sonnet-4.5"
opencode-config models --set medium "github-copilot/claude-sonnet-4"
opencode-config models --set low "github-copilot/claude-haiku-4.5"

# View current configuration
opencode-config models --list
```

After changing tiers, re-run `opencode-config update --all` to apply the new models to all installed files.

---

## Step 8: Try Installing More Components

```bash
# Upgrade to intermediate bundle
opencode-config install --group intermediate

# Check for updates
opencode-config update --all --dry-run

# Update specific component
opencode-config update build-code
```

---

## Step 9: Understanding the Setup

### Directory Structure

```
Your System
├── ~/opencode-registry/              # The registry (source)
│   ├── opencode/                     # All components live here
│   │   ├── agents/
│   │   ├── skills/
│   │   └── commands/
│   └── installer/                    # The CLI tool
│
├── ~/.config/opencode/               # Installation target (copied files)
│   ├── agents/         copied from registry, model resolved
│   ├── skills/         copied from registry
│   └── commands/       copied from registry
│   ├── opencode-registry-config.json     # Your settings + model tiers
│   └── opencode-registry-installed.json  # What's installed
```

### Component Types Explained

**What's the difference and when do you use each?**

| Component Type | Count | How You Use It | Who Calls It | Example |
|----------------|-------|----------------|--------------|---------|
| **Primary Agent** | 7 | Press **Tab** to switch | You (in OpenCode) | Switch to `build-code` agent |
| **Subagent** | 43 | Use **@mention** or invoked automatically | Primary agents or you | `@python-pro optimize this code` |
| **Skill** | 3 | Loaded by agents automatically | Agents/subagents | Agent loads `mcp-builder` skill when needed |
| **Command** | 2 | Type **/** in OpenCode | You (in OpenCode) | `/commit` to create git commit |

**In short:**
- **Agents & Subagents** = AI assistants (Tab for primary, @ for specialized)
- **Skills** = Reusable workflows (AI-driven, loaded automatically)
- **Commands** = User shortcuts (you type /, instant execution)

**Learn more:** [Agents](https://opencode.ai/docs/agents/), [Skills](https://opencode.ai/docs/skills/), [Commands](https://opencode.ai/docs/commands/)

---

### How It Works

1. **Registry (Read-Only)**: The `opencode-registry/` directory contains all components
2. **Installation**: CLI **copies** files from the registry to `~/.config/opencode/`, resolving `model_tier:` to the correct `model:` value
3. **Tracking**: Database tracks what's installed and when
4. **Model Tiers**: First install triggers wizard; subsequent installs use saved config
5. **Updates**: Pull latest changes from git, then run `update --all` — model tier config is re-applied automatically
6. **Auto-Detection**: Registry path is automatically detected from your current directory

**Git Worktree Support:** The CLI works seamlessly with git worktrees. When you run commands from a worktree, it automatically detects the correct registry location without requiring manual configuration updates.

---

## Common Tasks

### Installing Individual Components

**Note:** Currently, components are installed via bundles only. Individual component installation is planned for a future release.

```bash
# To install a specific component, use the bundle containing it
opencode-config list  # Find which bundle contains the component
opencode-config install --group intermediate
```

### Checking for Updates

```bash
# Check all components (safe, no changes)
opencode-config update --all --dry-run

# Update everything
opencode-config update --all

# Update specific component
opencode-config update build-code
```

### Uninstalling Components

```bash
# Preview what will be removed
opencode-config uninstall --all --dry-run

# Uninstall everything
opencode-config uninstall --all
```

### Fixing Issues

```bash
# Sync database with actual files on disk
opencode-config sync

# Preview sync
opencode-config sync --dry-run
```

---

## Next Steps

### Learn More

- **[Quick Reference](QUICKREF.md)** - All commands at a glance
- **[Versioning Guide](VERSIONING.md)** - Managing component versions
- **[Architecture](ARCHITECTURE.md)** - How the system works
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Customize Your Setup

1. **Add custom components** alongside registry components
2. **Configure target directory** if you don't want `~/.config/opencode/`
3. **Create your own bundles** by editing YAML files

### Stay Updated

```bash
# Pull latest registry changes
cd opencode-registry
git pull origin main

# Check for component updates
opencode-config update --all --dry-run

# Apply updates
opencode-config update --all
```

---

## Example Workflows

### Daily Developer Workflow

```bash
# Morning: Check for updates
opencode-config update --all --dry-run

# Apply updates if available
opencode-config update --all

# Verify everything works
opencode-config status
```

### First-Time Team Setup

```bash
# 1. Clone and install
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry/installer
pip install -e .

# 2. Install components
cd ..
opencode-config install --group intermediate

# 3. Verify
opencode-config status
```

### Troubleshooting Workflow

```bash
# If something seems wrong:

# 1. Check status
opencode-config status

# 2. Sync database
opencode-config sync

# 3. Verify files
ls -la ~/.config/opencode/agents/

# 4. Reinstall if needed
opencode-config uninstall --all
opencode-config install --group basic
```

---

## Tips for Success

1. **Start small**: Install the `basic` bundle first
2. **Use dry-run**: Always preview changes with `--dry-run`
3. **Sync regularly**: Run `sync` if database seems off
4. **Update often**: Keep components up-to-date with `update --all`
5. **Read the docs**: Check guides for specific features

---

## Getting Help

- **Documentation**: Check docs/ directory
- **Issues**: [GitHub Issues](https://github.com/juliendf/opencode-registry/issues)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Ready to start?** Run these commands:

```bash
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry/installer
pip install -e .
cd ..
opencode-config install --group basic
opencode-config status
```

Welcome to OpenCode Registry! 🎉
