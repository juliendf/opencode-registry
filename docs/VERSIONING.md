# Component Versioning Guide

OpenCode Registry uses **individual component versioning** with semantic versioning (semver) to provide granular control over component updates.

## Table of Contents

- [Overview](#overview)
- [Version Format](#version-format)
- [Component Types](#component-types)
- [Checking for Updates](#checking-for-updates)
- [Updating Components](#updating-components)
- [Version Compatibility](#version-compatibility)
- [Best Practices](#best-practices)

---

## Overview

Each component in the OpenCode Registry is **independently versioned**. This means:

- ✅ **Update individual components** without affecting others
- ✅ **Pin specific versions** for stability
- ✅ **Granular control** over your component library
- ✅ **Clear upgrade paths** with semantic versioning

### Why Individual Versioning?

Unlike monolithic versioning (where all components share one version), individual versioning gives you:

1. **Flexibility** - Update only what you need
2. **Stability** - Keep working versions while testing new ones
3. **Clarity** - Each component's version reflects its own changes
4. **Independence** - Component updates don't force ecosystem-wide upgrades

---

## Version Format

All components use **semantic versioning** (semver): `MAJOR.MINOR.PATCH`

```
1.2.3
│ │ │
│ │ └─ PATCH: Bug fixes, documentation updates
│ └─── MINOR: New features, backward-compatible changes
└───── MAJOR: Breaking changes, incompatible API changes
```

### Examples

- `1.0.0` - Initial stable release
- `1.1.0` - New features added (backward-compatible)
- `1.1.1` - Bug fix for 1.1.0
- `2.0.0` - Major update with breaking changes

---

## Component Types

### Agents & Subagents

**Version Location:** Top-level `version` field in frontmatter

```yaml
---
name: "Build Code"
description: "Full-stack coding agent"
type: "agent"
version: "1.2.0"  # ← Here
author: "OpenCode Team"
---
```

### Commands

**Version Location:** Top-level `version` field in frontmatter

```yaml
---
name: "Git Commit Helper"
description: "Intelligent commit message generation"
type: "command"
version: "1.0.1"  # ← Here
agent: "build-code"
---
```

### Skills

**Version Location:** `metadata.version` field (OpenCode spec requirement)

```yaml
---
name: "MCP Builder"
description: "Build Model Context Protocol servers"
type: "skill"
license: "MIT"
compatibility: "all"
metadata:
  version: "2.1.0"  # ← Here
  category: "development"
---
```

> **Note:** Skills use `metadata.version` instead of top-level `version` to comply with the OpenCode specification.

---

## Checking for Updates

### Check All Components

Preview available updates without making changes:

```bash
opencode-config update --all --dry-run
```

**Output Example:**
```
Updates Available:
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ Component       ┃ Installed ┃ Available ┃ Status ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│ build-code      │ 1.0.0     │ 1.2.0     │ UPDATE │
│ mcp-builder     │ 1.5.0     │ 2.0.0     │ UPDATE │
│ python-pro      │ 1.1.0     │ 1.1.0     │ OK     │
└─────────────────┴───────────┴───────────┴────────┘
```

### Check Specific Component

```bash
opencode-config update <component-id> --dry-run
```

Example:
```bash
opencode-config update build-code --dry-run
```

### View Installed Versions

List all installed components with their versions:

```bash
opencode-config list --installed
```

**Output:**
```
Installed Components:
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID              ┃ Name      ┃ Version ┃ Installed ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ build-code      │ Build...  │ 1.0.0   │ ✓         │
│ mcp-builder     │ MCP...    │ 1.5.0   │ ✓         │
└─────────────────┴───────────┴─────────┴───────────┘
```

---

## Updating Components

### Update All Components

Update all installed components to their latest versions:

```bash
opencode-config update --all
```

### Update Specific Component

Update a single component:

```bash
opencode-config update <component-id>
```

**Examples:**
```bash
# Update general development agent
opencode-config update build-code

# Update MCP builder skill
opencode-config update mcp-builder

# Update Python specialist subagent
opencode-config update python-pro
```

### Preview Before Updating

Always use `--dry-run` to preview changes first:

```bash
# Preview all updates
opencode-config update --all --dry-run

# Preview specific component update
opencode-config update build-code --dry-run
```

### Update Workflow

Recommended workflow for updates:

1. **Check for updates:**
   ```bash
   opencode-config update --all --dry-run
   ```

2. **Review changes** in the preview table

3. **Update selectively** or all at once:
   ```bash
   # Update specific components
   opencode-config update build-code
   opencode-config update mcp-builder
   
   # Or update everything
   opencode-config update --all
   ```

4. **Verify installation:**
   ```bash
   opencode-config status
   ```

---

## Version Compatibility

### Semantic Versioning Rules

OpenCode Registry follows standard semver compatibility:

| Update Type | Example | Compatibility | Risk |
|-------------|---------|---------------|------|
| **PATCH** | 1.0.0 → 1.0.1 | ✅ Fully compatible | Low |
| **MINOR** | 1.0.0 → 1.1.0 | ✅ Backward compatible | Low |
| **MAJOR** | 1.0.0 → 2.0.0 | ⚠️ Breaking changes | Medium-High |

### Update Recommendations

**PATCH Updates (x.x.X):**
- Bug fixes and documentation improvements
- **Safe to update immediately**
- No breaking changes

**MINOR Updates (x.X.x):**
- New features and enhancements
- **Generally safe to update**
- Backward compatible with existing usage

**MAJOR Updates (X.x.x):**
- Breaking changes or major redesigns
- **Review changelog before updating**
- May require configuration changes

---

## Best Practices

### 1. Check Before Updating

Always preview updates before applying:

```bash
opencode-config update --all --dry-run
```

### 2. Update Incrementally

For production environments, update components one at a time:

```bash
# Update and test one component at a time
opencode-config update build-code
# Test the updated component
opencode-config update mcp-builder
# Test again
```

### 3. Keep Track of Versions

Regularly check what's installed:

```bash
opencode-config status
opencode-config list --installed
```

### 4. Read Release Notes

Before major version updates (X.0.0), check:
- Component changelog
- Breaking changes
- Migration guides

### 5. Use Dry-Run Liberally

The `--dry-run` flag is your friend:

```bash
# Always safe to run - no changes made
opencode-config update --all --dry-run
```

### 6. Stay Updated

Update regularly to get:
- ✅ Bug fixes and improvements
- ✅ New features
- ✅ Security patches
- ✅ Performance enhancements

---

## Quick Reference

### Common Update Commands

```bash
# Check for all updates (safe, no changes)
opencode-config update --all --dry-run

# Update everything
opencode-config update --all

# Update specific component
opencode-config update <component-id>

# Preview specific component update
opencode-config update <component-id> --dry-run

# Check installed versions
opencode-config list --installed
opencode-config status
```

### Version Comparison

| Installed | Available | Action |
|-----------|-----------|--------|
| 1.0.0 | 1.0.1 | ✅ Patch update recommended |
| 1.0.0 | 1.1.0 | ✅ Minor update recommended |
| 1.0.0 | 2.0.0 | ⚠️ Review breaking changes |
| 1.5.0 | 1.5.0 | ✓ Already up to date |

---

## Examples

### Example 1: Regular Update Workflow

```bash
# Monday morning: Check for updates
$ opencode-config update --all --dry-run

Updates Available:
Component         Installed  Available  Status
build-code      1.0.0      1.1.0      UPDATE (minor)
python-pro        1.2.0      1.2.1      UPDATE (patch)

# Apply updates
$ opencode-config update --all

✓ Updated build-code: 1.0.0 → 1.1.0
✓ Updated python-pro: 1.2.0 → 1.2.1

# Verify
$ opencode-config status
```

### Example 2: Selective Update

```bash
# Check what needs updating
$ opencode-config update --all --dry-run

# Only update the Python specialist
$ opencode-config update python-pro

# Leave other components at current versions
```

### Example 3: Major Version Update

```bash
# Check for updates
$ opencode-config update mcp-builder --dry-run

Updates Available:
Component     Installed  Available  Status
mcp-builder   1.9.0      2.0.0      UPDATE (MAJOR - review changes)

# Read release notes, then update
$ opencode-config update mcp-builder
```

---

## Troubleshooting

### "Component already up to date"

Your installed version matches the registry version. No action needed.

### "Component not installed"

Install the component first:

```bash
opencode-config install <component-id>
```

### "Cannot determine version"

Sync your database:

```bash
opencode-config sync
```

---

## Related Documentation

- **[Quick Reference](QUICKREF.md)** - All CLI commands
- **[Architecture](ARCHITECTURE.md)** - System design
- **[README](../README.md)** - Getting started guide

---

**Questions or issues?** Open an issue on GitHub or check the main documentation.
