# Troubleshooting Guide

Common issues and solutions for OpenCode Registry.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Component Issues](#component-issues)
- [Update Issues](#update-issues)
- [Database Issues](#database-issues)
- [Symlink Issues](#symlink-issues)
- [Configuration Issues](#configuration-issues)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### Problem: `pip install -e .` fails

**Symptoms:**
```
ERROR: file:///path/to/opencode-registry does not appear to be a Python project
```

**Solutions:**

1. **Ensure you're in the installer directory:**
   ```bash
   cd opencode-registry/installer
   pip install -e .
   # Or for developers: pip install -e ".[dev]"
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

3. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

4. **Install in virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   cd installer
   pip install -e .
   ```

---

### Problem: `opencode-config: command not found`

**Symptoms:**
After installation, running `opencode-config` shows "command not found"

**Solutions:**

1. **Check if installation succeeded:**
   ```bash
   pip list | grep opencode
   ```

2. **Check PATH includes pip bin directory:**
   ```bash
   python -m site --user-base
   # Add /bin to your PATH
   ```

3. **Use python -m to run:**
   ```bash
   python -m opencode_config.cli --help
   ```

4. **Reinstall in development mode:**
   ```bash
   cd installer
   pip uninstall opencode-config
   pip install -e .
   ```

---

### Problem: Installation succeeds but no components visible

**Symptoms:**
```bash
opencode-config list
# Shows "No components found"
```

**Solutions:**

1. **Check registry path:**
   ```bash
   opencode-config config --list
   # Verify registry_path is correct
   ```

2. **Set registry path manually:**
   ```bash
   opencode-config config --registry /path/to/opencode-registry
   ```

3. **Verify opencode directory exists:**
   ```bash
   ls opencode/agents/
   ls opencode/skills/
   ```

---

## Component Issues

### Problem: Component not found when trying to install

**Symptoms:**
```bash
opencode-config install my-agent
# Error: Component 'my-agent' not found
```

**Solutions:**

1. **Check component exists:**
   ```bash
   opencode-config list | grep my-agent
   ```

2. **Use correct component ID:**
   - IDs are derived from filenames without extension
   - `build-code.md` → `build-code`
   - Skills use directory name: `mcp-builder/` → `mcp-builder`

3. **Check for typos:**
   ```bash
   opencode-config list --type agent  # List all agents
   ```

---

### Problem: Component shows as installed but missing from disk

**Symptoms:**
```bash
opencode-config status
# Shows component as installed
ls ~/.config/opencode/agents/
# But file is missing
```

**Solutions:**

1. **Sync database with disk:**
   ```bash
   opencode-config sync
   ```

2. **Reinstall the component:**
   ```bash
   opencode-config install --group basic
   ```

3. **Check symlink integrity:**
   ```bash
   ls -la ~/.config/opencode/agents/
   # Look for broken symlinks (red text on most terminals)
   ```

---

## Update Issues

### Problem: `opencode-config update --all` shows no updates

**Symptoms:**
All components show as up-to-date even after pulling latest changes

**Solutions:**

1. **Pull latest registry changes:**
   ```bash
   cd /path/to/opencode-registry
   git pull origin main
   ```

2. **Check component versions in registry:**
   ```bash
    grep "version:" opencode/agents/build-code.md
   ```

3. **Verify installed versions:**
   ```bash
   opencode-config status
   ```

4. **Force sync:**
   ```bash
   opencode-config sync
   opencode-config update --all --dry-run
   ```

---

### Problem: Update fails with permission error

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la ~/.config/opencode/
   ```

2. **Don't use sudo:**
   ```bash
   # WRONG: sudo opencode-config update --all
   # RIGHT:
   opencode-config update --all
   ```

3. **Fix ownership:**
   ```bash
   sudo chown -R $USER:$USER ~/.config/opencode/
   sudo chown -R $USER:$USER ~/.opencode-registry/
   ```

---

## Database Issues

### Problem: Database out of sync with reality

**Symptoms:**
`status` shows different results than what's actually in `~/.config/opencode/`

**Solutions:**

1. **Run sync command:**
   ```bash
   opencode-config sync
   ```

2. **Preview sync first:**
   ```bash
   opencode-config sync --dry-run
   ```

3. **Manual database rebuild:**
   ```bash
   rm ~/.opencode-registry/installed.json
   opencode-config sync
   ```

---

### Problem: Database corrupted

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting value
```

**Solutions:**

1. **Backup current database:**
   ```bash
   cp ~/.opencode-registry/installed.json ~/.opencode-registry/installed.json.bak
   ```

2. **Remove and rebuild:**
   ```bash
   rm ~/.opencode-registry/installed.json
   opencode-config sync
   ```

3. **Manually fix JSON:**
   ```bash
   # Edit with your preferred editor
   nano ~/.opencode-registry/installed.json
   # Or delete and reinstall
   ```

---

## Symlink Issues

### Problem: Broken symlinks after moving registry

**Symptoms:**
Components show as installed but symlinks are broken (red in `ls` output)

**Solutions:**

1. **Update registry path:**
   ```bash
   opencode-config config --registry /new/path/to/registry
   ```

2. **Uninstall and reinstall:**
   ```bash
   opencode-config uninstall --all
   opencode-config install --group basic
   ```

3. **Manual symlink fix:**
   ```bash
   rm ~/.config/opencode/agents/*
   opencode-config install --group basic
   ```

---

### Problem: Stow conflicts

**Symptoms:**
```
WARNING! stowing agent would cause conflicts:
  * existing target is neither a link nor a directory
```

**Solutions:**

1. **Check for existing files:**
   ```bash
   ls -la ~/.config/opencode/agents/
   ```

2. **Remove conflicting files:**
   ```bash
   # Backup first!
    mv ~/.config/opencode/agents/build-code.md ~/backup/
   opencode-config install --group basic
   ```

3. **Use --adopt with stow (advanced):**
   ```bash
   # This moves existing files into the registry (be careful!)
   cd opencode-registry
   stow --adopt opencode
   ```

---

## Configuration Issues

### Problem: Config changes not persisting

**Symptoms:**
Setting configuration values but they reset after restart

**Solutions:**

1. **Check config file exists:**
   ```bash
   ls -la ~/.opencode-registry/config.json
   ```

2. **Verify write permissions:**
   ```bash
   touch ~/.opencode-registry/test
   rm ~/.opencode-registry/test
   ```

3. **Manually edit config:**
   ```bash
   nano ~/.opencode-registry/config.json
   ```

---

### Problem: Registry path not detected automatically

**Symptoms:**
```
Error: Could not find registry. Run from registry directory.
```

**Cause:** The CLI auto-detects the registry by looking for both `opencode/` and `bundles/` directories in the current directory or parent directories.

**Solutions:**

1. **Run from repository directory:**
   ```bash
   cd /path/to/opencode-registry
   opencode-config list
   ```

2. **Enable auto-detection (default):**
   ```bash
   opencode-config config --registry auto
   ```

3. **Set path manually (if needed):**
   ```bash
   opencode-config config --registry /path/to/opencode-registry
   ```

4. **Verify directory structure:**
   ```bash
   # Both directories must exist
   ls opencode/
   ls bundles/
   ```

**Git Worktree Users:** Auto-detection works seamlessly with git worktrees. Simply run commands from your worktree directory.

---

## Git Worktree Issues

### Problem: Registry path breaks when switching worktrees

**Symptoms:**
After creating or switching to a git worktree, commands fail with "registry not found"

**Solutions:**

1. **Use auto-detection (recommended):**
   ```bash
   # Enable auto-detection
   opencode-config config --registry auto
   
   # Now run from any worktree
   cd /path/to/worktree
   opencode-config list
   ```

2. **Manually update registry path:**
   ```bash
   cd /path/to/your/worktree
   opencode-config config --registry $(pwd)
   ```

**Note:** With auto-detection enabled (default), the CLI automatically finds the registry location based on your current directory, making it seamless to work with multiple worktrees.

---

## Performance Issues

### Problem: `list` command is slow

**Symptoms:**
`opencode-config list` takes several seconds to run

**Solutions:**

1. **Check registry size:**
   ```bash
   find opencode -name "*.md" | wc -l
   ```

2. **This is normal for 60+ components** - expected time is 1-3 seconds

3. **Use filters to narrow results:**
   ```bash
   opencode-config list --type agent
   opencode-config list --installed
   ```

---

### Problem: Installation is slow

**Symptoms:**
Installation takes a long time even with dry-run

**Solutions:**

1. **This is normal for first-time install** - creating 60+ symlinks

2. **Install smaller bundles:**
   ```bash
   opencode-config install --group basic  # Only 4 components
   ```

3. **Check disk performance:**
   ```bash
   # Slow disk can affect symlink creation
   df -h ~/.config/opencode/
   ```

---

## Getting More Help

If your issue isn't covered here:

1. **Check existing issues:**
   - [GitHub Issues](https://github.com/juliendf/opencode-registry/issues)

2. **Enable verbose output:**
   ```bash
   opencode-config list -v  # If -v flag is available
   ```

3. **Provide diagnostic info when reporting:**
   ```bash
   # Include this info in bug reports:
   python --version
   opencode-config --version
   opencode-config config --list
   ls -la ~/.config/opencode/
   cat ~/.opencode-registry/installed.json
   ```

4. **Check logs:**
   ```bash
   # If logging is implemented
   cat ~/.opencode-registry/logs/opencode-config.log
   ```

---

## Quick Diagnostic Checklist

Run these commands to diagnose most issues:

```bash
# 1. Check installation
opencode-config --version

# 2. Check configuration
opencode-config config --list

# 3. Check components
opencode-config list | head -10

# 4. Check status
opencode-config status

# 5. Sync database
opencode-config sync --dry-run

# 6. Verify symlinks
ls -la ~/.config/opencode/agents/ | head -10

# 7. Check registry structure
ls -R opencode/ | head -20
```

If all of these work, your installation is healthy!

---

## Common Workflows

### Complete Reset

If everything is broken, start fresh:

```bash
# 1. Backup custom components
cp -r ~/.config/opencode/agents/my-custom-agent ~/backup/

# 2. Uninstall everything
opencode-config uninstall --all

# 3. Clear database
rm -rf ~/.opencode-registry/

# 4. Reinstall
cd /path/to/opencode-registry
git pull
opencode-config install --group basic

# 5. Restore custom components
cp ~/backup/my-custom-agent ~/.config/opencode/agents/
```

### Move Registry to New Location

```bash
# 1. Move directory
mv ~/old/location/opencode-registry ~/new/location/

# 2. Update config
opencode-config config --registry ~/new/location/opencode-registry

# 3. Reinstall (refreshes symlinks)
opencode-config uninstall --all
opencode-config install --group basic

# 4. Verify
opencode-config status
```

---

**Still stuck?** Open an issue on GitHub with:
- Your operating system
- Python version
- Output of diagnostic commands
- What you're trying to do
- What error you're getting
