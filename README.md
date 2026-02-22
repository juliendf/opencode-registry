# OpenCode Registry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A central hub for 55 OpenCode components: primary agents, specialized subagents, skills, and commands with intelligent installation management.

[Features](#-what-is-opencode-registry) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](CONTRIBUTING.md)

---

## 🎯 What is OpenCode Registry?

OpenCode Registry provides a **curated, beautiful library** of OpenCode components that makes it **dead easy** to discover, install, and manage them. It features:

- 📚 **Central Component Library** - All OpenCode agents, skills, and commands in one place
- 🛠️ **Smart Installer** - Intelligent CLI that handles installation complexity
- 🔗 **Symlink Management** - Uses GNU Stow or fallback symlinks for clean installations
- 📦 **Bundle Support** - Install groups of components (basic, intermediate, advanced)
- 🤖 **AI-Assisted Creation** - (Coming soon) Create new components with AI help
- 🌐 **Web Gallery** - (Coming soon) Browse components with a beautiful interface

## 🚀 Quick Start

### Installation

#### For Regular Users

1. **Clone the registry:**
   ```bash
   git clone https://github.com/juliendf/opencode-registry.git
   cd opencode-registry
   ```

2. **Install the CLI:**
   ```bash
   # Navigate to installer directory (where setup files live)
   cd installer
   pip install -e .
   ```

3. **Install components:**
   ```bash
   # Return to repository root
   cd ..
   
   # Install a bundle
   opencode-config install --group basic
   
   # Or install specific components
   opencode-config install plan-design
   ```

#### For Developers

If you plan to contribute or modify the codebase:

```bash
# Clone and navigate
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry

# Navigate to installer directory and install with dev dependencies
cd installer
pip install -e ".[dev]"  # Includes pytest, black, ruff, mypy

# Return to root and start developing
cd ..
```

**Note:** The CLI auto-detects the registry location when run from the repository directory. This works seamlessly with git worktrees.

### Basic Usage

```bash
# List all available components
opencode-config list

# Show component details
opencode-config info plan-design

# Install specific component (via bundle)
opencode-config install --group intermediate

# Install a bundle
opencode-config install --group intermediate

# Check what's installed
opencode-config status

# Sync database with actual installed components
opencode-config sync

# Preview before installing
opencode-config install --group basic --dry-run

# Uninstall everything
opencode-config uninstall --all
```

## 📦 Available Components (55 Total)

### Primary Agents (7)
Core AI assistants for different development roles:
- `ask-me-anything` - General Q&A for codebase, docs, concepts, and best practices
- `build-code` - Full-stack coding agent (frontend, backend, data)
- `build-infrastructure` - Infrastructure, DevOps, and cloud platforms
- `debug` - Debugging agent that investigates issues and fixes them
- `plan-design` - Product and feature planning, functional specs, user stories
- `plan-architecture` - Technical architecture and system design
- `review` - Code quality and security review

### Subagents (43)
Specialized experts organized by domain:
- **01-core** (5) - Backend, API, microservices, GraphQL, fullstack
- **02-languages** (7) - Python, TypeScript, Go, React, Bash, SQL, Vue
- **03-infrastructure** (13) - Kubernetes, Terraform, AWS, GCP, Azure, GitOps, Cloud
- **04-quality-and-security** (5) - Testing, security, performance, debugging
- **05-data-ai** (5) - ML, data engineering, AI, database optimization
- **06-developer-experience** (3) - CLI development, MCP, DX optimization
- **07-specialized-domains** (3) - Mobile, payments, technical writing
- **09-meta-orchestration** (2) - Workflow orchestration, context management

### Skills (3)
Multi-step workflows and processes:
- `content-research-writer` - Research and write content with citations
- `mcp-builder` - Build high-quality MCP servers
- `project-docs` - Generate comprehensive project documentation

### Commands (2)
Custom slash commands for common tasks:
- `commit` - Git commit helper
- `documentation` - Documentation review and updates

## 🎨 Bundles

Pre-configured groups for different use cases:

- **basic** - Essential agents and skills (4 components)
- **intermediate** - Extended collection (10+ components)  
- **advanced** - Complete ecosystem (all 55 components)

Install with: `opencode-config install --group <bundle-name>`

**Note:** Currently, components can only be installed via bundles. Individual component installation is planned for a future release.

## 🛠️ How It Works

OpenCode Registry uses **GNU Stow** (with symlink fallback) to manage component installation:

1. Components live in the `opencode/` directory
2. The CLI creates symlinks in `~/.config/opencode/`
3. Changes in the registry automatically reflect in your config
4. Installation state is tracked in `~/.opencode-registry/installed.json`

### Installation Methods

- **Stow** (preferred): Uses GNU Stow for elegant symlink management
- **Symlink** (fallback): Manual symlink creation if stow is not available

## 📋 Requirements

### Core Requirement

- **OpenCode** 1.2.5 or later
  - [Download OpenCode](https://opencode.ai)
  - [Try OpenCode Zen (Cloud)](https://zen.opencode.ai)
  - [Installation Guide](https://opencode.ai/docs/)
  - Check your version: `opencode --version`

### System Requirements

- **Python:** 3.8 or higher
- **Git:** For cloning and managing the registry

### Dependencies

The CLI automatically installs these when you run `pip install -e .`:
- **click** ≥8.1.0 - CLI framework
- **pyyaml** ≥6.0 - YAML parsing
- **rich** ≥13.0.0 - Terminal output
- **requests** ≥2.31.0 - HTTP client

### Optional

- **GNU Stow** - For elegant symlink management (recommended but not required)
  - macOS: `brew install stow`
  - Ubuntu/Debian: `sudo apt-get install stow`
  - Without it: CLI automatically falls back to manual symlinks

## 🔧 Configuration

```bash
# View current configuration
opencode-config config --list

# Set custom target directory
opencode-config config --target /custom/path

# Set registry path (optional - auto-detects by default)
opencode-config config --registry /path/to/registry

# Enable auto-detection (default)
opencode-config config --registry auto
```

Configuration is stored in `~/.opencode-registry/config.json`

**Registry Path Auto-Detection:** By default, the CLI automatically detects the registry location when you run commands from within the repository directory. This is especially useful when working with git worktrees.

## 📊 Installation Tracking

All installations are tracked in `~/.opencode-registry/installed.json`:

- What components are installed
- When they were installed
- How they were installed (stow vs symlink)
- Installation logs and history

The database automatically syncs when you install components. If you manually modify symlinks or need to rebuild the tracking database, use:

```bash
opencode-config sync
```

This will scan your `~/.config/opencode/` directory and detect all installed registry components.

## 🔄 Version Management

OpenCode Registry uses **individual component versioning** with semantic versioning (semver) for granular update control.

### Checking for Updates

```bash
# Check all components for updates (safe preview)
opencode-config update --all --dry-run

# Check specific component
opencode-config update build-code --dry-run
```

### Updating Components

```bash
# Update all components
opencode-config update --all

# Update specific component
opencode-config update build-code

# View installed versions
opencode-config list --installed
```

### Version Format

All components follow semantic versioning: `MAJOR.MINOR.PATCH`

- **PATCH** (1.0.X) - Bug fixes, safe to update
- **MINOR** (1.X.0) - New features, backward compatible
- **MAJOR** (X.0.0) - Breaking changes, review before updating

**Learn more:** [Versioning Guide](docs/VERSIONING.md) - Complete guide to component versioning

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding New Components

1. Add your component to the appropriate directory:
   - Agents: `opencode/agents/`
   - Subagents: `opencode/agents/subagents/<category>/`
   - Skills: `opencode/skills/<skill-name>/`
   - Commands: `opencode/commands/`

2. Include YAML frontmatter with metadata

3. Submit a pull request

## 📚 Documentation

- **[Getting Started](docs/GETTING-STARTED.md)** - Step-by-step beginner guide
- **[Quick Reference](docs/QUICKREF.md)** - One-page command cheat sheet
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Versioning Guide](docs/VERSIONING.md)** - Component version management
- **[Architecture](docs/ARCHITECTURE.md)** - System design and diagrams
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Changelog](CHANGELOG.md)** - Version history
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Testing Guide](installer/tests/README.md)** - Running and writing tests

## 🗺️ Roadmap

### ✅ Completed
- [x] Core CLI installer with GNU Stow integration
- [x] Bundle support (basic, intermediate, advanced)
- [x] Component listing and info commands
- [x] Installation tracking database
- [x] Individual component versioning (semantic versioning)
- [x] Update command with dry-run support
- [x] Selective component installation and uninstall
- [x] Database sync command
- [x] Dry-run mode for all operations
- [x] Status command with detailed component view

### 🚧 In Progress / Coming Soon
- [ ] Validation command for component integrity
- [ ] AI-assisted component creation
- [ ] Web gallery for browsing components
- [ ] Component search and filtering
- [ ] Voting/rating system
- [ ] Automated testing and CI/CD

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

### Third-Party Components

Some components in this repository are based on third-party work:

- **MCP Builder Skill** - Based on [Anthropic's MCP Builder](https://github.com/anthropics/skills/tree/main/skills/mcp-builder), licensed under Apache License 2.0. See [opencode/skills/mcp-builder/LICENSE.txt](opencode/skills/mcp-builder/LICENSE.txt) for the full license.
- **Content Research Writer Skill** - Based on [ComposioHQ's content-research-writer](https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer), licensed under Apache License 2.0. See [opencode/skills/content-research-writer/LICENSE.txt](opencode/skills/content-research-writer/LICENSE.txt) for the full license.

## 🙏 Acknowledgments

Built for the OpenCode community to make agent management effortless.

Special thanks to:
- **Anthropic** for the MCP Builder skill foundation
- **ComposioHQ** for the Content Research Writer skill
- All [contributors](https://github.com/juliendf/opencode-registry/graphs/contributors)

## ⭐ Show Your Support

If you find this project helpful, please consider:
- ⭐ **Starring this repository**
- 🐛 **Reporting bugs** or suggesting features
- 🔀 **Contributing** new components or improvements
- 📢 **Sharing** with others who might benefit

---

**Made with ❤️ for the OpenCode community**
# opencode-registry
