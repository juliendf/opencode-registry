# OpenCode Registry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> A curated collection of OpenCode agents, subagents, skills, and commands with smart installation management.

[Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](CONTRIBUTING.md)

---

## What is OpenCode Registry?

A curated collection of OpenCode components with a smart CLI installer:

- **5 primary agents** - Plan, build, debug, review, and general knowledge
- **10 specialist subagents** - Infrastructure, data, ML, security, mobile, and more
- **40+ skills** - Language expertise, architecture patterns, domain workflows
- **3 commands** - Commit, documentation, and knowledge base helpers
- **Smart CLI** - Installation, updates, and tracking
- **Model tier system** - Optional model configuration per complexity (high/medium/low/free)
- **Bundle support** - Install groups (basic/intermediate/advanced)

---

## Prerequisites

`opencode-registry` requires a working OpenCode setup:

- **OpenCode V2 is installed** — [V2 CLI guide](https://opencode.ai/v2/docs/cli)
- **At least one usable model backend is configured**
- **Python 3.8+ is installed**
- **Git is installed**

---

## Quick Start

```bash
# 1. Clone and install CLI
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry/installer && pip install -e .

# 2. Return to registry root and install components
cd .. && opencode-config install --group basic

# 3. Use with OpenCode
# Press Tab to select a primary agent. Agents load knowledge with V2 `skill` calls
# and delegate independent work with V2 `subagent` calls.
```

**Expected output after install:**
```
✓ Bundle installed: basic (4 components)
```

---

## Requirements

- **OpenCode V2** - [Install](https://opencode.ai/v2/docs/cli)
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
| `opencode-config update --all` | Update all components using configured tiers |
| `opencode-config update --all --inherit-model` | Re-copy on detected changes with session-model inheritance |
| `opencode-config models --wizard` | Configure model tiers (optional) |
| `opencode-config sync` | Rebuild database |

**Tip:** Use `--dry-run` to preview changes before applying.

---

## Components

| Type | Count | Examples |
|------|-------|----------|
| **Primary Agents** | 5 | plan, build, debug, review, ask-me-anything |
| **Subagents** | 10 | infrastructure-engineer, data-engineer, ai-engineer, security-auditor |
| **Skills** | 40+ | python-pro, kubernetes-patterns, mcp-builder, debugging-guide |
| **Commands** | 3 | /commit, /documentation, /kb |

## Organization Philosophy

**Primary Agents (5):** Override built-in opencode agents. Handle broad categories (planning, coding, debugging, review, general knowledge).

**Subagents (10):** Invoke with V2 `subagent` tool and path-derived IDs such as `subagents/infrastructure-engineer`. Use for autonomous execution, not knowledge lookup.

**Skills (40+):** Knowledge and workflow injection. Load into current context with V2 `skill` tool and exact skill ID, such as `python-pro`.

---

## Bundles

| Bundle | Components | Best For |
|--------|-----------|----------|
| `basic` | 4 | Getting started |
| `intermediate` | 16 | Common workflows |
| `advanced` | 58 | Complete ecosystem |

---

## How It Works

1. **Components** live in `opencode/`; source tier metadata stays in registry files
2. **Installation** copies files to `~/.config/opencode/`; default mode resolves configured tiers and otherwise inherits
3. **Tracking** stores state in `~/.config/opencode/opencode-registry-installed.json`
4. **Updates** re-apply configured tiers by default; `--inherit-model` removes agent/command model selectors for that invocation

---

## Model Tiers (Optional)

Model tiers are optional. Without configuration, installed components inherit the calling agent's model.

```bash
# Interactive wizard (recommended)
opencode-config models --wizard

# Or set manually
opencode-config models --set high "github-copilot/claude-sonnet-4.5"
opencode-config models --set medium "github-copilot/claude-sonnet-4"
opencode-config models --set low "github-copilot/claude-haiku-4.5"

# Explicitly remove model selectors, even when tiers are configured
opencode-config install --group advanced --inherit-model
# On update, this applies to the full registry copy when any change is detected
opencode-config update --all --inherit-model
```

`--inherit-model` applies only to that command. Install recopies the catalog; update runs only when a missing component, changed source fingerprint, or semantic-version update is detected. When update runs, it recopies the full registry package: custom files outside registry source remain untouched, but local edits to registry-managed files are overwritten. The flag removes top-level `model`, `model_tier`, and `variant` from each copied agent/command; skill files and prompt bodies remain unchanged. To force a full conversion without a pending update, run install with `--inherit-model`. Without the flag, tier-based behavior remains the default.

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/GETTING-STARTED.md) | Step-by-step tutorial |
| [Agent Guide](docs/AGENT-GUIDE.md) | Choose the right agent |
| [Permissions](docs/PERMISSIONS.md) | Configure agent autonomy and tools |
| [Quick Reference](docs/QUICKREF.md) | CLI command cheat sheet |
| [FAQ](docs/FAQ.md) | Common questions and troubleshooting |
| [Versioning](docs/VERSIONING.md) | Component version management |

---

## Configuration

```bash
# View config
opencode-config config --list

# Custom target directory
opencode-config config --target /path/to/directory

# Auto-detect the registry (works with Git worktrees)
opencode-config config --registry auto
```

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

Add components to:
- Agents: `opencode/agents/`
- Subagents: `opencode/agents/subagents/`
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
