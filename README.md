# OpenCode Registry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> Centralized library of 72 OpenCode components: agents, subagents, skills, commands, MCP servers, and tools with intelligent installation management.

[Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](CONTRIBUTING.md)

---

## What is OpenCode Registry?

A curated collection of OpenCode components with a smart CLI installer:

- **72 ready-to-use components** - Agents, subagents, skills, commands, MCP servers, and tools
- **Smart CLI** - Installation, updates, and tracking
- **Model tier system** - Configure models per complexity (high/medium/low/free)
- **Bundle support** - Install groups (basic/intermediate/advanced)

---

## Prerequisites

`opencode-registry` requires a working OpenCode setup:

- **OpenCode is installed**
- **At least one usable model backend is configured**
- **Python 3.8+ is installed**
- **Git is installed**

---

## Quick Start

```bash
# 1. Clone and install CLI
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry/installer && pip install -e .

# 2. Install components
cd .. && opencode-config install --group basic

# 3. Use with OpenCode
# Press Tab in OpenCode to switch agents; use @mention for subagents.
```

**Expected output after install:**

```text
✓ Bundle installed: basic (5 components)
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

## Components (72 Total)

| Type | Count | Examples |
|------|-------|----------|
| **Primary Agents** | 7 | build-code, plan-design, debug, review |
| **Subagents** | 46 | python-pro, kubernetes-expert, security-auditor |
| **Skills** | 12 | mcp-builder, project-docs, kubernetes-ops, argocd-ops, kb-search, registry-sync |
| **Commands** | 3 | /commit, /documentation, /kb |
| **MCP Servers** | 3 | ragclaw, context7, brave-search |
| **Tools** | 1 | github |

---

## Bundles

| Bundle | Components | Best For |
|--------|-----------|----------|
| `basic` | 5 | Getting started |
| `intermediate` | 16+ | Common workflows |
| `advanced` | 72 | Complete ecosystem |

---

## How It Works

1. **Components** live in `opencode/`; model-aware components can use `model_tier:` placeholders
2. **Installation** copies files to `~/.config/opencode/` and resolves model tiers where supported
3. **Tracking** stores state in `~/.config/opencode/opencode-registry-installed.json`
4. **Updates** re-apply your model tier config to new versions

---

## MCP Server

The registry includes a built-in [MCP](https://modelcontextprotocol.io/) server that exposes all components via the Model Context Protocol. AI agents and editors can discover, read, create, and delete components programmatically.

**Features:**

- **20 tools** — per-type CRUD (`list_agents`, `get_agent`, `create_agent`, `delete_agent`, etc.) across all 5 component types
- **5 resource templates** — `opencode://agents/{slug}`, `opencode://subagents/{slug}`, etc.
- **Stdio + HTTP transports** — works locally or as a network service
- **File watcher** — detects changes to `opencode/` and logs updates in real time
- **Scaffold generation** — `create_*` tools generate valid frontmatter + content when body is omitted

**Quick start:**

```bash
cd mcp-server && bun install

# stdio transport (for editor integration)
bun run src/cli.ts serve stdio

# HTTP transport (for network/multi-session use)
bun run src/cli.ts serve http --port 3000
```

**Editor configuration (OpenCode):**

```json
{
  "mcp": {
    "opencode-registry": {
      "command": "bun",
      "args": ["run", "/path/to/opencode-registry/mcp-server/src/cli.ts", "serve", "stdio"]
    }
  }
}
```

Built with Bun, TypeScript, and [`@modelcontextprotocol/sdk`](https://github.com/modelcontextprotocol/typescript-sdk). See [`mcp-server/`](mcp-server/) for full source.

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
- Subagents: `opencode/agents/subagents/<category>/`
- Skills: `opencode/skills/<name>/`
- Commands: `opencode/commands/`
- MCP Servers: `opencode/mcp-servers/`

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
