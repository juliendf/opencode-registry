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

- (Optional) **GNU Stow** for better symlink management
  ```bash
  # macOS
  brew install stow
  
  # Ubuntu/Debian
  sudo apt-get install stow
  
  # Check installation
  stow --version
  ```

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/opencode-registry.git

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
# Navigate to installer directory
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
# Navigate to installer directory
cd installer

# Install with development dependencies (pytest, black, ruff, etc.)
pip install -e ".[dev]"

# Verify installation
opencode-config --version

# Navigate back to repository root
cd ..
```

**Expected output:**
```
opencode-config, version 0.1.0
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
opencode-config info build-general
opencode-config info mcp-builder
```

**Note:** The CLI automatically detects the registry location when run from the repository directory (including git worktrees).

**What you'll see:**
- 8 primary agents for different tasks
- 43 specialized subagents
- 3 skills for workflows
- 2 commands for common operations

---

## Step 4: Choose a Bundle

OpenCode Registry offers three installation bundles:

| Bundle | Components | Best For |
|--------|-----------|----------|
| **basic** | 4 essential | First-time users, minimal setup |
| **intermediate** | 10+ components | Regular users, common workflows |
| **advanced** | All 57 components | Power users, complete ecosystem |

**Preview a bundle before installing:**

```bash
# Preview what will be installed
opencode-config install --group basic --dry-run
```

---

## Step 5: Install Your First Bundle

```bash
# Install the basic bundle
opencode-config install --group basic

# Expected output:
# ✓ Bundle 'basic' installed successfully
# Components: 4
# - Agents: 2
# - Skills: 2
```

**What just happened?**
- Components were symlinked to `~/.config/opencode/`
- Installation was tracked in `~/.opencode-registry/installed.json`
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
ls -la ~/.config/opencode/agents/
ls -la ~/.config/opencode/skills/
```

**You should see:**
- Symlinks pointing to the registry
- Components marked as installed
- Timestamps showing when installed

---

## Step 7: Try Installing More Components

```bash
# Upgrade to intermediate bundle
opencode-config install --group intermediate

# Check for updates
opencode-config update --all --dry-run

# Update specific component
opencode-config update build-general
```

---

## Step 8: Understanding the Setup

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
├── ~/.config/opencode/               # Installation target (symlinks)
│   ├── agents/         → points to registry
│   ├── skills/         → points to registry
│   └── commands/       → points to registry
│
└── ~/.opencode-registry/             # Configuration & tracking
    ├── config.json                   # Your settings
    └── installed.json                # What's installed
```

### Component Types Explained

**What's the difference and when do you use each?**

| Component | How You Use It | Who Calls It | Example |
|-----------|---|---|---|
| **Agent** | Press **Tab** to switch | You (in OpenCode) | Switch to `plan` agent for analysis |
| **Subagent** | Use **@mention** or invoked automatically | Primary agents or you | `@general search for function` |
| **Skill** | Loaded by agents automatically | Agents/subagents | Agent loads `git-release` skill when needed |
| **Command** | Type **/** in OpenCode | You (in OpenCode) | `/test` to run test suite |

**In short:**
- **Agents & Subagents** = AI assistants (Tab for primary, @ for specialized)
- **Skills** = Reusable workflows (AI-driven, loaded automatically)
- **Commands** = User shortcuts (you type /, instant execution)

**Learn more:** [Agents](https://opencode.ai/docs/agents/), [Skills](https://opencode.ai/docs/skills/), [Commands](https://opencode.ai/docs/commands/)

---

### How It Works

1. **Registry (Read-Only)**: The `opencode-registry/` directory contains all components
2. **Installation**: CLI creates symlinks from `~/.config/opencode/` to the registry
3. **Tracking**: Database tracks what's installed and when
4. **Updates**: Pull latest changes from git, then run `update` command
5. **Auto-Detection**: Registry path is automatically detected from your current directory

**Git Worktree Support:** The CLI works seamlessly with git worktrees. When you run commands from a worktree, it automatically detects the correct registry location without requiring manual configuration updates.

---

## Common Tasks

### Installing Individual Components

```bash
# Currently, components are installed via bundles
# To get a specific component, install the bundle containing it
opencode-config install --group intermediate
```

### Checking for Updates

```bash
# Check all components (safe, no changes)
opencode-config update --all --dry-run

# Update everything
opencode-config update --all

# Update specific component
opencode-config update build-general
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
git clone https://github.com/YOUR_USERNAME/opencode-registry.git
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

# 3. Verify symlinks
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
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/opencode-registry/issues)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Ready to start?** Run these commands:

```bash
git clone https://github.com/YOUR_USERNAME/opencode-registry.git
cd opencode-registry/installer
pip install -e .
cd ..
opencode-config install --group basic
opencode-config status
```

Welcome to OpenCode Registry! 🎉
