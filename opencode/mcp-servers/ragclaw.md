---
name: "RagClaw"
description: "Go-to knowledge base for AI coding agents. Index project docs, code, and web pages into searchable local KBs with hybrid vector + keyword retrieval. Fully offline, no API keys."
type: "mcp-server"
version: "0.8.1"
transport:
  - "stdio"
command: "ragclaw-mcp"
args: []
env:
  - name: RAGCLAW_DATA_DIR
    description: "Override data directory for knowledge bases (default: ~/.local/share/ragclaw/)"
    required: false
  - name: RAGCLAW_EMBEDDER
    description: "Embedder preset alias or HuggingFace model (nomic | bge | mxbai | minilm)"
    required: false
  - name: RAGCLAW_ALLOWED_PATHS
    description: "Restrict indexing to these paths (comma-separated)"
    required: false
  - name: RAGCLAW_CONFIG_DIR
    description: "Override config directory (default: ~/.config/ragclaw/)"
    required: false
  - name: RAGCLAW_PLUGINS_DIR
    description: "Override plugins directory (default: ~/.local/share/ragclaw/plugins/)"
    required: false
---

# RagClaw MCP Server

Your go-to knowledge base for AI-assisted development. RagClaw lets agents build and query
persistent, local knowledge bases from your project documentation, source code, web pages,
and more -- then retrieve exactly what's relevant using hybrid vector + keyword search.

## Overview

Use RagClaw whenever an agent needs long-term memory across sessions: index your project's
docs, architecture decisions, API references, or entire documentation sites into named
knowledge bases, then search them naturally. Multiple KBs can coexist (e.g. per-project,
per-topic) with descriptions and keywords for automatic routing.

Everything runs locally -- no API keys, no cloud dependencies. Embeddings are generated
on-device using configurable models (default: nomic-embed-text-v1.5).

Supported sources: Markdown, PDF, DOCX, code (TypeScript, Python, Go, Java), images (OCR),
and web pages (with optional site crawling).

## Installation

```bash
# Global install
npm install -g @emdzej/ragclaw-mcp

# Or use via npx (no install)
# Set command to: npx @emdzej/ragclaw-mcp
```

## Tools Provided

| Tool | Description |
|---|---|
| `rag_search` | Search knowledge base with vector, keyword, or hybrid mode |
| `rag_add` | Index a file, directory, or URL (pass `crawl: true` to follow links) |
| `rag_reindex` | Re-process changed sources (use `force: true` to reindex all) |
| `rag_merge` | Merge another .db file into a local knowledge base |
| `rag_status` | Get KB statistics including embedder info |
| `rag_list` | List indexed sources with description/keywords header |
| `rag_remove` | Remove a source from the index |
| `rag_list_databases` | List all KBs with name, description, and keywords |
| `rag_db_init` | Create a new KB (supports description and keywords params) |
| `rag_db_info` | Set or update description and keywords on a KB |
| `rag_db_info_get` | Read description and keywords from a KB |

## Embedder Presets

| Alias | Model | Language | Context | RAM |
|---|---|---|---|---|
| `nomic` (default) | nomic-ai/nomic-embed-text-v1.5 | English | 8192 tok | ~600 MB |
| `bge` | BAAI/bge-m3 | 100+ languages | 8192 tok | ~2.3 GB |
| `mxbai` | mixedbread-ai/mxbai-embed-large-v1 | English | 512 tok | ~1.4 GB |
| `minilm` | sentence-transformers/all-MiniLM-L6-v2 | English | 256 tok | ~90 MB |

## Editor Configuration Examples

### OpenCode

```json
{
  "mcp": {
    "ragclaw": {
      "command": "ragclaw-mcp"
    }
  }
}
```

### Claude Code

```json
{
  "mcpServers": {
    "ragclaw": {
      "command": "ragclaw-mcp"
    }
  }
}
```

## Links

- Repository: <https://github.com/emdzej/ragclaw>
- npm: <https://www.npmjs.com/package/@emdzej/ragclaw-mcp>
- License: MIT
