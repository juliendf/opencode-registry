# Frequently Asked Questions (FAQ)

## General Questions

### What is OpenCode Registry?

OpenCode Registry is a curated collection of AI agents, specialized subagents, skills (workflows), and custom commands designed to enhance AI-powered development workflows. It provides a CLI tool to easily install and manage these components in your development environment.

### Who is this for?

- **Developers** who want to enhance their AI coding assistants with specialized capabilities
- **Teams** looking to standardize AI workflows across their organization
- **AI enthusiasts** who want pre-built, production-ready agent configurations

### What's the difference between agents, subagents, skills, and commands?

- **Agents** (8 total): Primary AI personas for different development roles (e.g., `build-general`, `build-backend`, `plan-code-review`)
- **Subagents** (43 total): Specialized experts for specific technologies (e.g., `kubernetes-expert`, `react-specialist`, `python-pro`)
- **Skills** (3 total): Complex multi-step workflows and processes (e.g., `mcp-builder`, `project-docs`, `content-research-writer`)
- **Commands** (2 total): Custom slash commands for common tasks (e.g., `/commit`, `/documentation`)

### How much does it cost?

OpenCode Registry is **completely free and open-source** under the MIT License. No subscriptions, no fees, no limits.

## Installation & Setup

### What are the system requirements?

- **Python 3.8+** (for the CLI tool)
- **Git** (to clone the repository)
- **GNU Stow** (optional, for symlink management - falls back to manual symlinks if not available)
- Any operating system: macOS, Linux, or Windows (WSL)

### How do I install OpenCode Registry?

**For regular users:**

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/opencode-registry.git
cd opencode-registry

# 2. Install the CLI tool (must be done from installer/ directory)
cd installer
pip install -e .

# 3. Return to repository root and install components
cd ..
opencode-config install --group basic
```

**For developers (with testing/linting tools):**

```bash
# Same as above, but use:
pip install -e ".[dev]"
```

**Note:** The CLI automatically detects the registry location when you run it from the repository directory.

See [Getting Started Guide](GETTING-STARTED.md) for detailed instructions.

### Where are components installed?

By default, components are symlinked to `~/.config/opencode/`:

```
~/.config/opencode/
├── agents/          # Primary agents
│   └── subagents/   # Specialized subagents
├── skills/          # Workflow skills
└── commands/        # Custom commands
```

You can verify this with: `opencode-config status`

### Can I change the installation directory?

Yes! Use the `--target` flag:

```bash
opencode-config install --group basic --target /path/to/custom/directory
```

Or set it permanently in your config:

```bash
opencode-config config --target /path/to/custom/directory
```

You can also configure the registry path (though auto-detection is usually sufficient):

```bash
# View current configuration
opencode-config config --list

# Enable auto-detection (default)
opencode-config config --registry auto

# Or set manually if needed
opencode-config config --registry /path/to/registry
```

## Usage Questions

### What's the difference between bundles?

- **basic** (4 components): Essential agents for getting started
  - `build-general`, `plan-brainstorm`, `plan-code-review`, `plan-debug`
  
- **intermediate** (includes basic + 10+ more): Common specialized subagents
  - Adds: `python-pro`, `typescript-pro`, `react-specialist`, `backend-architect`, etc.
  
- **advanced** (all 57 components): Complete library including all agents, subagents, skills, and commands

### How do I see what components are available?

```bash
# List all components
opencode-config list

# Filter by type
opencode-config list --type agent
opencode-config list --type subagent
opencode-config list --type skill
opencode-config list --type command

# Get detailed info about a specific component
opencode-config info kubernetes-expert
```

### How do I install individual components?

```bash
# Install a specific agent
opencode-config install build-backend

# Install multiple components
opencode-config install python-pro react-specialist kubernetes-expert

# Preview before installing (dry-run)
opencode-config install --group intermediate --dry-run
```

### How do I update components?

```bash
# Check for updates
opencode-config status

# Update all components to latest versions
opencode-config update --all

# Update specific component
opencode-config update python-pro

# Preview updates without applying
opencode-config update --all --dry-run
```

### How do I uninstall components?

```bash
# Uninstall specific component
opencode-config uninstall build-backend

# Uninstall all components
opencode-config uninstall --all

# Uninstall entire bundle
opencode-config uninstall --group basic
```

### Can I customize installed components?

**Not directly!** Components are symlinked to the registry, so changes to installed files would affect the original registry.

**Best practice:**
1. Create custom components in `~/.config/opencode/` (outside symlinked directories)
2. Fork the repository and modify components there
3. Contribute improvements back via pull requests!

## Troubleshooting

### Command `opencode-config` not found

**Cause:** The CLI tool isn't installed or not in your PATH.

**Solution:**
```bash
# Reinstall the CLI
cd opencode-registry/installer
pip install -e .

# Verify installation
which opencode-config
opencode-config --version
```

### "Component not found" error

**Cause:** The component ID doesn't match available components.

**Solution:**
```bash
# List all available components to find the correct ID
opencode-config list

# Check specific component details
opencode-config info <component-id>
```

### Symlinks are broken after moving the registry

**Cause:** Symlinks point to absolute paths. Moving the registry breaks them.

**Solution:**
```bash
# Uninstall and reinstall from new location
opencode-config uninstall --all
opencode-config install --group basic
```

### Database shows installed but files are missing

**Cause:** Manual file deletion or filesystem changes.

**Solution:**
```bash
# Sync database with actual filesystem state
opencode-config sync

# Or reinstall
opencode-config uninstall --all
opencode-config install --group basic
```

For more troubleshooting help, see [Troubleshooting Guide](TROUBLESHOOTING.md).

## Advanced Questions

### Can I use this with multiple AI tools?

Yes! The component files are just markdown with YAML frontmatter. They can be used with any AI coding assistant that supports custom configurations (Claude, Cursor, Windsurf, etc.).

### How do versions work?

Components use semantic versioning (e.g., `1.0.0`, `1.2.3`). The CLI tracks:
- **Available version**: Latest version in the registry
- **Installed version**: Version you have installed

Use `opencode-config update` to upgrade to newer versions.

See [Versioning Guide](VERSIONING.md) for details.

### How do I contribute new components?

We love contributions! Here's the quick process:

1. Fork the repository
2. Create your component in the appropriate directory:
   - Agents: `opencode/agents/`
   - Subagents: `opencode/agents/subagents/<category>/`
   - Skills: `opencode/skills/<skill-name>/`
   - Commands: `opencode/commands/`
3. Add YAML frontmatter with metadata
4. Test it locally with `opencode-config install your-component`
5. Submit a pull request

See [Contributing Guide](../CONTRIBUTING.md) for detailed instructions.

### Can I create private/proprietary components?

Absolutely! You have several options:

1. **Fork the registry** and maintain your private components there
2. **Create a separate directory** outside `~/.config/opencode/` and manually link components
3. **Extend bundles** with your own `custom-bundle.yaml` file

The MIT license allows commercial and private use.

### How do I report bugs or request features?

- **Bugs**: [GitHub Issues](https://github.com/YOUR_USERNAME/opencode-registry/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/YOUR_USERNAME/opencode-registry/issues) with `enhancement` label
- **Questions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/opencode-registry/discussions)

### Does this work offline?

**Partially:**
- Once cloned and installed, the registry works fully offline
- Updating requires internet to pull latest changes from GitHub
- Some components (like MCP builder skill) may reference external resources

### Does the CLI work with git worktrees?

**Yes!** The CLI has built-in support for git worktrees through automatic registry path detection:

```bash
# Enable auto-detection (default)
opencode-config config --registry auto

# Now it works from any worktree
git worktree add ../my-feature feature-branch
cd ../my-feature
opencode-config list  # Works automatically!
```

When auto-detection is enabled, the CLI finds the registry location based on your current directory, so you can freely switch between worktrees without updating configuration.

### What's the project roadmap?

See [CHANGELOG.md](../CHANGELOG.md) for planned features. Upcoming highlights:
- Dependency management between components
- Component testing framework
- Web UI for browsing components
- Auto-update notifications
- Component templates generator

## Best Practices

### What bundle should I start with?

- **New users**: Start with `basic` bundle (4 essential agents)
- **Experienced developers**: Try `intermediate` (adds 10+ specialized subagents)
- **Power users**: Install `advanced` (all 57 components)

You can always add more components later!

### How often should I update?

We recommend:
- **Weekly**: Run `opencode-config update --all --dry-run` to check for updates
- **Before major projects**: Update to get latest improvements
- **After issues**: Update if you encounter bugs (they may be fixed)

### Should I commit installed components to git?

**No!** The components in `~/.config/opencode/` are symlinks. Instead:
- Commit your bundles configuration if you customize it
- Document which components your team should install
- Share the installation commands in your project's README

### How do I share my setup with my team?

```bash
# 1. Everyone clones the same registry
git clone https://github.com/YOUR_USERNAME/opencode-registry.git

# 2. Everyone installs the same bundle
opencode-config install --group intermediate

# 3. Optional: Create a custom bundle for your team
# Edit bundles/team-bundle.yaml with your specific components
opencode-config install --group team-bundle
```

---

## Still have questions?

- 📖 **Documentation**: Check our [complete documentation](../README.md)
- 🚀 **Getting Started**: See [Getting Started Guide](GETTING-STARTED.md)
- 🔧 **Troubleshooting**: See [Troubleshooting Guide](TROUBLESHOOTING.md)
- 💬 **Community**: Join [GitHub Discussions](https://github.com/YOUR_USERNAME/opencode-registry/discussions)
- 🐛 **Issues**: Report on [GitHub Issues](https://github.com/YOUR_USERNAME/opencode-registry/issues)

**Quick Links:**
- [Architecture Overview](ARCHITECTURE.md)
- [Versioning Guide](VERSIONING.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Command Reference](QUICKREF.md)
