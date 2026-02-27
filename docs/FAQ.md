# Frequently Asked Questions (FAQ)

Common questions and troubleshooting guide.

---

## Quick Fixes

Try these first:

| Issue | Fix |
|-------|-----|
| Command not found | `pip install -e installer/` from registry |
| No components found | Run from registry: `cd /path/to/opencode-registry` |
| Database out of sync | `opencode-config sync` |
| Permission denied | Don't use sudo - `chown -R $USER ~/.config/opencode/` |
| Registry not found | `opencode-config config --registry auto` |
| Something's wrong | Full reset: `uninstall --all && install --group basic` |

---

## Diagnostic Commands

```bash
# Check installation
opencode-config --version

# Check configuration
opencode-config config --list

# Check components
opencode-config list | head -10

# Check status
opencode-config status

# Sync database
opencode-config sync
```

---

## General

### What is OpenCode Registry?

A curated collection of 56 AI agents, subagents, skills, and commands with a CLI tool to install and manage them.

### What's the difference between agents, subagents, skills, and commands?

| Type | Use | How |
|------|-----|-----|
| **Primary Agents** | Core AI personas | Press **Tab** to switch |
| **Subagents** | Specialized experts | Use **@mention** or auto-invoked |
| **Skills** | Multi-step workflows | Loaded automatically |
| **Commands** | Common tasks | Type **/command** |

### How much does it cost?

Free and open-source under MIT License.

---

## Installation

### What are the requirements?

- **Python** 3.8+
- **Git**
- **OpenCode** 1.2.5+ - [Download](https://opencode.ai) or [OpenCode Zen](https://zen.opencode.ai)

### How do I install?

```bash
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry/installer
pip install -e .
cd ..
opencode-config install --group basic
```

See [Getting Started](GETTING-STARTED.md) for detailed steps.

### Where are components installed?

Files are **copied** to `~/.config/opencode/`:

```
~/.config/opencode/
├── agents/
├── skills/
├── commands/
├── opencode-registry-config.json
└── opencode-registry-installed.json
```

### Can I change the installation directory?

```bash
# Per-install
opencode-config install --group basic --target /path/to/directory

# Permanent
opencode-config config --target /path/to/directory
```

---

## Usage

### Which bundle should I start with?

- **basic** (4 components) - Essential agents
- **intermediate** (10+) - Common workflows
- **advanced** (56) - Everything

Start with `basic`, add more as needed.

### How do I update components?

```bash
# Check for updates
opencode-config update --all --dry-run

# Update all
opencode-config update --all

# Update specific
opencode-config update build-code
```

### How do I uninstall?

```bash
opencode-config uninstall --all
```

See [Quick Reference](QUICKREF.md) for all commands.

---

## Model Tiers

### What are model tiers?

Configure which model to use for different complexity levels. Set once, applied to all components.

### How do I configure model tiers?

```bash
# Interactive wizard
opencode-config models --wizard

# Or manually
opencode-config models --set high "github-copilot/claude-sonnet-4.5"
opencode-config models --set medium "github-copilot/claude-sonnet-4"
opencode-config models --set low "github-copilot/claude-haiku-4.5"
```

### What's the "free" tier for?

Testing, CI/CD, or environments without paid model access.

---

## Troubleshooting

### Problem: `pip install -e .` fails

**Symptoms:**
```
ERROR: file:///path/to/opencode-registry does not appear to be a Python project
```

**Solutions:**

1. Ensure you're in the installer directory:
   ```bash
   cd opencode-registry/installer
   pip install -e .
   ```

2. Check Python version:
   ```bash
   python --version  # Should be 3.8+
   ```

3. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```

4. Install in virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   cd installer
   pip install -e .
   ```

---

### Problem: `opencode-config: command not found`

**Solutions:**

1. Check if installation succeeded:
   ```bash
   pip list | grep opencode
   ```

2. Check PATH:
   ```bash
   python -m site --user-base
   ```

3. Use python -m to run:
   ```bash
   python -m opencode_config.cli --help
   ```

4. Reinstall:
   ```bash
   cd installer
   pip uninstall opencode-config
   pip install -e .
   ```

---

### Problem: Installation succeeds but no components visible

**Symptoms:**
`opencode-config list` shows "No components found"

**Solutions:**

1. Check registry path:
   ```bash
   opencode-config config --list
   ```

2. Set registry path:
   ```bash
   opencode-config config --registry /path/to/opencode-registry
   ```

3. Verify opencode directory exists:
   ```bash
   ls opencode/agents/
   ```

---

### Problem: Component not found

**Symptoms:**
`opencode-config install my-agent` fails

**Solutions:**

1. Check component exists:
   ```bash
   opencode-config list | grep my-agent
   ```

2. Use correct component ID:
   - `build-code.md` → `build-code`
   - Skills: `mcp-builder/` → `mcp-builder`

---

### Problem: Component shows as installed but missing

**Symptoms:**
`status` shows installed but files not on disk

**Solutions:**

1. Sync database:
   ```bash
   opencode-config sync
   ```

2. Reinstall:
   ```bash
   opencode-config install --group basic
   ```

---

### Problem: No updates found after pulling

**Symptoms:**
All components show up-to-date even after `git pull`

**Solutions:**

1. Pull latest:
   ```bash
   cd /path/to/opencode-registry
   git pull origin main
   ```

2. Sync and check:
   ```bash
   opencode-config sync
   opencode-config update --all --dry-run
   ```

---

### Problem: Permission denied during update

**Symptoms:**
`PermissionError: [Errno 13] Permission denied`

**Solutions:**

1. Don't use sudo:
   ```bash
   # WRONG: sudo opencode-config update --all
   # RIGHT: opencode-config update --all
   ```

2. Fix ownership:
   ```bash
   sudo chown -R $USER:$USER ~/.config/opencode/
   ```

---

### Problem: Database out of sync

**Symptoms:**
`status` shows different than actual files

**Solutions:**

1. Run sync:
   ```bash
   opencode-config sync
   ```

2. Preview sync:
   ```bash
   opencode-config sync --dry-run
   ```

3. Manual rebuild:
   ```bash
   rm ~/.config/opencode/opencode-registry-installed.json
   opencode-config sync
   ```

---

### Problem: Database corrupted

**Symptoms:**
`json.decoder.JSONDecodeError: Expecting value`

**Solutions:**

1. Backup and rebuild:
   ```bash
   cp ~/.config/opencode/opencode-registry-installed.json ~/.config/opencode/opencode-registry-installed.json.bak
   rm ~/.config/opencode/opencode-registry-installed.json
   opencode-config sync
   ```

---

### Problem: Registry not detected

**Symptoms:**
`Error: Could not find registry. Run from registry directory.`

**Solutions:**

1. Run from registry directory:
   ```bash
   cd /path/to/opencode-registry
   opencode-config list
   ```

2. Enable auto-detection:
   ```bash
   opencode-config config --registry auto
   ```

3. Set path manually:
   ```bash
   opencode-config config --registry /path/to/opencode-registry
   ```

---

### Problem: Git worktree - registry path breaks

**Solutions:**

1. Use auto-detection (recommended):
   ```bash
   opencode-config config --registry auto
   cd /path/to/worktree
   opencode-config list  # Works automatically!
   ```

2. Set path manually:
   ```bash
   opencode-config config --registry $(pwd)
   ```

---

## Performance

### `list` command is slow

Normal for 60+ components (1-3 seconds). Use filters:
```bash
opencode-config list --type agent
opencode-config list --installed
```

### Installation is slow

Normal for first-time install (copying 60+ files). Install smaller bundle:
```bash
opencode-config install --group basic
```

---

## Complete Reset

If everything is broken:

```bash
# 1. Uninstall everything
opencode-config uninstall --all

# 2. Clear database
rm -rf ~/.config/opencode/opencode-registry-*.json

# 3. Reinstall
cd /path/to/opencode-registry
git pull
opencode-config install --group basic

# 4. Verify
opencode-config status
```

---

## Advanced

### Does it work with git worktrees?

Yes! Auto-detection finds the registry from your current directory.

### How do versions work?

Components use semantic versioning. See [Versioning Guide](VERSIONING.md).

### Can I contribute?

Yes! See [Contributing Guide](../CONTRIBUTING.md).

1. Fork the repository
2. Add component to appropriate directory
3. Include YAML frontmatter
4. Submit a pull request

---

## Getting More Help

- [Getting Started](GETTING-STARTED.md) - Step-by-step tutorial
- [Quick Reference](QUICKREF.md) - CLI command cheat sheet
- [GitHub Issues](https://github.com/juliendf/opencode-registry/issues)
- [GitHub Discussions](https://github.com/juliendf/opencode-registry/discussions)

**When reporting issues, include:**
```bash
python --version
opencode-config --version
opencode-config config --list
ls -la ~/.config/opencode/
```
