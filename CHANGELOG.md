# Changelog

All notable changes to OpenCode Registry will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-23

### Model Tier System & Copy-Based Installation

This release replaces the GNU Stow/symlink installation model with a direct file copy approach, enabling per-component model customization.

### Added

#### Model Tier Configuration
- **`opencode-config models`** — new command to manage model tier configuration
  - `--list` — show current tier-to-model mappings in a rich table
  - `--set TIER MODEL` — set model for a specific tier (high/medium/low)
  - `--wizard` — interactive wizard to configure all tiers at once
  - `--reset` — reset tiers to defaults with confirmation prompt
  
- **Three-tier model system** in `~/.config/opencode/opencode-registry-config.json`:
  - `high` → complex reasoning (architecture, design) — default: `github-copilot/claude-sonnet-4.5`
  - `medium` → general coding (implementation, review) — default: `github-copilot/claude-sonnet-4`
  - `low` → simple tasks (docs, commits) — default: `github-copilot/claude-haiku-4.5`

- **`model_tier:` frontmatter field** added to all 55 components — during install, resolved to `model:` in the copied file

- **`--model/-m` flag** on `opencode-config install` — override tier resolution with an explicit model for all installed files

- **Model Tiers table** in `opencode-config status` output

#### Copy-Based Installation (`utils/copy.py`)
- `CopyManager` replaces `StowManager` — files are copied (not symlinked) to target directory
- Template processing during copy: `model_tier: high` → `model: <resolved-model>`
- `install_package()`, `uninstall_package()`, `detect_installed_components()` all use copy semantics
- `--dry-run` support throughout
- `model_override` parameter for explicit per-install model override

#### Template Engine (`utils/template.py`)
- `TemplateEngine` class for `{{tier:X}}` and `{{model:X}}` pattern substitution
- `resolve_model()` — tier name or literal model string → final model value
- `extract_tier_from_frontmatter()` / `extract_model_from_frontmatter()`
- `should_process_file()` — only `.md` files are processed; others copied as-is

### Changed

- **Installation method**: always `"copy"` — `--method` flag removed, `install_method` default updated
- **`opencode-config status`**: removed broken symlink check; added Model Tiers table
- **`opencode-config update`**: re-applies current tier config on each update (key advantage over symlinks)
- **`ComponentManifest`**: added `model_tier: Optional[str]` and `model: Optional[str]` fields
- **`Config`**: added `model_tiers` to `DEFAULT_CONFIG`, plus `get_model_for_tier()`, `set_model_tier()`, `list_model_tiers()` methods

### Removed

- **`utils/stow.py`** — deleted; `CopyManager` is the sole installation mechanism
- GNU Stow dependency — no longer required

### Fixed

- **`model_override` with tier-only frontmatter** — override now correctly replaces `model_tier:` line when no `model:` line exists

### Tests

- Added `tests/test_copy.py` — 26 unit tests for `CopyManager`
- Added `tests/test_integration_models.py` — 17 integration tests covering config → template → copy pipeline and CLI commands
- Extended `tests/test_manifest.py` — 6 new tests for `model_tier` / `model` field parsing
- Full suite: **143 tests, all passing**

---

## [0.1.0] - 2026-02-17

### 🎉 Initial Release

First working version of OpenCode Registry with complete installation and tracking system.

### Added

#### Core Infrastructure
- **Complete component library** with 57 components migrated from opencode-agent-workflow
  - 8 primary agents (plan-*, build-*)
  - 43 specialized subagents across 8 categories
  - 3 skills (project-docs, mcp-builder, content-research-writer)
  - 2 commands (commit, documentation)
  
#### CLI Commands
- `opencode-config list` - List all available components with rich table output
  - Filter by type: `--type agent|subagent|skill|command`
  - Supports searching and sorting
  
- `opencode-config info <component-id>` - Show detailed component information
  - Displays metadata from YAML frontmatter
  - Shows installation instructions
  
- `opencode-config install` - Install components or bundles
  - `--group <bundle>` - Install predefined bundles (basic, intermediate, advanced)
  - `--dry-run` - Preview installation without making changes
  - `--target <path>` - Custom installation directory
  - Automatic component detection and database sync after installation
  
- `opencode-config status` - Show installation status
  - `--details` - Show detailed view with installation method
  - Displays all installed components with metadata
  - Shows installed bundles
  - Verifies symlink integrity
  
- `opencode-config sync` - Sync database with actual installed components
  - Scans symlinks in target directory
  - Detects all registry components
  - Rebuilds installation database
  - `--dry-run` - Preview sync without updating database
  
- `opencode-config uninstall` - Uninstall components
  - `--all` - Remove all registry components
  - `--group <bundle>` - Uninstall bundle (currently removes all components)
  - `--dry-run` - Preview uninstallation
  - Confirmation prompt for safety
  
- `opencode-config config` - Manage configuration
  - `--list` - Show current configuration
  - `--target <path>` - Set installation target directory
  - `--registry <path>` - Set registry path
  
- `opencode-config update` - Update components to latest versions
  - `--all` - Update all installed components
  - `--dry-run` - Preview updates without making changes
  - Shows version comparison table

#### Installation System
- **GNU Stow integration** for elegant symlink management
  - Automatically detects if stow is available
  - Falls back to manual symlink creation
  - Proper `.stowrc` configuration for clean operation
  
- **Merge-friendly installation** - Registry components install alongside existing user files
  - User's custom agents/skills remain untouched
  - Registry components added via symlinks
  - No conflicts or overwrites
  
- **Installation tracking database** (`~/.opencode-registry/installed.json`)
  - Tracks individual components (agents, subagents, skills, commands)
  - Records installation timestamp
  - Logs installation method (stow vs symlink)
  - Maintains installation history
  - Tracks bundle memberships

#### Component Detection
- **Automatic component detection** from symlinks
  - Detects primary agents from `agent/*.md` symlinks
  - Detects subagents from `agent/subagents/**/*.md`
  - Detects skills from `skill/*/` directory symlinks
  - Detects commands from `command/*.md` files
  - Accurately counts and categorizes all components

#### Bundle System
- **Three predefined bundles:**
  - `basic.yaml` - 4 essential components for getting started
  - `intermediate.yaml` - 10+ components for common workflows
  - `advanced.yaml` - All 57 components for complete installation
  
- **YAML-based bundle definitions** with metadata
  - Name and description
  - Component lists
  - Easy to extend

#### Configuration Management
- **User configuration** stored in `~/.opencode-registry/config.json`
  - Registry path auto-detection
  - Custom target directory support
  - Persistent settings

#### Developer Experience
- **Rich CLI output** with color and formatting
  - Beautiful tables for component listings
  - Progress spinners for operations
  - Color-coded status messages
  - Detailed error messages
  
- **Dry-run mode** for all destructive operations
  - Preview installations before committing
  - See what would be changed
  - Safe experimentation

### Fixed
- **Stow configuration issue** - Simplified `.stowrc` to allow proper symlink creation
- **Component tracking** - Database now accurately reflects installed components
- **Merge conflicts** - Installation works alongside existing user configuration

### Documentation
- Comprehensive README.md with quickstart guide
- Detailed STATUS.md tracking project progress
- INSTALLATION_FIXED.md documenting stow troubleshooting
- Inline help for all CLI commands
- Code documentation and comments

### Technical Details
- **Language:** Python 3.8+
- **CLI Framework:** Click 8.0+
- **Output:** Rich library for formatted output
- **Configuration:** JSON for settings, YAML for bundles
- **Installation:** GNU Stow (preferred) with symlink fallback
- **Frontmatter:** YAML frontmatter parsing from markdown files

## [Unreleased]

### Planned Features
- Component validation command (check frontmatter, structure, integrity)
- AI-assisted component creation wizard
- Web gallery for browsing components
- Component search and advanced filtering
- Dependency tracking and resolution
- Community features (ratings, voting, reviews)
- CI/CD integration and automated testing
- Plugin system for extensibility

---

[0.1.0]: https://github.com/yourusername/opencode-registry/releases/tag/v0.1.0
