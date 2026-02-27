# OpenCode Registry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> Centralized library of 56 OpenCode components: agents, subagents, skills, and commands with intelligent installation management.

[Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](CONTRIBUTING.md)

---

## What is OpenCode Registry?

A curated collection of OpenCode components with a smart CLI installer:

- **56 ready-to-use components** - Agents, subagents, skills, and commands
- **Smart CLI** - Installation, updates, and tracking
- **Model tier system** - Configure models per complexity (high/medium/low/free)
- **Bundle support** - Install groups (basic/intermediate/advanced)

---

## Quick Start

```bash
# 1. Clone and install CLI
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry/installer && pip install -e .

# 2. Install components
cd .. && opencode-config install --group basic

# 3. Use with OpenCode
# Press Tab in OpenCode to switch agents, @mention for subagents
```

**Expected output after install:**
```
✓ Bundle installed: basic (4 components)
```

---

## Requirements

- **OpenCode** 1.2.5+ - [Download](https://opencode.ai) or [OpenCode Zen](https://zen.opencode.ai)
- **Python** 3.8+
- **Git**

---

## Essential Commands

| Command | Description |
|---------|-------------|
| `opencode-config list` | Browse available components |
| `opencode-config info <id>` | Show component details |
| `opencode-config install --group <bundle>` | Install a bundle |
| `opencode-config status` | Check what's installed |
| `opencode-config update --all` | Update all components |
| `opencode-config models --wizard` | Configure model tiers |
| `opencode-config sync` | Rebuild database |

**Tip:** Use `--dry-run` to preview changes before applying.

---

## Components (56 Total)

| Type | Count | Examples |
|------|-------|----------|
| **Primary Agents** | 7 | build-code, plan-design, debug, review |
| **Subagents** | 43 | python-pro, kubernetes-expert, security-auditor |
| **Skills** | 3 | mcp-builder, project-docs, content-research-writer |
| **Commands** | 3 | /commit, /documentation, /kb |

---

## Bundles

| Bundle | Components | Best For |
|--------|-----------|----------|
| `basic` | 4 | Getting started |
| `intermediate` | 10+ | Common workflows |
| `advanced` | 56 | Complete ecosystem |

---

## How It Works

1. **Components** live in `opencode/` with `model_tier:` placeholders
2. **Installation** copies files to `~/.config/opencode/` and resolves model tiers
3. **Tracking** stores state in `~/.config/opencode/opencode-registry-installed.json`
4. **Updates** re-apply your model tier config to new versions

---

## Model Tiers

```bash
# Interactive wizard (recommended)
opencode-config models --wizard

# Or set manually
opencode-config models --set high "github-copilot/claude-sonnet-4.5"
opencode-config models --set medium "github-copilot/claude-sonnet-4"
opencode-config models --set low "github-copilot/claude-haiku-4.5"
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/GETTING-STARTED.md) | Step-by-step tutorial |
| [Agent Guide](docs/AGENT-GUIDE.md) | Choose the right agent |
| [Permissions](docs/PERMISSIONS.md) | Configure agent autonomy and tools |
| [Quick Reference](docs/QUICKREF.md) | CLI command cheat sheet |
| [FAQ](docs/FAQ.md) | Common questions + troubleshooting |
| [Versioning](docs/VERSIONING.md) | Component version management |

---

## Configuration

```bash
# View config
opencode-config config --list

# Custom target directory
opencode-config config --target /path/to/directory

# Auto-detect registry (works with git worktrees)
opencode-config config --registry auto
```

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

Add components to:
- Agents: `opencode/agents/`
- Subagents: `opencode/agents/subagents/<category>/`
- Skills: `opencode/skills/<name>/`
- Commands: `opencode/commands/`

Include YAML frontmatter with metadata.

---

## License

MIT License. See [LICENSE](LICENSE).

Third-party components:
- MCP Builder Skill - [Apache 2.0](opencode/skills/mcp-builder/LICENSE.txt)
- Content Research Writer - [Apache 2.0](opencode/skills/content-research-writer/LICENSE.txt)

---

Special thanks to:
- **Anthropic** for the MCP Builder skill foundation
- **ComposioHQ** for the Content Research Writer skill
- All [contributors](https://github.com/juliendf/opencode-registry/graphs/contributors)

---

**Built for the OpenCode community**
