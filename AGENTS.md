# AGENTS.md - OpenCode Registry Development Guide

Quick reference for AI coding agents working with the OpenCode Registry codebase.

## 🚀 Essential Commands

### Build & Test
```bash
# Install CLI in development mode
cd installer && pip install -e ".[dev]"

# Run all tests (143 tests, 100% pass rate)
pytest tests/

# Run single test file
pytest tests/test_version.py

# Run specific test by name
pytest -k "test_parse_version"

# Run with coverage
pytest tests/ --cov=opencode_config --cov-report=html

# Format & lint
black src/ && ruff check --fix src/
```

### CLI Usage
```bash
opencode-config list                      # List components
opencode-config install --group basic     # Install bundle
opencode-config install --dry-run         # Preview changes
opencode-config status                    # Check status
opencode-config sync                      # Sync database
```

## 📁 Project Structure

```
installer/src/opencode_config/
├── cli.py              # Entry point, command registration
├── config.py           # Config management (~/.config/opencode/)
├── commands/           # CLI command modules (install, list, models, etc.)
└── utils/              # Shared utilities (manifest, version, copy, template)

opencode/               # Component library
├── agents/             # Primary agents & subagents/
├── skills/             # Skills (SKILL.md workflows)
└── commands/           # Custom commands
```

## 🎨 Code Style (PEP 8 + Black)

**Line length:** 100 chars | **Type hints:** Required | **Docstrings:** Google style

**Imports:** Group standard → third-party → local
```python
import json
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console

from .config import Config
```

**Naming:**
- `PascalCase` for classes
- `snake_case` for functions/methods
- `UPPER_SNAKE_CASE` for constants
- `_private` for internal methods

**Type hints required:**
```python
def parse_frontmatter(md_file: Path) -> Optional[Dict[str, Any]]:
    """Parse YAML frontmatter from markdown file."""
    pass
```

**Error handling - use specific exceptions:**
```python
if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")
```

## 🔧 Architecture Patterns

### CLI Commands
- One module per command in `commands/`
- Use Click decorators for args
- Use Rich for console output
- Keep logic thin, delegate to utils

### Configuration
- Centralized in `config.py`
- Auto-detect registry path (looks for both `opencode/` and `bundles/` directories)
- Store in `~/.opencode-registry/config.json`
- Always use Path objects
- **Git worktree support**: Auto-detection works seamlessly with git worktrees

### Installation Tracking
- Track in `~/.opencode-registry/installed.json`
- Record timestamp, method (stow/symlink), status
- Provide `sync` to rebuild from filesystem

### Component Discovery
- Scan `opencode/` directory structure
- Parse YAML frontmatter for metadata
- Support manifest.yaml or frontmatter

## 📦 Component Files

**YAML frontmatter (required):**
```yaml
---
name: "Component Name"
description: "Brief description"
type: "agent|subagent|skill|command"
version: "1.0.0"
model_tier: "free|low|medium|high"  # optional: tier to resolve model IDs
---
```

Notes

- `model_tier` is optional. If provided, the installer will resolve the
  tier to the configured model ID for runtime usage. Valid values are
  `high`, `medium`, `low`, and `free`.

**Markdown style:**
- ATX headers (`#`)
- Code fences with language
- 2-space indent for YAML
- Blank lines between sections

## 🧪 Testing

**Organization:** Mirror src/ structure in tests/

**Naming:** `test_<function>_<behavior>`
```python
def test_parse_version_with_v_prefix():
    assert parse_version("v1.2.3") == (1, 2, 3)
```

**Coverage:** Aim for >80%, test happy + error paths

## 📝 Commit Format

```
<type>: <description>

feat: Add selective component uninstall
fix: Handle missing frontmatter gracefully
docs: Update README with new commands
test: Add tests for version parsing
```

## 🚨 Critical Rules

1. **Never hardcode paths** - Use `Path.home()` and `os.path.expanduser()`
2. **Always type hint** - Functions must have type signatures
3. **Use specific exceptions** - No bare `except:` blocks
4. **Format before commit** - Run `black src/ && ruff check src/`
5. **Test before PR** - Ensure `pytest` passes
6. **Use --dry-run** - Preview changes in new features
7. **Follow semver** - Don't break backward compatibility

## 💡 Key Patterns

**Config access:**
```python
config = Config()  # Auto-loads ~/.config/opencode/opencode-registry-config.json
target = config.target_dir  # Returns Path object
model_for_high = config.get_model_for_tier("high")  # Get tier config
```

**Component structure:**
```python
opencode/agents/my-agent.md          # Primary agent
opencode/agents/subagents/01-core/   # Subagent category
opencode/skills/skill-name/SKILL.md  # Skill definition
```

**Adding to bundles:**
Edit `bundles/basic.yaml`, `intermediate.yaml`, or `advanced.yaml`

## 🔍 Key Files

- `cli.py` - Command registration
- `config.py` - Config management
- `utils/manifest.py` - Frontmatter parsing
- `utils/version.py` - Semantic versioning
- `utils/installed_db.py` - Installation tracking
- `utils/copy.py` - File copy with template processing
- `utils/template.py` - Model tier resolution
- `commands/install.py` - Core install logic
- `commands/models.py` - Model tier configuration
