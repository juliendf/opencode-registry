# AGENTS.md - OpenCode Registry Development Guide

Quick reference for AI coding agents working with the OpenCode Registry codebase.

## Essential Commands

### Build & Test
```bash
# Install CLI in development mode
cd installer && pip install -e ".[dev]"

# Run all tests
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

## Project Structure

```
installer/src/opencode_config/
├── cli.py              # Entry point, command registration
├── config.py           # Config management
├── commands/           # CLI command modules
└── utils/              # Shared utilities

opencode/               # Component library
├── agents/             # Primary agents (5)
│   ├── ask-me-anything.md
│   ├── plan.md
│   ├── build.md
│   ├── debug.md
│   ├── review.md
│   └── subagents/      # Specialist subagents (10, flat)
│       ├── infrastructure-engineer.md
│       ├── data-engineer.md
│       ├── ml-engineer.md
│       ├── mlops-engineer.md
│       ├── ai-engineer.md
│       ├── penetration-tester.md
│       ├── security-auditor.md
│       ├── mobile-developer.md
│       ├── cli-developer.md
│       └── fullstack-developer.md
├── skills/             # Skills (40+) - knowledge injection
│   ├── python-pro/
│   ├── typescript-pro/
│   ├── aws-patterns/
│   ├── kubernetes-patterns/
│   └── ...
└── commands/           # Custom commands (3)
    ├── commit.md
    ├── documentation.md
    └── kb.md
```

## Organization Philosophy

**Primary Agents (5):** Override built-in opencode agents. Handle broad categories (planning, coding, debugging, review, general knowledge).

**Subagents (10):** Invoke with V2 `subagent` tool and IDs prefixed by `subagents/`. Use for autonomous execution, not knowledge lookup.

**Skills (40+):** Inject knowledge into current context with V2 `skill` tool and exact skill ID. Load when domain expertise is needed without spawning a child session.

## Code Style

**Line length:** 100 chars | **Type hints:** Required | **Docstrings:** Google style

**Imports:** standard → third-party → local

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

## Architecture Patterns

### CLI Commands
- One module per command in `commands/`
- Use Click decorators for args
- Use Rich for console output
- Keep logic thin, delegate to utils

### Configuration
- Centralized in `config.py`
- Auto-detect registry path (looks for `opencode/` and `bundles/` directories)
- Store in `~/.config/opencode/opencode-registry-config.json`
- Always use Path objects
- **Git worktree support**: Auto-detection works seamlessly

### Installation Tracking
- Track in `~/.config/opencode/opencode-registry-installed.json`
- Record timestamp, method (copy), status
- Provide `sync` to rebuild from filesystem

### Component Discovery
- Scan `opencode/` directory structure
- Parse YAML frontmatter for metadata

## Component Files

**YAML frontmatter (required):**
```yaml
---
name: "Component Name"
description: "Brief description"
type: "agent|subagent|skill|command"
model_tier: "medium"  # Optional, remove to inherit caller model
---
```

**Notes:**
- `model_tier` is optional. Valid values: `high`, `medium`, `low`, `free`
- `version:` field removed in v1.0 — tracked by installer database instead
- `install --inherit-model` and `update --inherit-model` remove model selectors for that invocation only; update recopies the full registry package when any change is detected

**Markdown style:**
- ATX headers (`#`)
- Code fences with language
- 2-space indent for YAML
- Blank lines between sections

## Testing

**Organization:** Mirror src/ structure in tests/

**Naming:** `test_<function>_<behavior>`

**Coverage:** Aim for >80%

## Commit Format

```
<type>: <description>

feat: Add selective component uninstall
fix: Handle missing frontmatter gracefully
docs: Update README with new commands
```

## Critical Rules

1. **Never hardcode paths** - Use `Path.home()` and `os.path.expanduser()`
2. **Always type hint** - Functions must have type signatures
3. **Use specific exceptions** - No bare `except:` blocks
4. **Format before commit** - Run `black src/ && ruff check src/`
5. **Test before PR** - Ensure `pytest` passes
6. **Use --dry-run** - Preview changes in new features
7. **Follow semver** - Don't break backward compatibility

## Key Patterns

**Config access:**
```python
config = Config()
target = config.target_dir
model_for_high = config.get_model_for_tier("high")
```

**Component structure:**

Agents (primary or subagent):
```
opencode/agents/my-agent.md
opencode/agents/subagents/my-subagent.md
```

Skills:
```
opencode/skills/skill-name/SKILL.md
```

Skills require this frontmatter:
```yaml
---
name: skill-name
description: When to trigger and what this skill covers
---
```

**Adding to bundles:**
Edit `bundles/basic.yaml`, `intermediate.yaml`, or `advanced.yaml`

## Key Files

- `cli.py` - Command registration
- `config.py` - Config management
- `utils/manifest.py` - Frontmatter parsing
- `utils/version.py` - Semantic versioning
- `utils/installed_db.py` - Installation tracking
- `utils/copy.py` - File copy with template processing
- `utils/template.py` - Model tier resolution
- `commands/install.py` - Core install logic
- `commands/models.py` - Model tier configuration
